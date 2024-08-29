from django.db import models

from blog.storage import Cafe24OBS


class Image(models.Model):
    file = models.ImageField(
        blank=False,
        null=False,
        unique=True,
        storage=Cafe24OBS,
        upload_to="media/",
        editable=False,
        width_field="width",
        height_field="height",
    )
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(null=False, auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.file.url
