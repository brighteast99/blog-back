import graphene

from blog.core.errors import NotFoundError
from blog.core.models import Hashtag
from blog.utils.decorators import login_required

from . import HashtagType
from .filter import HashtagFilter


class Query(graphene.ObjectType):
    hashtag = graphene.Field(HashtagType, name=graphene.String(required=True))
    hashtags = graphene.List(
        HashtagType, keyword=graphene.String(), limit=graphene.Int()
    )

    @staticmethod
    @login_required
    def resolve_hashtag(self, info, **kwargs):
        try:
            hashtag = Hashtag.objects.get(name=kwargs.get("name"))
        except Hashtag.DoesNotExist:
            raise NotFoundError("태그를 찾을 수 없습니다")

        return hashtag

    @staticmethod
    @login_required
    def resolve_hashtags(self, info, **kwargs):
        queryset = HashtagFilter(data=kwargs, queryset=Hashtag.objects.all()).qs

        limit = kwargs.get("limit", None)
        if limit is not None:
            queryset = queryset[:limit]

        return queryset
