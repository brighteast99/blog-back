import graphene
from graphene_django import DjangoObjectType
from blog.core.errors import PermissionDeniedError

from blog.core.models import Category, Draft
from blog.core.schema.category.type import CategoryType


class DraftType(DjangoObjectType):
    id = graphene.Int()
    category = graphene.Field(CategoryType)
    summary = graphene.String()

    class Meta:
        model = Draft
        fields = '__all__'

    @staticmethod
    def resolve_id(self, info):
        authenticated = info.context.user.is_authenticated
        if self.is_hidden and not authenticated:
            raise PermissionDeniedError()
        return self.id

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)

    @staticmethod
    def resolve_summary(self, info):
        return f'[{self.category.name if self.category is not None else "분류 미지정"}] {self.title} ({self.created_at})'
