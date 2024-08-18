from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from blog.storage import Cafe24OBS


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    cover_image = models.ImageField(
        blank=True, null=True, storage=Cafe24OBS, upload_to="category-images/"
    )
    subcategory_of = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    class MPTTMeta:
        order_insertion_by = ["name"]
        parent_attr = "subcategory_of"

    def delete(self, *args, **kwargs):
        self.cover_image.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
