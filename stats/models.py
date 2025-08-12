from django.db import models
from common.models import CommonModel
from datetime import timedelta


class UserStats(CommonModel):

    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    total_exp = models.IntegerField(default=0)
    total_candy = models.IntegerField(default=0)
    total_record_time = models.DurationField(default=timedelta())
    total_attendance_count = models.IntegerField(default=0)

    # 총 셀로잉 정보
    total_seloing_count = models.IntegerField(default=0)
    total_seloing_score = models.IntegerField(default=0)
    total_seloing_score_avg = models.FloatField(default=0.0)

    total_repeat_score = models.IntegerField(default=0)
    total_stable_score = models.IntegerField(default=0)
    total_topic_score = models.IntegerField(default=0)
    total_filler_score = models.IntegerField(default=0)

    total_repeat_count = models.IntegerField(default=0)
    total_filler_count = models.IntegerField(default=0)

    # 셀로잉 점수 평균 계산
    def save(self, *args, **kwargs):
        if self.total_seloing_count > 0:
            self.total_seloing_score_avg = self.total_seloing_score / self.total_seloing_count
        else:
            self.total_seloing_score_avg = 0.0
        super().save(*args, **kwargs)



class GlobalStats(CommonModel):

    global_exp = models.IntegerField(default=0)
    global_candy = models.IntegerField(default=0)
    global_record_time = models.DurationField(default=timedelta())
    global_attendance_count = models.IntegerField(default=0)

    # 총 셀로잉 정보
    global_seloing_count = models.IntegerField(default=0)
    global_seloing_score = models.IntegerField(default=0)
    global_seloing_score_avg = models.FloatField(default=0.0)

    global_repeat_score = models.IntegerField(default=0)
    global_stable_score = models.IntegerField(default=0)
    global_topic_score = models.IntegerField(default=0)
    global_filler_score = models.IntegerField(default=0)

    global_repeat_count = models.IntegerField(default=0)
    global_filler_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.global_seloing_count > 0:
            self.global_seloing_score_avg = self.global_seloing_score / self.global_seloing_count
        else:
            self.global_seloing_score_avg = 0.0
        super().save(*args, **kwargs)
