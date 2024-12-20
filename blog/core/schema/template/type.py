import graphene
from graphene_django import DjangoObjectType

from blog.core.models import Template


class TemplateType(DjangoObjectType):
    id = graphene.Int()
    thumbnail = graphene.String()
    images = graphene.List(graphene.String)
    tags = graphene.List(graphene.String)

    class Meta:
        model = Template
        fields = "__all__"

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_thumbnail(self, info):
        return self.thumbnail.file.url if self.thumbnail else None

    @staticmethod
    def resolve_images(self, info):
        return [image.file.url for image in self.images.all()]

    @staticmethod
    def resolve_tags(self, info):
        return self.tags.values_list("name", flat=True)
