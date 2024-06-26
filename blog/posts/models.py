from django.contrib.postgres.fields import ArrayField
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from blog.storage import Cafe24OBS


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    cover_image = models.ImageField(blank=True, null=True, storage=Cafe24OBS, upload_to='category-image/')
    subcategory_of = TreeForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    class MPTTMeta:
        order_insertion_by = ['name']
        parent_attr = 'subcategory_of'

    def __str__(self):
        return self.name


class BasePostContent(models.Model):
    content = models.TextField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    images = ArrayField(models.URLField(), default=list)

    class Meta:
        abstract = True


class Template(BasePostContent):
    name = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class BasePost(BasePostContent):
    title = models.CharField(max_length=100, null=False, blank=False)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True)

    class Meta:
        abstract = True


class Draft(BasePost):
    category = models.ForeignKey(
        Category, related_name='drafts', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title} (임시 저장본)'


class Post(BasePost):
    category = models.ForeignKey(
        Category, related_name='posts', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title}'
