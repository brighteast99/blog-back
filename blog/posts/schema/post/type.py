import graphene
from graphene_django import DjangoObjectType

from blog.posts.models import Category, Post
from blog.posts.schema.category.type import CategoryType


class PostType(DjangoObjectType):
    category = graphene.Field(CategoryType)

    class Meta:
        model = Post
        fields = '__all__'

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)
