import requests
from django.urls import path
from . import views

app_name = 'seloing'

urlpatterns = [
    # 새로운 주제 생성 API
    path('topics/', views.TopicGenerateView.as_view(), name='topic-generate'),
    path('topics/<int:pk>/', views.TopicDetailView.as_view(), name='topic-detail'),
    
    # 기존 주제 생성 (deprecated, 호환성을 위해 유지)
    # path('topics/', views.TopicCreateView.as_view(), name='topic-create-old'),
    
    # POST /v1/seloing - 셀로잉 생성
    path('', views.SeloingCreateView.as_view(), name='seloing-create'),
    
    # POST /v1/seloing/<int:seloing_id>/recording - 녹음 파일 분석 요청
    path('<int:seloing_id>/recording/', views.RecordingUploadView.as_view(), name='recording-upload'),
    
    # GET /v1/seloing/<int:seloing_id>/progress - 분석 상태 조회
    path('<int:seloing_id>/progress/', views.AnalysisProgressView.as_view(), name='analysis-progress'),
    
    # POST /v1/seloing/<int:seloing_id> - AI 결과 콜백 & GET - 분석 결과 조회
    path('<int:seloing_id>/', views.SeloingResultView.as_view(), name='seloing-result'),
    
    # AI 콜백 전용 (POST만, 별도 처리)
    path('<int:seloing_id>/callback/', views.AICallbackView.as_view(), name='ai-callback'),
    
    # POST /v1/seloing/<int:seloing_id>/stat - 보상 지급
    path('<int:seloing_id>/stat/', views.RewardClaimView.as_view(), name='reward-claim'),
]