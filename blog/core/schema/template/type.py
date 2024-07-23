import graphene
from graphene_django import DjangoObjectType

from blog.core.models import Template


class TemplateType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = Template
        fields = "__all__"

    @staticmethod
    def resolve_id(self, info):
        return self.id
