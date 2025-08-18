from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import UserStats, GlobalStats
from .serializers import (
    RankingSerializer, UserRankingDetailSerializer, 
    UserStatsSerializer, GlobalStatsSerializer, UserRewardsSerializer
)
from users.models import User


class RankingListView(APIView):
    """랭킹 조회"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 평균 점수 기준으로 랭킹 조회 (상위 100명)
        user_stats = UserStats.objects.select_related('user').filter(
            total_seloing_count__gt=0  # 셀로잉을 한 번 이상 한 유저만
        ).order_by('-total_seloing_score_avg', '-total_seloing_count')[:100]
        
        ranking_data = []
        for idx, stats in enumerate(user_stats, 1):
            ranking_data.append({
                'rank': idx,
                'user': {
                    'id': stats.user.id,
                    'nickname': stats.user.nickname,
                    'profile_image': stats.user.profile_image,
                    'stats': {
                        'id': stats.id,
                        'total_exp': stats.total_exp,
                        'total_candy': stats.total_candy,
                        'total_record_time': stats.total_record_time,
                        'total_attendance_count': stats.total_attendance_count,
                        'total_seloing_count': stats.total_seloing_count,
                        'total_seloing_score': stats.total_seloing_score,
                        'total_seloing_score_avg': stats.total_seloing_score_avg,
                        'total_repeat_score': stats.total_repeat_score,
                        'total_stable_score': stats.total_stable_score,
                        'total_topic_score': stats.total_topic_score,
                        'total_filler_score': stats.total_filler_score,
                        'total_repeat_count': stats.total_repeat_count,
                        'total_filler_count': stats.total_filler_count,
                        'created_at': stats.created_at,
                        'updated_at': stats.updated_at
                    }
                },
                'score': float(stats.total_seloing_score_avg)
            })
        
        serializer = RankingSerializer(ranking_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRankingDetailView(APIView):
    """랭킹 유저 조회"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        try:
            user_stats = UserStats.objects.get(user=user)
        except UserStats.DoesNotExist:
            return Response({
                'error': '해당 유저의 통계가 존재하지 않습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 해당 유저의 랭킹 계산
        if user_stats.total_seloing_count == 0:
            user_rank = None
            total_users = UserStats.objects.filter(total_seloing_count__gt=0).count()
        else:
            # 자신보다 평균 점수가 높은 유저 수 + 1
            better_users = UserStats.objects.filter(
                total_seloing_count__gt=0,
                total_seloing_score_avg__gt=user_stats.total_seloing_score_avg
            ).count()
            
            # 같은 평균 점수일 때 총 셀로잉 개수가 많은 유저 수
            same_avg_better_count = UserStats.objects.filter(
                total_seloing_score_avg=user_stats.total_seloing_score_avg,
                total_seloing_count__gt=user_stats.total_seloing_count
            ).count()
            
            user_rank = better_users + same_avg_better_count + 1
            total_users = UserStats.objects.filter(total_seloing_count__gt=0).count()
        
        # 글로벌 스탯 가져오기
        global_stats, created = GlobalStats.objects.get_or_create(id=1)
        
        response_data = {
            'user_rank': user_rank,
            'total_users': total_users,
            'user_stats': UserStatsSerializer(user_stats).data,
            'global_stats': GlobalStatsSerializer(global_stats).data
        }
        
        serializer = UserRankingDetailSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRewardsView(APIView):
    """유저 보상 정보 (exp, candy) 조회"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id=None):
        # user_id가 있으면 해당 유저, 없으면 현재 로그인한 유저
        if user_id:
            # 본인 정보만 조회 가능 (또는 관리자)
            if user_id != request.user.id and not request.user.is_staff:
                return Response(
                    {"error": "본인의 정보만 조회할 수 있습니다."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        
        user_stats = UserStats.objects.filter(user=user).first()
        if not user_stats:
            return Response({
                'error': '해당 유저의 통계가 존재하지 않습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserRewardsSerializer(user_stats)
        return Response(serializer.data, status=status.HTTP_200_OK)