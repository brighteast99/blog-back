import json
import graphene
from django.db import DatabaseError, IntegrityError
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from blog.posts.models import Category, Post


class CategoryType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()
    post_count = graphene.Int(exclude_subcategories=graphene.Boolean())
    subcategories = graphene.List(lambda: CategoryType)

    class Meta:
        model = Category
        fields = '__all__'

    @staticmethod
    def resolve_id(self, info):
        return self.id

    @staticmethod
    def resolve_name(self, info):
        if self.id is None:
            return "전체 게시글"

        if self.id == 0:
            return "분류 미지정"

        return self.name

    @staticmethod
    def resolve_description(self, info):
        if self.id is None:
            return "블로그의 모든 게시글"

        if self.id == 0:
            return "분류가 없는 게시글"

        return self.description

    @staticmethod
    def resolve_subcategories(self, info):
        if not info.context.user.is_authenticated:
            self.subcategories.exclude(is_hidden=True)
        return self.subcategories.all()

    @staticmethod
    def resolve_post_count(self, info, exclude_subcategories=False):
        if self.id is None:
            posts = Post.objects
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            if exclude_subcategories:
                posts = self.posts
            else:
                posts = Post.objects.filter(category__in=Category.get_descendants(self, include_self=True))

        if not info.context.user.is_authenticated:
            posts = posts.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))

        return posts.count()

    @staticmethod
    def resolve_posts(self, info):
        if self.id is None:
            posts = Post.objects.all()
        elif self.id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            posts = self.posts.all()

        if not info.context.user.is_authenticated:
            posts = posts.exclude(is_hidden=True)

        return posts


class PostType(DjangoObjectType):
    category = graphene.Field(CategoryType)

    class Meta:
        model = Post
        fields = '__all__'

    @staticmethod
    def resolve_category(self, info):
        return self.category if self.category is not None else Category(id=0)


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType)
    category_list = graphene.JSONString()
    category_info = graphene.Field(CategoryType, id=graphene.Int())
    post_list = graphene.List(PostType, category_id=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_categories(root, info):
        if not info.context.user.is_authenticated:
            return Category.objects.exclude(is_hidden=True)

        return Category.objects.all()

    @staticmethod
    def resolve_category_list(root, info):
        authenticated = info.context.user.is_authenticated
        root_categories = Category.objects.root_nodes()
        all_posts = Post.objects

        if not authenticated:
            root_categories = root_categories.exclude(is_hidden=True)
            all_posts = all_posts.exclude(Q(category__is_hidden=True) | Q(is_hidden=True))

        def category_to_dict(instance):
            subcategories = instance.subcategories.all()

            if not authenticated:
                subcategories = subcategories.exclude(is_hidden=True)

            result = {
                'id': instance.id,
                'isHidden': instance.is_hidden,
                'name': instance.name,
                'postCount': all_posts.filter(category__in=instance.get_descendants(include_self=True)).count(),
                'subcategories': [category_to_dict(subcategory)
                                  for subcategory in subcategories]
            }
            return result

        categories_list = [{
            'name': '전체 게시글',
            'postCount': all_posts.count(),
            'subcategories': []
        }]
        categories_list.extend([category_to_dict(category) for category in root_categories])
        categories_list.append({
            'id': 0,
            'name': '분류 미지정',
            'postCount': all_posts.filter(category__isnull=True).count(),
            'subcategories': []
        })
        return json.dumps(categories_list)

    @staticmethod
    def resolve_category_info(root, info, **args):
        id = args.get('id')

        if id is None:
            return Category()

        if id == 0:
            return Category(id=0)

        result = Category.objects.filter(id=id).first()

        if not info.context.user.is_authenticated and result.is_hidden:
            raise GraphQLError('You do not have permission to perform this action')

        return result

    @staticmethod
    def resolve_post_list(root, info, **args):
        authenticated = info.context.user.is_authenticated
        category_id = args.get('category_id')

        if category_id is None:
            posts = Post.objects.all()
        elif category_id == 0:
            posts = Post.objects.filter(category__isnull=True)
        else:
            try:
                category = Category.objects.get(id=category_id)
                if not authenticated and category.is_hidden:
                    raise GraphQLError('You do not have permission to perform this action')
            except Category.DoesNotExist:
                return []

            subcategories = category.get_descendants(include_self=True)
            if not authenticated:
                subcategories = subcategories.exclude(is_hidden=True)

            posts = Post.objects.filter(category__in=subcategories)

        if not authenticated:
            posts = posts.exclude(Q(is_hidden=True) | Q(category__is_hidden=True))

        return posts

    @staticmethod
    def resolve_post(root, info, **args):
        try:
            post = Post.objects.get(id=args.get('id'))
        except Post.DoesNotExist:
            return None

        if not info.context.user.is_authenticated and \
                (post.is_hidden or (post.category is not None and post.category.is_hidden)):
            raise GraphQLError('You do not have permission to perform this action')

        return post


class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=False)
    content = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    thumbnail = graphene.String(required=False)


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        data = PostInput(required=True)

    success = graphene.Boolean()
    created_post = graphene.Field(PostType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        data = args.get('data')

        print(data)

        if 'category' in data:
            try:
                category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                raise GraphQLError(f'Category with id {data.category} does not exist.')
        else:
            category = None

        try:
            post = Post.objects.create(title=data.title,
                                       category=category,
                                       content=data.content,
                                       is_hidden=data.is_hidden,
                                       thumbnail=data.thumbnail)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create post: {e}')

        return CreatePostMutation(success=True, created_post=post)


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = PostInput(required=True)

    success = graphene.Boolean()
    updated_post = graphene.Field(PostType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        post_id = args.get('id')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return UpdatePostMutation(success=False, updated_post=None)

        data = args.get('data')
        post.title = data.get('title', post.title)
        if 'category' in data:
            post.category = Category.objects.get(id=data.category)
        else:
            post.category = None
        post.content = data.get('content', post.content)
        post.is_hidden = data.get('is_hidden', post.is_hidden)
        post.thumbnail = data.get('thumbnail', post.thumbnail)

        try:
            post.save()
        except (DatabaseError, IntegrityError) as e:
            return UpdatePostMutation(success=False, updated_post=None)

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        post_id = args.get('id')

        try:
            post = Post.objects.get(id=post_id)
            post.is_deleted = True
            post.save()
            return DeletePostMutation(success=True)
        except Post.DoesNotExist:
            raise GraphQLError(f'Post with id {post_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(f'Failed to delete post with id {post_id}')


class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
