import math

import graphene

from blog.core.errors import InvalidValueError, NotFoundError, PermissionDeniedError
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
        tag=graphene.List(graphene.String),
        page_size=graphene.Int(),
        offset=graphene.Int(),
        target_post=graphene.ID(),
        order_by=graphene.String(),
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
        # Filtering
        queryset = PostFilter(
            data=kwargs, queryset=Post.objects.all(), user=info.context.user
        ).qs

        queryset = list(queryset)

        # Highlighting
        title_keywords = set(
            map(
                lambda keyword: keyword.lower(),
                kwargs.get("title", kwargs.get("title_and_content", "")).split(),
            )
        )
        content_keywords = set(
            map(
                lambda keyword: keyword.lower(),
                kwargs.get("content", kwargs.get("title_and_content", "")).split(),
            )
        )
        for post in queryset:
            post.title_highlights = PostFilter.find_matching_intervals(
                post.title.lower(), title_keywords
            )
            post.content_highlights = PostFilter.find_matching_intervals(
                post.text_content.lower(), content_keywords
            )

        # ordering
        order_by = kwargs.get("order_by", "recent")
        VALID_CONDITIONS = ["recent", "relavant"]
        if order_by not in VALID_CONDITIONS:
            raise InvalidValueError(
                f"Invalid sort condition '{order_by}'. must be one of: {VALID_CONDITIONS}"
            )

        if order_by == "relavant":
            tag = kwargs.get("tag", list)
            if len(tag):
                queryset.sort(
                    key=PostFilter.matched_tags(tag),
                    reverse=True,
                )
            elif len(title_keywords) or len(content_keywords):
                queryset.sort(
                    key=PostFilter.longest_matched_text,
                    reverse=True,
                )

        # Pagination
        page_size = kwargs.pop("page_size", queryset.__len__() or 1)
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
        queryset = queryset[offset : offset + page_size]

        return PaginatedPostType(
            posts=queryset,
            page_info=PageInfoType(pages=pages, current_page=current_page),
        )
