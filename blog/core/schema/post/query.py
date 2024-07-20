import graphene
from graphene_django.filter import DjangoFilterConnectionField
from blog.core.errors import NotFoundError, PermissionDeniedError
from blog.utils.convertid import localid

from blog.core.models import Post
from . import PostType


class Query(graphene.ObjectType):
    post = graphene.Field(PostType, id=graphene.ID(required=True))
    posts = DjangoFilterConnectionField(PostType)

    @staticmethod
    def resolve_post(root, info, **kwargs):
        id = localid(kwargs.get('id'))

        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise NotFoundError('게시글을 찾을 수 없습니다.')

        if not info.context.user.is_authenticated and \
                (post.is_hidden or (post.category is not None and post.category.is_hidden)):
            raise PermissionDeniedError('접근할 수 없는 게시글입니다')
        return post
