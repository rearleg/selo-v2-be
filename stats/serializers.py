from rest_framework import serializers
from .models import UserStats, GlobalStats
from users.models import User


class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = [
            'id', 'total_exp', 'total_candy', 'total_record_time',
            'total_attendance_count', 'total_seloing_count', 'total_seloing_score',
            'total_seloing_score_avg', 'total_repeat_score', 'total_stable_score',
            'total_topic_score', 'total_filler_score', 'total_repeat_count',
            'total_filler_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_seloing_score_avg']


class GlobalStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalStats
        fields = [
            'id', 'global_exp', 'global_candy', 'global_record_time',
            'global_attendance_count', 'global_seloing_count', 'global_seloing_score',
            'global_seloing_score_avg', 'global_repeat_score', 'global_stable_score',
            'global_topic_score', 'global_filler_score', 'global_repeat_count',
            'global_filler_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['global_seloing_score_avg']


class RankingUserSerializer(serializers.ModelSerializer):
    """랭킹용 유저 정보"""
    stats = UserStatsSerializer(source='userstats', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_image', 'stats']


class RankingSerializer(serializers.Serializer):
    """랭킹 조회 결과"""
    rank = serializers.IntegerField()
    user = RankingUserSerializer()
    score = serializers.FloatField()
    
    
class UserRankingDetailSerializer(serializers.Serializer):
    """특정 유저의 랭킹 정보"""
    user_rank = serializers.IntegerField()
    total_users = serializers.IntegerField()
    user_stats = UserStatsSerializer()
    global_stats = GlobalStatsSerializer()