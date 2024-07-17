import graphene
from django.db.models import Q
from graphql import GraphQLError

from blog.core.models import Category, Post
from . import PostType


class Query(graphene.ObjectType):
    post_list = graphene.List(PostType, category_id=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_post_list(root, info, **args):
        authenticated = info.context.user.is_authenticated
        category_id = args.get('category_id')

        posts = Post.objects.exclude(
            Q(is_deleted=True) | Q(category__is_deleted=True))

        if not authenticated:
            posts = posts.exclude(Q(is_hidden=True) |
                                  Q(category__is_hidden=True))

        if category_id is None:
            pass
        elif category_id == 0:
            posts = posts.filter(category__isnull=True)
        else:
            try:
                category = Category.objects.get(id=category_id)
                if not authenticated and category.is_hidden:
                    raise GraphQLError(
                        'You do not have permission to perform this action')
            except Category.DoesNotExist:
                return []

            subcategories = category.get_descendants(include_self=True)
            posts = posts.filter(category__in=subcategories)

        return posts

    @staticmethod
    def resolve_post(root, info, **args):
        try:
            post = Post.objects.get(id=args.get('id'))
        except Post.DoesNotExist:
            return None

        if not info.context.user.is_authenticated and \
                (post.is_hidden or (post.category is not None and post.category.is_hidden)):
            raise GraphQLError(
                'You do not have permission to perform this action')

        return post
