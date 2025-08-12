from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserType, UserSelloingInfo


class UserSelloingInfoInline(admin.StackedInline):
    model = UserSelloingInfo
    extra = 0
    max_num = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "username",
        "email",
        "nickname",
        "is_onboarding",
        "user_type_display",
        "date_joined",
        "last_login",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "is_onboarding",
        "user_type",
        "date_joined",
    ]
    search_fields = ["username", "email", "nickname", "user_type__seloing_type"]
    ordering = ["-date_joined"]
    readonly_fields = ("last_login", "date_joined")
    list_select_related = ["user_type"]  # FK 미리 조인해서 쿼리 수 줄이기
    inlines = [UserSelloingInfoInline]

    # BaseUserAdmin.fieldsets를 직접 덮어써서 first_name/last_name 제거
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "email",
                    "nickname",
                    "profile_image",
                    "user_type",
                    "is_onboarding",
                    "isConsentPersonalInfo",
                    "isConsentMarketing",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # 생성 폼도 우리 모델 필드에 맞춰 정의
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "nickname",
                    "profile_image",
                    "user_type",
                    "isConsentPersonalInfo",
                    "isConsentMarketing",
                ),
            },
        ),
    )

    @admin.display(description="User Type")
    def user_type_display(self, obj):
        # UserType.__str__가 없으니 안전하게 FK 필드를 직접 출력
        return obj.user_type.seloing_type if obj.user_type else "-"


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "seloing_type", "description", "created_at"]
    search_fields = ["seloing_type", "description"]
    ordering = ["id"]
