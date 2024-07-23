from django.db import models

from blog.storage import Cafe24OBS


class Info(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        blank=True, null=True, storage=Cafe24OBS, upload_to="profile-image/"
    )
