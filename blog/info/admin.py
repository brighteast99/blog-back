from django.contrib import admin
from blog.info.models import Info


class InfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'avatar')


admin.site.register(Info, InfoAdmin)
