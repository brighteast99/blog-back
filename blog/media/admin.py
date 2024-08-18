from django.contrib import admin
from django.utils.html import format_html

from blog.media.models import Image


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "uploaded_at",
    )

    def image_preview(self, instance):
        return format_html(f'<img src="{instance.file.url}" style="max-height:100px"/>')

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


admin.site.register(Image, ImageAdmin)
