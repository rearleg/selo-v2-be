from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from users.views import SignupView, LoginView, LogoutView, KakaoLogin, JWTVerifyView


def healthz(_):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 - API 문서에 맞게 구성
    path(
        "api/v1/",
        include(
            [
                # 인증
                path("signup/", SignupView.as_view(), name="signup"),
                path("login/", LoginView.as_view(), name="login"),
                path("logout/", LogoutView.as_view(), name="logout"),
                # 소셜 로그인
                path("auth/kakao/", KakaoLogin.as_view(), name="kakao-login"),
                # JWT 토큰 검증
                path("auth/verify/", JWTVerifyView.as_view(), name="jwt-verify"),
                # 유저 관리
                path("users/", include("users.urls")),
                # 셀로잉
                path("seloing/", include("seloing.urls")),
                # 지식/팁
                path("knowledge/", include("knowledge.urls")),
                path("tips/", include("tips.urls")),
                # 랭킹
                path("ranking/", include("stats.urls")),
                # 미디어 (API 문서에는 없지만 필요시 사용)
                path("media/", include("medias.urls")),
            ]
        ),
    ),
    path("api/healthz", healthz),
]
