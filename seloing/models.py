from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import CommonModel


class Topic(CommonModel):
    """주제 생성 및 선택"""
    class IsSelectChoice(models.TextChoices):
        NONE = "none", "선택안함"
        FIRST = "1", "첫번째 주제"
        SECOND = "2", "두번째 주제"
        THIRD = "3", "세번째 주제"
        SKIP = "skip", "다시뽑기"
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    topic1 = models.CharField(max_length=300)
    topic2 = models.CharField(max_length=300)
    topic3 = models.CharField(max_length=300)
    is_select = models.CharField(
        max_length=10,
        choices=IsSelectChoice.choices,
        default=IsSelectChoice.NONE
    )
    
    def __str__(self):
        return f"Topic {self.pk} - User: {self.user.username}"


class Seloing(CommonModel):
    """셀로잉 학습 세션"""
    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    selected_topic = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)


class SeloingAnalysis(CommonModel):
    """AI 분석 결과 (전사 및 피드백)"""
    seloing = models.OneToOneField(Seloing, on_delete=models.CASCADE)
    original_transcript = models.TextField()
    analyzed_transcript = models.TextField()
    disfluency_feedback = models.TextField()
    topic_feedback = models.TextField()
    stability_feedback = models.TextField()


class SeloingResult(CommonModel):
    """AI 분석 기반 점수 결과"""
    seloing = models.OneToOneField(Seloing, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    repeat_score = models.IntegerField()
    topic_score = models.IntegerField()
    filler_score = models.IntegerField()
    stability_score = models.IntegerField()

    repeat_count = models.IntegerField()
    filler_count = models.IntegerField()


class SeloingAudio(CommonModel):
    """녹음된 음성 파일 정보"""
    seloing = models.OneToOneField(Seloing, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    file_url = models.URLField()
    duration_seconds = models.FloatField()


class SeloingReward(CommonModel):
    """학습 완료 시 보상"""
    seloing = models.OneToOneField(Seloing, on_delete=models.CASCADE)
    earned_exp = models.IntegerField()
    earned_candy = models.IntegerField()


@receiver(post_save, sender=Seloing)
def update_stats_and_rewards_on_completion(sender, instance, created, **kwargs):
    """셀로잉이 완료될 때 통계 업데이트 및 보상 지급"""
    # 셀로잉이 완료되고 결과가 있을 때만 처리
    if instance.is_completed and hasattr(instance, 'seloingresult'):
        # 1. 통계 업데이트 (점수, 횟수 등)
        from .utils import update_seloing_statistics
        update_seloing_statistics(instance, instance.seloingresult)
        
        # 2. 보상 지급 (경험치, 캔디) - 이미 보상이 지급되지 않은 경우만
        if not hasattr(instance, 'seloingreward'):
            from stats.models import UserStats, GlobalStats
            from django.db import transaction
            
            with transaction.atomic():
                # 점수 기반 보상 계산
                result = instance.seloingresult
                if result and result.total_score:
                    earned_exp = result.total_score * 5  # 점수 * 5
                    earned_candy = result.total_score * 10  # 점수 * 10
                else:
                    earned_exp = 25  # 기본 경험치
                    earned_candy = 50  # 기본 캔디
                
                # 보상 저장
                SeloingReward.objects.create(
                    seloing=instance,
                    earned_exp=earned_exp,
                    earned_candy=earned_candy
                )
                
                # 유저 스탯의 보상 필드 업데이트 (통계와는 별개)
                user_stats, created = UserStats.objects.get_or_create(user=instance.user)
                user_stats.total_exp += earned_exp
                user_stats.total_candy += earned_candy
                user_stats.save()
                
                # 글로벌 스탯의 보상 필드 업데이트
                global_stats, created = GlobalStats.objects.get_or_create(id=1)
                global_stats.global_exp += earned_exp
                global_stats.global_candy += earned_candy
                global_stats.save()