import graphene
from graphene_django import DjangoObjectType

from blog.core.models import Category, Draft
from blog.core.schema.category.type import CategoryType


class DraftType(DjangoObjectType):
    id = graphene.Int()
    category = graphene.Field(CategoryType)
    summary = graphene.String()
    thumbnail = graphene.String()
    images = graphene.List(graphene.String)

    class Meta:
        model = Draft
        fields = "__all__"

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)

    @staticmethod
    def resolve_summary(self, info):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title or "제목 없음"}'

    @staticmethod
    def resolve_thumbnail(self, info):
        return self.thumbnail.file.url if self.thumbnail else None

    @staticmethod
    def resolve_images(self, info):
        return self.images.values_list("file", flat=True)
