from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # 유저 관리 (GET /v1/users, GET/PATCH/DELETE /v1/users/<int:user_id>)
    path("", views.UserListView.as_view(), name="user-list"),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
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
]
