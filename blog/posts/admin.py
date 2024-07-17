from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from blog.posts.models import Category, Post, Template, Draft


class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'id', 'indented_title',
                    'cover', 'is_hidden', 'is_deleted', )

    def cover(self, instance):
        if instance.cover_image:
            return format_html(f'<img src="{instance.cover_image.url}" style="max-height:150px"/>')
        return format_html('<div/>')

    mptt_level_indent = 20


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title', 'created_at',
                    'updated_at', 'is_hidden', 'is_deleted', )


admin.site.register(Post, PostAdmin)


class TemplateAdmin(admin.ModelAdmin):
    def preview(self, instance):
        return format_html(f'<div style="max-height: 300px; overflow-y: auto">{instance.content}</div>')

    list_display = ('id', 'name', 'preview')


admin.site.register(Template, TemplateAdmin)


class DraftAdmin(admin.ModelAdmin):
    def preview(self, instance):
        return format_html(f'<div style="max-height: 300px; overflow-y: auto">{instance.content}</div>')

    list_display = ('id', 'category', 'title',
                    'preview', 'created_at', 'is_hidden')


admin.site.register(Draft, DraftAdmin)
