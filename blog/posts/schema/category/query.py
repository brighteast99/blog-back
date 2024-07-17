import json
import graphene
from django.db.models import Q
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from blog.posts.models import Category, Post
from . import CategoryType


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType)
    category_list = graphene.JSONString()
    valid_supercategories = graphene.List(
        CategoryType, id=graphene.Int(required=True))
    category_info = graphene.Field(CategoryType, id=graphene.Int())

    @staticmethod
    def resolve_categories(root, info):
        categories = Category.objects.filter(is_deleted=False)
        if not info.context.user.is_authenticated:
            return categories.exclude(is_hidden=True)

        return categories

    @staticmethod
    def resolve_category_list(root, info):
        authenticated = info.context.user.is_authenticated
        root_categories = Category.objects.root_nodes().filter(is_deleted=False)
        all_posts = Post.objects.exclude(
            Q(is_deleted=True) | Q(category__is_deleted=True))

        if not authenticated:
            root_categories = root_categories.exclude(is_hidden=True)
            all_posts = all_posts.exclude(
                Q(category__is_hidden=True) | Q(is_hidden=True))

        def category_to_dict(instance):
            subcategories = instance.subcategories.filter(is_deleted=False)

            if not authenticated:
                subcategories = subcategories.exclude(is_hidden=True)

            result = {
                'id': instance.id,
                'isHidden': instance.is_hidden,
                'name': instance.name,
                'level': instance.level,
                'postCount': all_posts.filter(category__in=instance.get_descendants(include_self=True)).count(),
                'subcategories': [category_to_dict(subcategory)
                                  for subcategory in subcategories]
            }
            return result

        categories_list = [{
            'name': '전체 게시글',
            'level': 0,
            'postCount': all_posts.count(),
            'subcategories': []
        }]
        categories_list.extend([category_to_dict(category)
                               for category in root_categories])
        categories_list.append({
            'id': 0,
            'name': '분류 미지정',
            'level': 0,
            'postCount': all_posts.filter(category__isnull=True).count(),
            'subcategories': []
        })
        return json.dumps(categories_list)

    @login_required
    @staticmethod
    def resolve_valid_supercategories(root, info, **args):
        id = args.get('id')
        result = Category.objects.filter(id=id).first()

        return Category.objects.exclude(Q(id__in=result.get_descendants(include_self=True)) | Q(is_deleted=True))

    @staticmethod
    def resolve_category_info(root, info, **args):
        id = args.get('id')

        if id is None:
            return Category()

        if id == 0:
            return Category(id=0)

        result = Category.objects.filter(id=id).first()

        if not info.context.user.is_authenticated and result.is_hidden:
            raise GraphQLError(
                'You do not have permission to perform this action')

        return result
