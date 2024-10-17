from django.db import models

from blog.media.models import Image

from . import Category


class Hashtag(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)


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
    tags = models.ManyToManyField(Hashtag, related_name="tagged_%(class)s")

    class Meta:
        abstract = True


class Template(AbstractTemplate):
    template_name = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        ordering = ["template_name"]

    def __str__(self):
        return f"{self.template_name}"


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
    updated_at = models.DateTimeField(null=False, auto_now=True)

    class Meta:
        abstract = True


class Draft(AbstractDraft):
    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title} (임시 저장본)'


class Post(AbstractDraft):
    text_content = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title}'
