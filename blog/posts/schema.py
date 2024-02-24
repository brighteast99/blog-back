import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db import DatabaseError, IntegrityError

from blog.posts.models import Category, Post


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('id', 'name', 'subcategory_of', 'subcategories')


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = '__all__'
        # ordering = ('-id',)


class Query(graphene.ObjectType):
    posts = graphene.List(PostType, category=graphene.Int())
    category_by_name = graphene.Field(CategoryType, name=graphene.String(required=True))

    def resolve_posts(root, info):
        # We can easily optimize query count in the resolve method
        return Post.objects.select_related('category').all()

    def resolve_category_by_name(root, info, name):
        try:
            return Category.objects.get(name=name)
        except Category.DoesNotExist:
            return None


class CreatePostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=True)
    content = graphene.String(required=True)


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        data = CreatePostInput(required=True)

    success = graphene.Boolean()
    created_post = graphene.Field(PostType)

    def mutate(root, info, **args):
        data = args.get('data')

        try:
            category = Category.objects.get(id=data.category)
        except Category.DoesNotExist:
            raise GraphQLError(f'Category with id {data.category} does not exist.')

        try:
            post = Post.objects.create(title=data.title,
                                       category=category,
                                       content=data.content)
        except DatabaseError or IntegrityError as e:
            raise GraphQLError(f'Failed to create post: {e}')

        return CreatePost(success=True, created_post=post)


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
        except DatabaseError or IntegrityError as e:
            raise GraphQLError(f'Failed to update post with id {post_id}: {e}')

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

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
