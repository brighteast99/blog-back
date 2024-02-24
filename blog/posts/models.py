from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    subcategory_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                       related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['id']

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    category = models.ForeignKey(
        Category, related_name='posts', on_delete=models.CASCADE
    )
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'[{self.category.name}] {self.title}'
