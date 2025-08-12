from django.db import models
from common.models import CommonModel



class Image(CommonModel):
    file = models.URLField()

class ProfileImage(CommonModel):
    file = models.URLField()
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)