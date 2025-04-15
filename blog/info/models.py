from django.db import models

from blog.storage import OBS, OverwriteOBS


class Info(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        blank=True, null=True, storage=OBS, upload_to="staticfiles/"
    )
    favicon = models.ImageField(
        blank=True, null=True, storage=OverwriteOBS, upload_to="staticfiles/"
    )
