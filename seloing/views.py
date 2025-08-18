import uuid
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.db import transaction
from .models import Seloing, SeloingAnalysis, SeloingResult, SeloingAudio, SeloingReward, Topic
from .serializers import (
    TopicCreateSerializer,
    SeloingCreateSerializer,
    RecordingUploadSerializer,
    AnalysisProgressSerializer,
    AICallbackSerializer,
    StatSaveSerializer,
    SeloingSerializer,
    TopicSerializer,
    TopicGenerateSerializer,
    TopicUpdateSerializer,
)
from .services import generate_topics_sync
from stats.models import UserStats, GlobalStats
import requests


class TopicCreateView(APIView):
    """관심사 주제 생성"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TopicCreateSerializer(data=request.data)
        if serializer.is_valid():
            # AI나 로직을 통해 주제 생성
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SeloingCreateView(APIView):
    """셀로잉 생성"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SeloingCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            seloing = serializer.save()
            return Response(
                {
                    "message": "셀로잉이 생성되었습니다.",
                    "seloing_id": seloing.id,
                    "selected_topic": seloing.selected_topic,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RecordingUploadView(APIView):
#     """녹음 파일 분석 요청"""

#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, seloing_id):
#         seloing = get_object_or_404(Seloing, id=seloing_id, user=request.user)

#         if seloing.is_completed:
#             return Response(
#                 {"error": "이미 완료된 셀로잉입니다."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         serializer = RecordingUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             audio_file = serializer.validated_data["audio_file"]
#             duration_seconds = serializer.validated_data["duration_seconds"]

#             # 파일 저장 로직 (실제 구현에서는 S3 등 클라우드 스토리지 사용)
#             filename = f"seloing_{seloing_id}_{audio_file.name}"
#             file_url = f"https://your-storage.com/{filename}"  # 실제 URL로 교체

#             # 오디오 정보 저장
#             seloing_audio, created = SeloingAudio.objects.get_or_create(
#                 seloing=seloing,
#                 defaults={
#                     "filename": filename,
#                     "file_url": file_url,
#                     "duration_seconds": duration_seconds,
#                 },
#             )

#             # AI 분석 요청 (비동기)
#             try:
#                 ai_response = requests.post(
#                     "http://ai-server/ai/v1/selowhisper",  # 실제 AI 서버 URL로 교체
#                     json={
#                         "seloing_id": seloing.id,
#                         "audio_url": file_url,
#                         "callback_url": f"http://your-backend/v1/seloing/{seloing.id}",
#                     },
#                 )

#                 return Response(
#                     {
#                         "message": "분석 요청이 완료되었습니다.",
#                         "seloing_id": seloing.id,
#                     },
#                     status=status.HTTP_202_ACCEPTED,
#                 )

#             except Exception as e:
#                 return Response(
#                     {"error": "AI 분석 요청 중 오류가 발생했습니다."},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecordingUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, seloing_id):
        seloing = get_object_or_404(Seloing, id=seloing_id, user=request.user)

        if seloing.is_completed:
            return Response({"error": "이미 완료된 셀로잉입니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = RecordingUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_file = serializer.validated_data["audio_file"]
        duration_seconds = serializer.validated_data["duration_seconds"]

        # S3 경로(폴더/파일명) 구성
        # 예: seloing/1234/uuid_originalname.m4a
        s3_path = f"seloing/{seloing_id}/{uuid.uuid4()}_{audio_file.name}"

        # S3에 저장 (django-storages의 default_storage 사용)
        # InMemoryUploadedFile/TemporaryUploadedFile은 그대로 save에 넣어도 됨
        saved_name = default_storage.save(s3_path, audio_file)

        # 퍼블릭 URL (AWS_QUERYSTRING_AUTH=False면 깔끔한 URL 반환)
        file_url = default_storage.url(saved_name)

        # DB 저장
        seloing_audio, created = SeloingAudio.objects.get_or_create(
            seloing=seloing,
            defaults={
                "filename": audio_file.name,
                "file_url": file_url,
                "duration_seconds": duration_seconds,
            },
        )
        if not created:
            # 이미 레코드가 있으면 갱신
            seloing_audio.filename = audio_file.name
            seloing_audio.file_url = file_url
            seloing_audio.duration_seconds = duration_seconds
            seloing_audio.save(update_fields=["filename", "file_url", "duration_seconds"])

        # (선택) AI 분석 비동기 호출은 그대로 유지
        # requests.post("http://ai-server/ai/v1/selowhisper", json={...})

        return Response(
            {
                "message": "업로드 완료",
                "seloing_id": seloing.id,
                "file_url": file_url,
            },
            status=status.HTTP_202_ACCEPTED,
        )

class AnalysisProgressView(APIView):
    """분석 상태 조회"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, seloing_id):
        seloing = get_object_or_404(Seloing, id=seloing_id, user=request.user)

        # 분석 상태 결정 로직
        if seloing.is_completed:
            status_data = {
                "status": "completed",
                "progress_percentage": 100,
                "message": "분석이 완료되었습니다.",
            }
        elif hasattr(seloing, "seloingaudio"):
            status_data = {
                "status": "processing",
                "progress_percentage": 50,
                "message": "음성 분석 중입니다...",
            }
        else:
            status_data = {
                "status": "pending",
                "progress_percentage": 0,
                "message": "분석 대기중입니다.",
            }

        serializer = AnalysisProgressSerializer(status_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AICallbackView(APIView):
    """AI 결과 콜백"""

    permission_classes = [permissions.AllowAny]  # AI 서버에서 호출

    def post(self, request, seloing_id):
        seloing = get_object_or_404(Seloing, id=seloing_id)

        serializer = AICallbackSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # 분석 결과 저장
                SeloingAnalysis.objects.create(
                    seloing=seloing,
                    original_transcript=serializer.validated_data[
                        "original_transcript"
                    ],
                    analyzed_transcript=serializer.validated_data[
                        "analyzed_transcript"
                    ],
                    disfluency_feedback=serializer.validated_data[
                        "disfluency_feedback"
                    ],
                    topic_feedback=serializer.validated_data["topic_feedback"],
                    stability_feedback=serializer.validated_data["stability_feedback"],
                )

                # 점수 결과 저장
                seloing_result = SeloingResult.objects.create(
                    seloing=seloing,
                    total_score=serializer.validated_data["total_score"],
                    repeat_score=serializer.validated_data["repeat_score"],
                    topic_score=serializer.validated_data["topic_score"],
                    filler_score=serializer.validated_data["filler_score"],
                    stability_score=serializer.validated_data["stability_score"],
                    repeat_count=serializer.validated_data["repeat_count"],
                    filler_count=serializer.validated_data["filler_count"],
                )

                # 셀로잉 완료 처리 (signal에서 자동으로 통계 업데이트됨)
                seloing.is_completed = True
                seloing.save()

            return Response(
                {"message": "AI 결과가 저장되었습니다."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SeloingResultView(APIView):
    """분석 결과 조회"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, seloing_id):
        seloing = get_object_or_404(Seloing, id=seloing_id, user=request.user)

        if not seloing.is_completed:
            return Response(
                {"error": "아직 분석이 완료되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SeloingSerializer(seloing)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RewardClaimView(APIView):
    """보상 지급 (EXP, Candy)"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, seloing_id):
        seloing = get_object_or_404(Seloing, id=seloing_id, user=request.user)

        if not seloing.is_completed:
            return Response(
                {"error": "완료되지 않은 셀로잉입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 보상이 지급된 경우
        if hasattr(seloing, "seloingreward"):
            return Response(
                {"error": "이미 보상이 지급된 셀로잉입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StatSaveSerializer(data=request.data)
        if serializer.is_valid():
            earned_exp = serializer.validated_data["earned_exp"]
            earned_candy = serializer.validated_data["earned_candy"]

            with transaction.atomic():
                # 보상 저장
                SeloingReward.objects.create(
                    seloing=seloing, earned_exp=earned_exp, earned_candy=earned_candy
                )

                # 유저 스탯에 보상만 추가 (셀로잉 점수는 이미 AICallback에서 처리됨)
                user_stats, created = UserStats.objects.get_or_create(user=request.user)
                user_stats.total_exp += earned_exp
                user_stats.total_candy += earned_candy
                user_stats.save()

                # 글로벌 스탯에 보상만 추가
                global_stats, created = GlobalStats.objects.get_or_create(id=1)
                global_stats.global_exp += earned_exp
                global_stats.global_candy += earned_candy
                global_stats.save()

            return Response(
                {
                    "message": "보상이 지급되었습니다.",
                    "earned_exp": earned_exp,
                    "earned_candy": earned_candy,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicGenerateView(APIView):
    """주제 생성 API"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """주제 생성 (POST) - 바디 없이"""
        try:
            # ChatGPT API로 주제 생성 (동기 처리)
            topic1, topic2, topic3 = generate_topics_sync(request.user)
            
            # DB에 저장
            topic = Topic.objects.create(
                user=request.user,
                topic1=topic1,
                topic2=topic2,
                topic3=topic3
            )
            
            # 생성된 주제를 바로 응답으로 반환
            serializer = TopicSerializer(topic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"주제 생성 실패: {e}")
            return Response(
                {"error": "주제 생성 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """최근 주제 조회 (GET)"""
        latest_topic = Topic.objects.filter(user=request.user).order_by('-created_at').first()
        if latest_topic:
            serializer = TopicSerializer(latest_topic)
            return Response(serializer.data)
        else:
            return Response(
                {"message": "생성된 주제가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )


class TopicDetailView(APIView):
    """주제 상세 조회 및 업데이트 API"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """특정 주제 조회 (GET)"""
        topic = get_object_or_404(Topic, pk=pk, user=request.user)
        serializer = TopicSerializer(topic)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """주제 선택 업데이트 (PUT)"""
        topic = get_object_or_404(Topic, pk=pk, user=request.user)
        serializer = TopicUpdateSerializer(topic, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
