import requests
import jwt
import json
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from .models import User, OnboardingSession, OnboardingMessage
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserOnboardingSerializer,
    OnboardingSessionSerializer,
    OnboardingChatSerializer,
)
from seloing.serializers import SeloingListSerializer
from seloing.models import Seloing


class SignupView(APIView):
    """회원가입"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # JWT 토큰 생성 (Access + Refresh)
            from .jwt_utils import generate_jwt_tokens
            tokens = generate_jwt_tokens(user)
            return Response(
                {
                    "message": "회원가입이 완료되었습니다.",
                    "user": UserSerializer(user).data,
                    "access_token": tokens['access_token'],
                    "refresh_token": tokens['refresh_token'],
                    "access_expires_in": tokens['access_expires_in'],
                    "refresh_expires_in": tokens['refresh_expires_in'],
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """로그인"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            # JWT 토큰 생성 (Access + Refresh)
            from .jwt_utils import generate_jwt_tokens
            tokens = generate_jwt_tokens(user)
            return Response(
                {
                    "message": "로그인되었습니다.",
                    "user": UserSerializer(user).data,
                    "access_token": tokens['access_token'],
                    "refresh_token": tokens['refresh_token'],
                    "access_expires_in": tokens['access_expires_in'],
                    "refresh_expires_in": tokens['refresh_expires_in'],
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """로그아웃"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Refresh Token이 있으면 무효화
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            from .jwt_utils import revoke_refresh_token
            revoke_refresh_token(refresh_token)
        
        logout(request)
        return Response({"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK)


class UserListView(APIView):
    """유저 리스트 조회 (관리자만)"""

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """유저 정보 조회/수정/삭제 (본인만)"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user_id, request_user):
        user = get_object_or_404(User, id=user_id)

        # 본인만 접근 가능
        if user != request_user:
            return None
        return user

    def get(self, request, user_id):
        """유저 정보 조회"""
        user = self.get_object(user_id, request.user)
        if user is None:
            return Response(
                {"error": "본인의 정보만 조회할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        """유저 정보 수정"""
        user = self.get_object(user_id, request.user)
        if user is None:
            return Response(
                {"error": "본인의 정보만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """유저 회원 탈퇴"""
        user = self.get_object(user_id, request.user)
        if user is None:
            return Response(
                {"error": "본인의 계정만 탈퇴할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 실제 삭제 대신 비활성화
        user.is_active = False
        user.save()

        return Response(
            {"message": "회원 탈퇴가 완료되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class UserSeloingHistoryView(APIView):
    """유저 셀로잉 이력 조회 (본인만, 완료된 것만)"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # 본인만 조회 가능
        if user != request.user:
            return Response(
                {"error": "본인의 이력만 조회할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 완료된 셀로잉만 조회
        seloing_list = Seloing.objects.filter(user=user, is_completed=True).order_by(
            "-created_at"
        )

        serializer = SeloingListSerializer(seloing_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSeloingDetailView(APIView):
    """유저 셀로잉 이력 상세 조회 (본인만)"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, seloing_id):
        user = get_object_or_404(User, id=user_id)

        # 본인만 조회 가능
        if user != request.user:
            return Response(
                {"error": "본인의 이력만 조회할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        seloing = get_object_or_404(Seloing, id=seloing_id, user=user)

        # 완료된 것만 상세 조회 가능
        if not seloing.is_completed:
            return Response(
                {"error": "완료된 셀로잉만 조회할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from seloing.serializers import SeloingSerializer

        serializer = SeloingSerializer(seloing)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserOnboardingView(APIView):
    """유저 온보딩 정보 업데이트 (본인만)"""

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, user_id):
        """온보딩 정보 업데이트 및 완료 처리"""
        user = get_object_or_404(User, id=user_id)

        # 본인만 접근 가능
        if user != request.user:
            return Response(
                {"error": "본인의 정보만 수정할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserOnboardingSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(
                {
                    "message": "온보딩이 완료되었습니다.",
                    "user": UserSerializer(updated_user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KakaoLogin(APIView):
    """카카오 소셜 로그인"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        카카오 소셜 로그인 (Web: 인가 코드, React Native: 액세스 토큰)
        Request body: {"code": "카카오_인가_코드"} 또는 {"access_token": "카카오_액세스_토큰"}
        """
        code = request.data.get('code')
        access_token = request.data.get('access_token')
        
        if not code and not access_token:
            return Response(
                {"error": "인가 코드 또는 액세스 토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 1. 액세스 토큰 획득 (인가 코드 방식 또는 직접 토큰)
            if access_token:
                # React Native: 직접 액세스 토큰 사용
                final_access_token = access_token
            else:
                # Web: 인가 코드로 액세스 토큰 받기
                kakao_token_data = self._get_kakao_token(code)
                if not kakao_token_data:
                    return Response(
                        {"error": "카카오 토큰 받기에 실패했습니다."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                final_access_token = kakao_token_data.get('access_token')
            
            # 2. 카카오 사용자 정보 받기
            kakao_user_data = self._get_kakao_user_info(final_access_token)
            if not kakao_user_data:
                return Response(
                    {"error": "카카오 사용자 정보를 가져올 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. 사용자 생성 또는 로그인
            user = self._get_or_create_user(kakao_user_data)
            
            # 4. JWT 토큰 생성 (Access + Refresh)
            from .jwt_utils import generate_jwt_tokens
            tokens = generate_jwt_tokens(user)
            
            return Response({
                "message": "카카오 로그인 성공",
                "user": UserSerializer(user).data,
                "access_token": tokens['access_token'],
                "refresh_token": tokens['refresh_token'],
                "access_expires_in": tokens['access_expires_in'],
                "refresh_expires_in": tokens['refresh_expires_in'],
                "is_new_user": user.date_joined == user.last_login
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"로그인 처리 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_kakao_token(self, code):
        """카카오 인가 코드로 액세스 토큰 받기"""
        token_url = "https://kauth.kakao.com/oauth/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_CLIENT_ID,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code,
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def _get_kakao_user_info(self, access_token):
        """카카오 액세스 토큰으로 사용자 정보 받기"""
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        response = requests.get(user_info_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def _get_or_create_user(self, kakao_data):
        """카카오 사용자 정보로 Django 사용자 생성 또는 조회"""
        kakao_id = str(kakao_data['id'])
        kakao_account = kakao_data.get('kakao_account', {})
        profile = kakao_account.get('profile', {})
        
        # 카카오 ID를 username으로 사용 (kakao_ 접두사)
        username = f"kakao_{kakao_id}"
        
        # 기존 사용자 찾기
        try:
            user = User.objects.get(username=username)
            # 로그인 시간 업데이트
            user.last_login = timezone.now()
            user.save()
            return user
        except User.DoesNotExist:
            pass
        
        # 새 사용자 생성
        email = kakao_account.get('email', f'{username}@kakao.local')
        nickname = profile.get('nickname', f'카카오사용자_{kakao_id[:8]}')
        profile_image = profile.get('profile_image_url', '')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            nickname=nickname,
            profile_image=profile_image,
            # 카카오 로그인이므로 패스워드는 사용하지 않음
            password=None
        )
        
        # 로그인 시간 설정
        user.last_login = timezone.now()
        user.set_unusable_password()
        user.save()
        
        return user

class NaverLogin(APIView):
    pass

class GoogleLogin(APIView):
    pass


class TokenRefreshView(APIView):
    """Refresh Token으로 새로운 Access Token 발급"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Refresh Token으로 새로운 토큰 쌍 발급
        Request body: {"refresh_token": "refresh_token"}
        """
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {"error": "Refresh token이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .jwt_utils import refresh_access_token
        tokens = refresh_access_token(refresh_token)
        
        if tokens:
            return Response({
                "access_token": tokens['access_token'],
                "refresh_token": tokens['refresh_token'],
                "access_expires_in": tokens['access_expires_in'],
                "refresh_expires_in": tokens['refresh_expires_in'],
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "유효하지 않거나 만료된 refresh token입니다."
            }, status=status.HTTP_401_UNAUTHORIZED)


class JWTVerifyView(APIView):
    """JWT 토큰 검증 및 사용자 정보 반환"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        JWT 토큰 검증
        Request body: {"token": "jwt_token"}
        """
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "토큰이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .jwt_utils import get_user_from_token
        user = get_user_from_token(token)
        
        if user:
            return Response({
                "valid": True,
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "valid": False,
                "error": "유효하지 않은 토큰입니다."
            }, status=status.HTTP_401_UNAUTHORIZED)


class OnboardingChatView(APIView):
    """온보딩 대화 처리"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """현재 온보딩 세션 조회"""
        session = OnboardingSession.objects.filter(
            user=request.user, 
            is_active=True
        ).first()
        
        if not session:
            # 새로운 세션 생성
            session = OnboardingSession.objects.create(user=request.user)
            # 첫 번째 AI 메시지 추가
            OnboardingMessage.objects.create(
                session=session,
                sender=OnboardingMessage.SenderChoice.AI,
                content="안녕하세요! 셀로에 오신 것을 환영합니다 🎉\n\n셀로 사용을 위해 몇 가지 질문을 드릴게요. 먼저 셀로를 사용하는 목표가 무엇인가요?\n\n예를 들어:\n- 발표 실력 향상\n- 면접 준비\n- 일상 대화 실력 향상\n- 영업 스킬 개발\n\n어떤 목표를 가지고 계신지 자유롭게 말씀해 주세요!",
                step=OnboardingSession.StepChoice.GOAL
            )
        
        serializer = OnboardingSessionSerializer(session)
        return Response(serializer.data)
    
    def post(self, request):
        """온보딩 대화 메시지 처리"""
        serializer = OnboardingChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = serializer.validated_data['message']
        
        # 현재 활성 세션 가져오기
        session = OnboardingSession.objects.filter(
            user=request.user, 
            is_active=True
        ).first()
        
        if not session:
            return Response(
                {"error": "활성 온보딩 세션이 없습니다. GET 요청으로 세션을 시작해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 사용자 메시지 저장
        OnboardingMessage.objects.create(
            session=session,
            sender=OnboardingMessage.SenderChoice.USER,
            content=user_message,
            step=session.current_step
        )
        
        # AI 응답 생성
        ai_response = self._generate_ai_response(session, user_message)
        
        # AI 메시지 저장
        OnboardingMessage.objects.create(
            session=session,
            sender=OnboardingMessage.SenderChoice.AI,
            content=ai_response['message'],
            step=session.current_step
        )
        
        # 단계 업데이트
        if ai_response['next_step']:
            session.current_step = ai_response['next_step']
            session.save()
        
        # 온보딩 완료 처리
        if session.current_step == OnboardingSession.StepChoice.COMPLETED:
            self._complete_onboarding(session)
        
        serializer = OnboardingSessionSerializer(session)
        return Response(serializer.data)
    
    def _generate_ai_response(self, session, user_message):
        """ChatGPT를 사용한 AI 응답 생성"""
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            current_step = session.current_step
            
            # 시스템 프롬프트 생성
            system_prompt = self._get_system_prompt(current_step)
            
            # 대화 히스토리 구성
            messages = [{"role": "system", "content": system_prompt}]
            
            # 이전 대화 내역 추가 (최근 6개 메시지만)
            recent_messages = session.messages.all().order_by('created_at')
            if recent_messages.count() > 6:
                recent_messages = recent_messages[recent_messages.count()-6:]
            
            for msg in recent_messages:
                role = "assistant" if msg.sender == OnboardingMessage.SenderChoice.AI else "user"
                messages.append({"role": role, "content": msg.content})
            
            # 현재 사용자 메시지 추가
            messages.append({"role": "user", "content": user_message})
            
            # ChatGPT API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_completion_tokens=300,
                temperature=0.7
            )
            
            ai_message = response.choices[0].message.content.strip()
            
            # 다음 단계 결정
            next_step = self._determine_next_step(current_step, ai_message)
            
            return {
                'message': ai_message,
                'next_step': next_step
            }
            
        except Exception as e:
            # API 오류 시 기본 응답 사용
            return self._get_fallback_response(current_step, user_message)
    
    def _get_system_prompt(self, current_step):
        """단계별 시스템 프롬프트 생성"""
        base_prompt = """
당신은 셀로(Selo)라는 음성 대화 연습 앱의 친근한 온보딩 도우미입니다.
사용자가 편안하게 느낄 수 있도록 친근하고 격려하는 톤으로 대화해주세요.
이모지를 적절히 사용하고, 한국어로 대답해주세요.
응답은 300자 이내로 간결하게 해주세요.

셀로는 음성 대화 실력 향상을 도와주는 AI 서비스입니다.
"""
        
        if current_step == OnboardingSession.StepChoice.GOAL:
            return base_prompt + """
현재 사용자의 목표를 파악하는 단계입니다.
사용자가 목표를 말하면, 그 목표에 대해 공감하고 격려한 후, 
자연스럽게 직업이나 상황에 대해 질문해주세요.

예시 목표: 발표 실력 향상, 면접 준비, 일상 대화 실력 향상, 영업 스킬 개발 등
"""
        
        elif current_step == OnboardingSession.StepChoice.JOB:
            return base_prompt + """
현재 사용자의 직업이나 상황을 파악하는 단계입니다.
사용자가 직업/상황을 말하면, 그에 대해 공감하고 
해당 분야에서 커뮤니케이션의 중요성을 언급한 후,
자연스럽게 관심사에 대해 질문해주세요.

예시 직업/상황: 학생, 직장인, 프리랜서, 창업 준비중, 주부 등
"""
        
        elif current_step == OnboardingSession.StepChoice.INTEREST:
            return base_prompt + """
현재 사용자의 관심사를 파악하는 마지막 단계입니다.
사용자가 관심사를 말하면, 그에 대해 긍정적으로 반응하고,
온보딩 완료를 알려주세요.

반드시 마지막에는 "온보딩이 완료되었습니다!"라고 명확히 말해주세요.
"""
        
        return base_prompt
    
    def _determine_next_step(self, current_step, ai_message):
        """AI 응답 내용을 보고 다음 단계 결정"""
        # "온보딩이 완료되었습니다"가 포함되어 있으면 완료
        if "온보딩이 완료" in ai_message:
            return OnboardingSession.StepChoice.COMPLETED
        
        # 단계별 자동 진행
        step_flow = {
            OnboardingSession.StepChoice.GOAL: OnboardingSession.StepChoice.JOB,
            OnboardingSession.StepChoice.JOB: OnboardingSession.StepChoice.INTEREST,
            OnboardingSession.StepChoice.INTEREST: OnboardingSession.StepChoice.COMPLETED
        }
        return step_flow.get(current_step)
    
    def _get_fallback_response(self, current_step, user_message):
        """API 오류 시 기본 응답"""
        fallback_responses = {
            OnboardingSession.StepChoice.GOAL: {
                'message': f"'{user_message}' 목표네요! 정말 좋은 목표입니다 👍\n\n셀로는 이런 목표를 달성하는데 도움이 될 거예요. 그렇다면 현재 어떤 일을 하고 계신가요?",
                'next_step': OnboardingSession.StepChoice.JOB
            },
            OnboardingSession.StepChoice.JOB: {
                'message': f"{user_message} 상황이시군요! 그 분야에 맞는 커뮤니케이션 스킬이 정말 중요하죠 💼\n\n마지막으로 평소에 관심 있는 분야나 취미가 있나요?",
                'next_step': OnboardingSession.StepChoice.INTEREST  
            },
            OnboardingSession.StepChoice.INTEREST: {
                'message': f"{user_message}에 관심이 있으시는군요! 정말 흥미로운 분야네요 ✨\n\n온보딩이 완료되었습니다! 🎉",
                'next_step': OnboardingSession.StepChoice.COMPLETED
            }
        }
        
        return fallback_responses.get(current_step, {
            'message': "죄송합니다. 다시 시도해주세요.",
            'next_step': None
        })
    
    def _get_goal_from_session(self, session):
        """세션에서 목표 추출"""
        goal_messages = session.messages.filter(
            sender=OnboardingMessage.SenderChoice.USER,
            step=OnboardingSession.StepChoice.GOAL
        )
        return goal_messages.first().content if goal_messages.exists() else ""
    
    def _get_job_from_session(self, session):
        """세션에서 직업 추출"""
        job_messages = session.messages.filter(
            sender=OnboardingMessage.SenderChoice.USER,
            step=OnboardingSession.StepChoice.JOB
        )
        return job_messages.first().content if job_messages.exists() else ""
    
    def _complete_onboarding(self, session):
        """온보딩 완료 처리"""
        user = session.user
        
        # 사용자 정보에서 응답 추출
        goal = self._get_goal_from_session(session)
        job = self._get_job_from_session(session)
        interest_messages = session.messages.filter(
            sender=OnboardingMessage.SenderChoice.USER,
            step=OnboardingSession.StepChoice.INTEREST
        )
        interest = interest_messages.first().content if interest_messages.exists() else ""
        
        # UserSelloingInfo 업데이트
        seloing_info = user.seloing_infos.first()
        if seloing_info:
            seloing_info.goal = goal
            seloing_info.job = job
            seloing_info.interest = interest
            seloing_info.save()
        
        # 온보딩 완료 표시
        user.is_onboarding = True
        user.save()
        
        # 세션 비활성화
        session.is_active = False
        session.save()