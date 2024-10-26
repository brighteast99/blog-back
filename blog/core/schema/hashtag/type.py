import graphene
from graphene_django import DjangoObjectType

from blog.core.models import Hashtag
from blog.core.schema.post import PostType


class HashtagType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()
    tagged_posts = graphene.List(PostType)

    class Meta:
        model = Hashtag
        fields = "__all__"

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_name(self, info):
        return self.name

    @staticmethod
    def resolve_tagged_posts(self, info):
        return self.tagged_posts.all()
