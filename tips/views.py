from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import Tips, Knowledge
from .serializers import TipsSerializer, KnowledgeSerializer


class TipsListView(APIView):
    """팁 조회"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        tips = Tips.objects.all().order_by('-created_at')
        serializer = TipsSerializer(tips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KnowledgeListView(APIView):
    """지식 조회"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        knowledge = Knowledge.objects.all().order_by('-created_at')
        serializer = KnowledgeSerializer(knowledge, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
