from django.contrib import admin
from blog.posts.models import Category, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subcategory_of', 'is_deleted', 'is_hidden', 'cover_image')


admin.site.register(Category, CategoryAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', '__str__', 'is_hidden', 'created_at', 'updated_at', )


admin.site.register(Post, PostAdmin)