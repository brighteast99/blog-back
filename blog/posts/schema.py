import json
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db import DatabaseError, IntegrityError
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
        return self.subcategories.all()

    @staticmethod
    def resolve_post_count(self, info, exclude_subcategories=False):
        if self.id is None:
            return Post.objects.count()

        if self.id == 0:
            return Post.objects.filter(category__isnull=True).count()

        if exclude_subcategories:
            return self.posts.count()

        subcategories = Category.get_descendants(self, include_self=True)
        return Post.objects.filter(category__in=subcategories).count()

    @staticmethod
    def resolve_posts(self, info):
        if self.id is None:
            return Post.objects.all()

        if self.id == 0:
            return Post.objects.filter(category__isnull=True)

        return self.posts.all()


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
        return Category.objects.all()

    @staticmethod
    def resolve_category_list(root, info):
        root_categories = Category.objects.root_nodes()

        def category_to_dict(instance):
            result = {
                'id': instance.id,
                'name': instance.name,
                'postCount': Post.objects.filter(category__in=instance.get_descendants(include_self=True)).count(),
                'subcategories': [category_to_dict(subcategory)
                                  for subcategory in instance.subcategories.all()]
            }
            return result

        categories_list = [{
            'name': '전체 게시글',
            'postCount': Post.objects.count(),
            'subcategories': []
        }]
        categories_list.extend([category_to_dict(category) for category in root_categories])
        categories_list.append({
            'id': 0,
            'name': '분류 미지정',
            'postCount': Post.objects.filter(category__isnull=True).count(),
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

        return Category.objects.filter(id=id).first()

    @staticmethod
    def resolve_post_list(root, info, **args):
        category_id = args.get('category_id')

        if category_id is None:
            return Post.objects.all()

        if category_id == 0:
            return Post.objects.filter(category__isnull=True)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return []

        subcategories = category.get_descendants(include_self=True)
        return Post.objects.filter(category__in=subcategories)

    @staticmethod
    def resolve_post(root, info, **args):
        try:
            post = Post.objects.get(id=args.get('id'))
        except Post.DoesNotExist:
            return None

        return post


class CreatePostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=False)
    content = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    thumbnail = graphene.String(required=False)


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        data = CreatePostInput(required=True)

    success = graphene.Boolean()
    created_post = graphene.Field(PostType)

    @staticmethod
    def mutate(root, info, **args):
        data = args.get('data')

        if data.category != 0:
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


class UpdatePostInput(graphene.InputObjectType):
    title = graphene.String()
    category = graphene.Int()
    content = graphene.String()


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = UpdatePostInput(required=True)

    success = graphene.Boolean()
    updated_post = graphene.Field(PostType)

    @staticmethod
    def mutate(root, info, **args):
        post_id = args.get('id')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError(f'Post with id {post_id} does not exist.')

        data = args.get('data')
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        if 'category' in data:
            post.category = Category.objects.get(id=data.category)

        try:
            post.save()
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to update post with id {post_id}: {e}')

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
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
