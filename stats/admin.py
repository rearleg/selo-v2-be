from django.contrib import admin
from .models import UserStats, GlobalStats


@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'total_exp', 'total_candy', 'total_seloing_count', 
        'total_seloing_score_avg', 'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__nickname']
    ordering = ['-total_seloing_score_avg', '-total_exp']
    readonly_fields = ['total_seloing_score_avg', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user',)
        }),
        ('경험치 & 보상', {
            'fields': ('total_exp', 'total_candy', 'total_record_time', 'total_attendance_count')
        }),
        ('셀로잉 통계', {
            'fields': (
                'total_seloing_count', 'total_seloing_score', 'total_seloing_score_avg',
                'total_repeat_score', 'total_stable_score', 'total_topic_score', 
                'total_filler_score', 'total_repeat_count', 'total_filler_count'
            )
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GlobalStats)
class GlobalStatsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'global_exp', 'global_candy', 'global_seloing_count', 
        'global_seloing_score_avg', 'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    ordering = ['-id']
    readonly_fields = ['global_seloing_score_avg', 'created_at', 'updated_at']
    
    fieldsets = (
        ('글로벌 경험치 & 보상', {
            'fields': ('global_exp', 'global_candy', 'global_record_time', 'global_attendance_count')
        }),
        ('글로벌 셀로잉 통계', {
            'fields': (
                'global_seloing_count', 'global_seloing_score', 'global_seloing_score_avg',
                'global_repeat_score', 'global_stable_score', 'global_topic_score', 
                'global_filler_score', 'global_repeat_count', 'global_filler_count'
            )
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # 글로벌 스탯은 하나만 존재해야 함
        return not GlobalStats.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # 글로벌 스탯 삭제 방지
        return False
