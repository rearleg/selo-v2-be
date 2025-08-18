from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import CommonModel


class User(AbstractUser):

    # first_name, last_name은 serializer에서 제거할 예정
    first_name = models.CharField(
        max_length=150,
        blank=True,
        editable=False,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        editable=False,
    )
    profile_image = models.URLField(blank=True)
    nickname = models.CharField(
        max_length=150,
        default="",
    )

    # 온보딩 여부
    is_onboarding = models.BooleanField(
        default=False,
    )
    user_type = models.ForeignKey(
        "users.UserType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        default=2,
    )

    # 개인정보 수집 이용 동의 여부
    isConsentPersonalInfo = models.BooleanField(
        default=False,
    )

    # 마케팅 정보 수신 동의 여부
    isConsentMarketing = models.BooleanField(
        default=False,
    )


# 유저 타입
class UserType(CommonModel):

    class SeloingTypeChoice(models.TextChoices):
        BEGGINER = "혼돈의 달변가형"
        ELEMENTARY = "성장중인 소통 초보형"
        INTERMEDIATE = "신중한 전략가형"
        ADVANCED = "소통의 장인형"
        MASTER = "마스터 커뮤니케이터"

    seloing_type = models.CharField(
        max_length=30,
        choices=SeloingTypeChoice.choices,
    )
    description = models.TextField(
        max_length=200, null=True, blank=True, default="설명이 없습니다."
    )

    def __str__(self):
        return self.seloing_type


# 유저 셀로잉 정보
class UserSelloingInfo(CommonModel):

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="seloing_infos",
    )
    #### level은 유저 타입으로 변경
    # level = models.TextField(
    #     max_length=200,
    #     null=True,
    #     blank=True,
    # )
    goal = models.TextField(
        max_length=200,
        null=True,
        blank=True,
    )
    job = models.TextField(
        max_length=200,
        null=True,
        blank=True,
    )
    interest = models.TextField(
        max_length=200,
        null=True,
        blank=True,
    )


# Refresh Token 관리
class RefreshToken(CommonModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="refresh_tokens"
    )
    token_hash = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['user', 'is_revoked']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"RefreshToken for {self.user.username}"


# 블랙리스트된 토큰
class BlacklistedToken(CommonModel):
    token_hash = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['token_hash']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"BlacklistedToken: {self.token_hash[:20]}..."


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    """유저 생성 시 UserStats와 UserSelloingInfo 자동 생성"""
    if created:
        from stats.models import UserStats

        # UserStats 생성
        UserStats.objects.create(user=instance)

        # UserSelloingInfo 생성
        UserSelloingInfo.objects.create(user=instance)