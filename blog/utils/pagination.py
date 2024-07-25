from math import ceil

import graphene
from graphene import relay

from blog.utils.convertid import localid


class ExtendedPageInfo(relay.PageInfo):
    pages = graphene.Int()
    current_page = graphene.Int()


class ExtendedConnection(relay.Connection):
    class Meta:
        abstract = True

    page_info = graphene.Field(ExtendedPageInfo)

    @staticmethod
    def resolve_page_info(root, info):
        total_count = root.length
        page_size = info.variable_values.get("first")
        if not page_size:
            page_size = info.variable_values.get("last")
        if not page_size:
            page_size = len(root.edges)
        pages = ceil(total_count / page_size) if page_size else 1

        start_idx = int(
            localid(root.page_info.start_cursor)
            if root.page_info.start_cursor is not None
            else 0
        )
        current_page = start_idx // page_size if page_size else 0

        return ExtendedPageInfo(
            has_next_page=root.page_info.has_next_page,
            has_previous_page=root.page_info.has_previous_page,
            start_cursor=root.page_info.start_cursor,
            end_cursor=root.page_info.end_cursor,
            pages=pages,
            current_page=current_page,
        )
