import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType

from blog.core.errors import PermissionDeniedError
from blog.core.models import Category, Post


class CategoryType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()
    level = graphene.Int()
    post_count = graphene.Int(exclude_subcategories=graphene.Boolean(False))
    subcategories = graphene.List(lambda: CategoryType)
    ancestors = graphene.List(lambda: CategoryType)
    cover_image = graphene.String()

    class Meta:
        model = Category
        fields = "__all__"

    @staticmethod
    def resolve_name(self, info):
        if self.id is None:
            return "전체 게시글"

        if self.id == 0:
            return "분류 미지정"

        return self.name

    @staticmethod
    def resolve_level(self, info):
        if self.id is None or self.id == 0:
            return 0

        return self.level

    @staticmethod
    def resolve_description(self, info):
        if self.id is None:
            return "블로그의 모든 게시글"

        if self.id == 0:
            return "분류가 없는 게시글"

        return self.description

    @staticmethod
    def resolve_subcategories(self, info):
        if not info.context.user.is_authenticated:
            self.subcategories.exclude(is_hidden=True)
        return self.subcategories.all()

    @staticmethod
    def resolve_ancestors(self, info):
        if self.id is None or self.id == 0:
            return []
        if not info.context.user.is_authenticated and self.is_hidden:
            raise PermissionDeniedError()
        return self.get_ancestors()

    @staticmethod
    def resolve_post_count(self, info, exclude_subcategories=False):
        posts = Post.objects.exclude(is_deleted=True)

        if not info.context.user.is_authenticated:
            posts = posts.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))

        if self.id is None:
            pass
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            if exclude_subcategories:
                posts = self.posts
            else:
                posts = Post.objects.filter(
                    category__in=Category.get_descendants(self, include_self=True)
                )

        return posts.count()

    @staticmethod
    def resolve_posts(self, info):
        if self.id is None:
            posts = Post.objects.all()
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            posts = self.posts.all()

        posts = posts.exclude(is_deleted=True)
        if not info.context.user.is_authenticated:
            posts = posts.exclude(is_hidden=True)

        return posts

    @staticmethod
    def resolve_cover_image(self, info):
        return self.cover_image.url if self.cover_image else None
