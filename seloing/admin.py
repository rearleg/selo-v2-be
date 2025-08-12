from django.contrib import admin
from .models import Seloing, SeloingAnalysis, SeloingResult, SeloingAudio, SeloingReward


class SeloingAnalysisInline(admin.StackedInline):
    model = SeloingAnalysis
    extra = 0
    max_num = 1


class SeloingResultInline(admin.StackedInline):
    model = SeloingResult
    extra = 0
    max_num = 1


class SeloingAudioInline(admin.StackedInline):
    model = SeloingAudio
    extra = 0
    max_num = 1


class SeloingRewardInline(admin.StackedInline):
    model = SeloingReward
    extra = 0
    max_num = 1


@admin.register(Seloing)
class SeloingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'selected_topic', 'is_completed', 'created_at', 'updated_at']
    list_filter = ['is_completed', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__nickname', 'selected_topic']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [SeloingAnalysisInline, SeloingResultInline, SeloingAudioInline, SeloingRewardInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'selected_topic', 'is_completed')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SeloingAnalysis)
class SeloingAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'seloing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['seloing__user__username', 'seloing__selected_topic']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('분석 결과', {
            'fields': ('seloing', 'original_transcript', 'analyzed_transcript')
        }),
        ('피드백', {
            'fields': ('disfluency_feedback', 'topic_feedback', 'stability_feedback')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SeloingResult)
class SeloingResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'seloing', 'total_score', 'repeat_score', 'topic_score', 'filler_score', 'stability_score', 'created_at']
    list_filter = ['total_score', 'created_at']
    search_fields = ['seloing__user__username', 'seloing__selected_topic']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('점수', {
            'fields': ('seloing', 'total_score', 'repeat_score', 'topic_score', 'filler_score', 'stability_score')
        }),
        ('카운트', {
            'fields': ('repeat_count', 'filler_count')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SeloingAudio)
class SeloingAudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'seloing', 'filename', 'duration_seconds', 'created_at']
    list_filter = ['created_at']
    search_fields = ['seloing__user__username', 'filename']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SeloingReward)
class SeloingRewardAdmin(admin.ModelAdmin):
    list_display = ['id', 'seloing', 'earned_exp', 'earned_candy', 'created_at']
    list_filter = ['created_at']
    search_fields = ['seloing__user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
