import json

import graphene
from django.db.models import Q

from blog.core.errors import NotFoundError, PermissionDeniedError
from blog.core.models import Category, Post
from blog.utils.decorators import login_required

from . import CategoryType


class Query(graphene.ObjectType):
    category = graphene.Field(
        CategoryType, id=graphene.Int(), is_deleted=graphene.Boolean()
    )
    categories = graphene.List(CategoryType)
    category_hierarchy = graphene.JSONString()
    valid_supercategories = graphene.List(CategoryType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_category(self, info, **kwargs):
        id = kwargs.get("id")
        is_deleted = kwargs.get("is_deleted", False)

        authenticated = info.context.user.is_authenticated

        if is_deleted and not authenticated:
            raise PermissionDeniedError()

        if id is None:
            return Category()

        if id == 0:
            return Category(id=0)

        try:
            category = Category.objects.get(id=id, is_deleted=is_deleted)
        except Category.DoesNotExist:
            raise NotFoundError("게시판을 찾을 수 없습니다")

        if category.is_hidden and not authenticated:
            raise PermissionDeniedError("접근할 수 없는 게시판입니다")

        return category

    @staticmethod
    def resolve_categories(self, info):
        categories = Category.objects.filter(is_deleted=False)
        if not info.context.user.is_authenticated:
            return categories.exclude(is_hidden=True)

        return categories

    @staticmethod
    def resolve_category_hierarchy(self, info):
        authenticated = info.context.user.is_authenticated
        root_categories = Category.objects.root_nodes().filter(is_deleted=False)
        all_posts = Post.objects.exclude(is_deleted=True)

        if not authenticated:
            root_categories = root_categories.exclude(is_hidden=True)
            all_posts = all_posts.exclude(
                Q(category__is_hidden=True) | Q(is_hidden=True)
            )

        def category_to_dict(instance):
            subcategories = instance.subcategories.filter(is_deleted=False)

            if not authenticated:
                subcategories = subcategories.exclude(is_hidden=True)

            result = {
                "id": instance.id,
                "isHidden": instance.is_hidden,
                "name": instance.name,
                "level": instance.level,
                "postCount": all_posts.filter(
                    category__in=instance.get_descendants(include_self=True)
                ).count(),
                "subcategories": [
                    category_to_dict(subcategory) for subcategory in subcategories
                ],
            }
            return result

        categories_list = [
            {
                "name": "전체 게시글",
                "level": 0,
                "postCount": all_posts.count(),
                "subcategories": [],
            }
        ]
        categories_list.extend(
            [category_to_dict(category) for category in root_categories]
        )
        categories_list.append(
            {
                "id": 0,
                "name": "분류 미지정",
                "level": 0,
                "postCount": all_posts.filter(category__isnull=True).count(),
                "subcategories": [],
            }
        )
        return json.dumps(categories_list)

    @login_required
    @staticmethod
    def resolve_valid_supercategories(self, info, **kwargs):
        id = kwargs.get("id")
        try:
            result = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise NotFoundError("게시판을 찾을 수 없습니다")

        return Category.objects.exclude(
            Q(id__in=result.get_descendants(include_self=True)) | Q(is_deleted=True)
        )
