from django.contrib import admin
from .models import Image, ProfileImage


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_preview', 'created_at', 'updated_at']
    search_fields = ['file']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def file_preview(self, obj):
        """파일 URL 미리보기"""
        if obj.file:
            return obj.file if len(obj.file) <= 50 else obj.file[:47] + '...'
        return '파일 없음'
    file_preview.short_description = '파일 URL'
    
    fieldsets = (
        ('이미지 정보', {
            'fields': ('file',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'file_preview', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__nickname', 'file']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def file_preview(self, obj):
        """파일 URL 미리보기"""
        if obj.file:
            return obj.file if len(obj.file) <= 50 else obj.file[:47] + '...'
        return '파일 없음'
    file_preview.short_description = '파일 URL'
    
    fieldsets = (
        ('프로필 이미지 정보', {
            'fields': ('user', 'file')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
