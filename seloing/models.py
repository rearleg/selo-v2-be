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
def update_stats_on_seloing_completion(sender, instance, created, **kwargs):
    """셀로잉이 완료될 때 통계 자동 업데이트"""
    # 셀로잉이 완료되고 결과가 있을 때만 통계 업데이트
    if instance.is_completed and hasattr(instance, 'seloingresult'):
        from .utils import update_seloing_statistics
        update_seloing_statistics(instance, instance.seloingresult)