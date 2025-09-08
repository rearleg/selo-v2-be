from django.urls import path
from . import views
from stats.views import UserRewardsView

app_name = "users"

urlpatterns = [
    # 유저 관리 (GET /v1/users, GET/PATCH/DELETE /v1/users/<int:user_id>)
    path("", views.UserListView.as_view(), name="user-list"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
    # 유저 온보딩 (PUT /v1/users/<int:user_id>/onboarding)
    path("<int:user_id>/onboarding/", views.UserOnboardingView.as_view(), name="user-onboarding"),
    # 유저 셀로잉 이력 (GET /v1/users/<int:user_id>/seloing)
    path(
        "<int:user_id>/seloing/",
        views.UserSeloingHistoryView.as_view(),
        name="user-seloing-history",
    ),
    path(
        "<int:user_id>/seloing/<int:seloing_id>/",
        views.UserSeloingDetailView.as_view(),
        name="user-seloing-detail",
    ),
    # 유저 보상 조회 (GET /v1/users/<int:user_id>/rewards)
    path(
        "<int:user_id>/rewards/",
        UserRewardsView.as_view(),
        name="user-rewards",
    ),
    # 내 보상 조회 (GET /v1/users/me/rewards)
    path(
        "me/rewards/",
        UserRewardsView.as_view(),
        name="my-rewards",
    ),
    # 소셜 로그인
    path(
        "kakao/",
        views.KakaoLogin.as_view(),
        name="kakao-login",
    ),
    path(
        "naver/",
        views.NaverLogin.as_view(),
        name="naver-login",
    ),
    path(
        "google/",
        views.GoogleLogin.as_view(),
        name="google-login",
    ),
    # 온보딩 대화
    path(
        "onboarding/chat/",
        views.OnboardingChatView.as_view(),
        name="onboarding-chat",
    ),
]
