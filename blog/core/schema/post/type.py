import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from blog.core.models import Category, Post
from blog.core.schema.category.type import CategoryType
from .filter import PostFilter


class PostType(DjangoObjectType):
    category = graphene.Field(CategoryType)

    class Meta:
        model = Post
        filterset_class = PostFilter
        interfaces = (Node, )
        fields = '__all__'

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)
