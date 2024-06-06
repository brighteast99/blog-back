from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from blog.posts.models import Category, Post, Template


class CategoryAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'id', 'indented_title',
        'cover_image', 'is_deleted', 'is_hidden')
    mptt_level_indent = 20


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', '__str__', 'is_hidden', 'created_at', 'updated_at', )


admin.site.register(Post, PostAdmin)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'content', )


admin.site.register(Template, TemplateAdmin)