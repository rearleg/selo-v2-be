from django.db import transaction
from stats.models import UserStats, GlobalStats


def update_seloing_statistics(seloing, seloing_result):
    """셀로잉 완료 시 통계 자동 업데이트"""
    with transaction.atomic():
        # 유저 스탯 업데이트 (항상 업데이트)
        user_stats, created = UserStats.objects.get_or_create(user=seloing.user)
        
        user_stats.total_seloing_count += 1
        user_stats.total_seloing_score += seloing_result.total_score
        user_stats.total_repeat_score += seloing_result.repeat_score
        user_stats.total_stable_score += seloing_result.stability_score
        user_stats.total_topic_score += seloing_result.topic_score
        user_stats.total_filler_score += seloing_result.filler_score
        user_stats.total_repeat_count += seloing_result.repeat_count
        user_stats.total_filler_count += seloing_result.filler_count
        user_stats.save()

        # 글로벌 스탯 업데이트 (셀로잉 카운트가 3 이상일 때만)
        if user_stats.total_seloing_count >= 3:
            global_stats, created = GlobalStats.objects.get_or_create(id=1)
            global_stats.global_seloing_count += 1
            global_stats.global_seloing_score += seloing_result.total_score
            global_stats.global_repeat_score += seloing_result.repeat_score
            global_stats.global_stable_score += seloing_result.stability_score
            global_stats.global_topic_score += seloing_result.topic_score
            global_stats.global_filler_score += seloing_result.filler_score
            global_stats.global_repeat_count += seloing_result.repeat_count
            global_stats.global_filler_count += seloing_result.filler_count
            global_stats.save()