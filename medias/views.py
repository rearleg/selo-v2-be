from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import Image, ProfileImage
from .serializers import (
    ImageSerializer, ProfileImageSerializer, ImageUploadSerializer
)


class ImageListCreateView(APIView):
    """이미지 리스트 조회 및 생성"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        images = Image.objects.all().order_by('-created_at')
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileImageCreateView(APIView):
    """프로필 이미지 생성"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ProfileImageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageUploadView(APIView):
    """이미지 업로드 (일반)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            
            # 파일 저장 로직 (실제 구현에서는 S3 등 클라우드 스토리지 사용)
            filename = f"image_{request.user.id}_{image_file.name}"
            file_url = f"https://your-storage.com/{filename}"  # 실제 URL로 교체
            
            # 이미지 정보 저장
            image = Image.objects.create(file=file_url)
            
            return Response({
                'message': '이미지 업로드가 완료되었습니다.',
                'image': ImageSerializer(image).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileImageUploadView(APIView):
    """프로필 이미지 업로드"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            
            # 파일 저장 로직
            filename = f"profile_{request.user.id}_{image_file.name}"
            file_url = f"https://your-storage.com/{filename}"  # 실제 URL로 교체
            
            # 기존 프로필 이미지가 있다면 삭제하고 새로 생성
            ProfileImage.objects.filter(user=request.user).delete()
            profile_image = ProfileImage.objects.create(
                user=request.user,
                file=file_url
            )
            
            # User 모델의 profile_image도 업데이트
            request.user.profile_image = file_url
            request.user.save()
            
            return Response({
                'message': '프로필 이미지 업로드가 완료되었습니다.',
                'profile_image': ProfileImageSerializer(profile_image).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
