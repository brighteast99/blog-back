from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin

from blog.core.models import Category, Draft, Post, Template


def content_preview(content: str):
    return format_html(
        f'<div style="max-height: 300px; overflow-y: auto">{content}</div>'
    )


def format_tags(tags: str):
    spans = list(
        map(
            lambda tag: f'<span style="padding: 1px 2px; margin: 0 2px; background-color:dimgray; border: 1px solid gray; border-radius: 4px;">#{tag}</span>',
            tags.split(),
        )
    )
    return format_html("".join(spans))


class CategoryAdmin(DraggableMPTTAdmin):

    def cover(self, instance: Category):
        if instance.cover_image:
            return format_html(
                f'<img src="{instance.cover_image.url}" style="max-height:150px"/>'
            )
        return format_html("<div/>")

    list_display = (
        "tree_actions",
        "id",
        "indented_title",
        "cover",
        "is_hidden",
        "is_deleted",
    )

    mptt_level_indent = 20


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    def assigned_tags(self, instance: Post):
        return format_tags(instance.tags)

    list_display = (
        "id",
        "category",
        "title",
        "assigned_tags",
        "created_at",
        "updated_at",
        "is_hidden",
        "is_deleted",
        "deleted_at",
    )


admin.site.register(Post, PostAdmin)


class TemplateAdmin(admin.ModelAdmin):
    def preview(self, instance: Template):
        return content_preview(instance.content)

    def assigned_tags(self, instance: Template):
        return format_tags(instance.tags)

    list_display = (
        "id",
        "template_name",
        "title",
        "preview",
        "assigned_tags",
    )


admin.site.register(Template, TemplateAdmin)


class DraftAdmin(admin.ModelAdmin):
    def preview(self, instance: Draft):
        return content_preview(instance.content)

    def assigned_tags(self, instance: Draft):
        return format_tags(instance.tags)

    list_display = (
        "id",
        "category",
        "title",
        "preview",
        "assigned_tags",
        "created_at",
        "updated_at",
        "is_hidden",
    )


admin.site.register(Draft, DraftAdmin)
