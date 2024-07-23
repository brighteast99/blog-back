import graphene
from graphene_django.filter import DjangoFilterConnectionField

from blog.core.errors import NotFoundError, PermissionDeniedError
from blog.core.models import Post
from blog.utils.convertid import localid

from . import PostType


class Query(graphene.ObjectType):
    post = graphene.Field(
        PostType, id=graphene.ID(required=True), is_deleted=graphene.Boolean()
    )
    posts = DjangoFilterConnectionField(PostType)

    @staticmethod
    def resolve_post(root, info, **kwargs):
        id = localid(kwargs.get("id"))
        is_deleted = kwargs.get("is_deleted", False)

        authenticated = info.context.user.is_authenticated

        if is_deleted and not authenticated:
            raise PermissionDeniedError()

        try:
            post = Post.objects.get(id=id, is_deleted=is_deleted)
        except Post.DoesNotExist:
            raise NotFoundError("게시글을 찾을 수 없습니다.")

        if (
            post.is_hidden or getattr(post.category, "is_hidden", False)
        ) and not authenticated:
            raise PermissionDeniedError("접근할 수 없는 게시글입니다")
        return post
