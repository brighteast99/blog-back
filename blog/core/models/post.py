from django.contrib.postgres.fields import ArrayField
from django.db import models

from blog.media.models import Image

from . import Category


class AbstractTemplate(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    content = models.TextField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    thumbnail = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        related_name="%(class)s_thumbnail_of",
        null=True,
        default=None,
    )
    images = models.ManyToManyField(Image, related_name="%(class)s_content_of")

    class Meta:
        abstract = True


class Template(AbstractTemplate):
    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title}"


class AbstractDraft(AbstractTemplate):
    category = models.ForeignKey(
        Category,
        related_name="%(class)ss",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)

    class Meta:
        abstract = True


class Draft(AbstractDraft):
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title} (임시 저장본)'


class Post(AbstractDraft):
    text_content = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title}'
