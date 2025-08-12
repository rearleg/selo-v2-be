from rest_framework import serializers
from .models import Tips, Knowledge


class TipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tips
        fields = ['id', 'text', 'created_at', 'updated_at']


class KnowledgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ['id', 'title', 'detail', 'created_at', 'updated_at']