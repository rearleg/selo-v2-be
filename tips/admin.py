from django.contrib import admin
from .models import Tips, Knowledge


@admin.register(Tips)
class TipsAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_preview', 'created_at', 'updated_at']
    search_fields = ['text']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def text_preview(self, obj):
        """텍스트 미리보기 (처음 50자)"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '내용 미리보기'
    
    fieldsets = (
        ('팁 내용', {
            'fields': ('text',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'detail_preview', 'created_at', 'updated_at']
    search_fields = ['title', 'detail']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def detail_preview(self, obj):
        """상세 내용 미리보기 (처음 50자)"""
        return obj.detail[:50] + '...' if len(obj.detail) > 50 else obj.detail
    detail_preview.short_description = '상세 내용 미리보기'
    
    fieldsets = (
        ('지식 정보', {
            'fields': ('title', 'detail')
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
