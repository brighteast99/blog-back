import graphene
from graphene_django import DjangoObjectType

from blog.posts.models import Category, Draft
from blog.posts.schema.category.type import CategoryType


class DraftType(DjangoObjectType):
    id = graphene.Int()
    category = graphene.Field(CategoryType)
    summary = graphene.String()

    class Meta:
        model = Draft
        fields = '__all__'

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)

    @staticmethod
    def resolve_summary(self, info):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title}'