from django.contrib import admin
from django.utils.html import format_html

from blog.info.models import Info
from blog.settings import AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME


class InfoAdmin(admin.ModelAdmin):
    list_display = ("favicon_preview", "title", "description", "avatar_image")

    def favicon_preview(self, instance):
        if instance.favicon:
            return format_html(
                f'<img src="{instance.favicon.url}" style="width:24px; height:24px; object-position: center; object-fit: cover;"/>'
            )
        else:
            return format_html("<div>no favicon</div>")

    def avatar_image(self, instance):
        url = (
            instance.avatar.url
            if instance.avatar
            else f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/staticfiles/default-profile.png"
        )
        return format_html(
            f'<img src="{url}" style="width:150px; height:150px; object-position: center; object-fit: cover; border-radius:50%"/>'
        )


admin.site.register(Info, InfoAdmin)
