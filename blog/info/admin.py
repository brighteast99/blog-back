from django.contrib import admin
from django.utils.html import format_html
from blog.info.models import Info


class InfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'avatar_image')

    def avatar_image(self, instance):
        url = instance.avatar.url if instance.avatar else \
            'https://kr.cafe24obs.com/blog.brighteast/staticfiles/default-profile.png'
        return format_html(f'<img src="{url}" style="width:150px; height:150px; object-position: center; object-fit: cover; border-radius:50%"/>')


admin.site.register(Info, InfoAdmin)
