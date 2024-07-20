import graphene
from django.db import DatabaseError, IntegrityError
from graphql import GraphQLError
from blog.core.errors import InternalServerError, NotFoundError
from blog.utils.decorators import login_required

from blog.core.models import Category, Post
from . import PostType


class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=False)
    content = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    thumbnail = graphene.String(required=False)
    images = graphene.List(graphene.String, required=True, default=list)


class CreatePostMutation(graphene.Mutation):
    class Arguments:
        data = PostInput(required=True)

    success = graphene.Boolean()
    created_post = graphene.Field(PostType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        data = args.get('data')

        if 'category' in data:
            try:
                category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                raise NotFoundError('게시판을 찾을 수 없습니다')
        else:
            category = None

        try:
            post = Post.objects.create(title=data.title,
                                       category=category,
                                       content=data.content,
                                       is_hidden=data.is_hidden,
                                       thumbnail=data.thumbnail,
                                       images=data.images)
        except (DatabaseError, IntegrityError) as e:
            raise InternalServerError()

        return CreatePostMutation(success=True, created_post=post)


class UpdatePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
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
            raise NotFoundError('게시글을 찾을 수 없습니다')

        data = args.get('data')
        post.title = data.get('title', post.title)
        if 'category' in data and data.category != 0:
            try:
                post.category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                NotFoundError('게시판을 찾을 수 없습니다')
        else:
            post.category = None
        post.content = data.get('content', post.content)
        post.is_hidden = data.get('is_hidden', post.is_hidden)
        post.thumbnail = data.get('thumbnail')
        post.images = data.get('images', post.images)

        try:
            post.save()
        except (DatabaseError, IntegrityError) as e:
            raise InternalServerError()

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

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
            raise NotFoundError('게시글을 찾을 수 없습니다')
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
