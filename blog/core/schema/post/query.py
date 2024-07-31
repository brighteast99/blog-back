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

        if title_keywords or content_keywords:

            def find_keywords(str, keywords):
                highlights = []
                for keyword in keywords:
                    cur = 0
                    while cur < len(str):
                        cur = str.find(keyword, cur)
                        if cur == -1:
                            break
                        highlights.append([cur, cur + len(keyword)])
                        cur += len(keyword)

                if len(highlights) < 2:
                    return highlights

                highlights.sort(key=lambda x: x[0])
                merged_highlights = [highlights[0]]

                for [current_start, current_end] in highlights[1:]:
                    last_start, last_end = merged_highlights[-1]
                    if current_start <= last_end:
                        merged_highlights[-1] = [last_start, max(last_end, current_end)]
                    else:
                        merged_highlights.append([current_start, current_end])

                return merged_highlights

            for post in queryset:
                post.title_highlights = find_keywords(
                    post.title.lower(), title_keywords
                )
                post.content_highlights = find_keywords(
                    post.text_content.lower(), content_keywords
                )

        return PaginatedPostType(
            posts=queryset,
            page_info=PageInfoType(pages=pages, current_page=current_page),
        )
