from rest_framework import serializers
from .models import Image, ProfileImage


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'created_at', 'updated_at']


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id', 'file', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ImageUploadSerializer(serializers.Serializer):
    """이미지 업로드용"""
    image = serializers.ImageField()
    
    def validate_image(self, value):
        # 이미지 형식 검증
        if not value.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise serializers.ValidationError('지원되지 않는 이미지 형식입니다.')
        
        # 파일 크기 제한 (예: 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('이미지 크기가 너무 큽니다. (최대 10MB)')
        
        return value