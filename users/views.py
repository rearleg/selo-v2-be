import requests
import jwt
import json
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from .models import User
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserOnboardingSerializer,
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