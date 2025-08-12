from django.db import models
from common.models import CommonModel


class Tips(CommonModel):
    text = models.TextField()


class Knowledge(CommonModel):
    title = models.CharField(max_length=150)
    detail = models.TextField()
