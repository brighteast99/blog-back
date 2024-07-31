import math

import graphene

from blog.core.errors import NotFoundError, PermissionDeniedError
from blog.core.models import Post
from blog.utils.convertid import localid

from . import PostType
from .filter import PostFilter
from .type import PageInfoType, PaginatedPostType


class Query(graphene.ObjectType):
    post = graphene.Field(
        PostType, id=graphene.ID(required=True), is_deleted=graphene.Boolean()
    )
    posts = graphene.Field(
        PaginatedPostType,
        category_id=graphene.Int(),
        title_and_content=graphene.String(),
        title=graphene.String(),
        content=graphene.String(),
        page_size=graphene.Int(),
        offset=graphene.Int(),
        target_post=graphene.ID(),
    )

    @staticmethod
    def resolve_post(self, info, **kwargs):
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

    @staticmethod
    def resolve_posts(self, info, **kwargs):
        queryset = PostFilter(
            data=kwargs, queryset=Post.objects.all(), user=info.context.user
        ).qs

        page_size = kwargs.pop("page_size", queryset.__len__())
        target_post = kwargs.pop("target_post", None)

        if target_post:
            target_post = localid(target_post)
            try:
                post = queryset.get(id=target_post)
                post_position = list(queryset).index(post)
            except ValueError:
                raise NotFoundError()
            offset = post_position // page_size * page_size
        else:
            offset = kwargs.pop("offset", 0)

        pages = math.ceil(queryset.__len__() / page_size)
        current_page = offset // page_size
        queryset = list(queryset)[offset : offset + page_size]
        return PaginatedPostType(
            posts=queryset,
            page_info=PageInfoType(pages=pages, current_page=current_page),
        )
