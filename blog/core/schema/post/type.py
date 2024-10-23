import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from blog.core.models import Category, Post
from blog.core.schema.category.type import CategoryType
from blog.utils.pagination import PageInfoType

from .filter import PostFilter


class PostType(DjangoObjectType):
    category = graphene.Field(CategoryType)
    thumbnail = graphene.String()
    images = graphene.List(graphene.String)
    tags = graphene.List(graphene.String)
    title_highlights = graphene.List(graphene.List(graphene.Int))
    content_highlights = graphene.List(graphene.List(graphene.Int))

    class Meta:
        model = Post
        interfaces = (Node,)
        filterset_class = PostFilter
        fields = "__all__"

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)

    @staticmethod
    def resolve_thumbnail(self, info):
        return self.thumbnail.file.url if self.thumbnail else None

    @staticmethod
    def resolve_images(self, info):
        return [image.file.url for image in self.images.all()]

    @staticmethod
    def resolve_tags(self, info):
        return self.tags.values_list("name", flat=True)


class PaginatedPostType(graphene.ObjectType):
    posts = graphene.List(PostType)
    page_info = graphene.Field(PageInfoType)
