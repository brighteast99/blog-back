import graphene
from django.db import DatabaseError, IntegrityError

from blog.core.errors import InternalServerError, InvalidValueError, NotFoundError
from blog.core.models import Category, Post
from blog.media.models import Image
from blog.media.utils import get_image, get_images
from blog.utils.convertid import localid
from blog.utils.decorators import login_required

from . import PostType


class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int()
    content = graphene.String(required=True)
    text_content = graphene.String(required=True)
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
    def mutate(self, info, **kwargs):
        data = kwargs.get("data")

        if "category" in data:
            try:
                category = Category.objects.get(id=data.category, is_deleted=False)
            except Category.DoesNotExist:
                raise InvalidValueError("게시판을 찾을 수 없습니다")
        else:
            category = None

        try:
            thumbnail = get_image(data.thumbnail)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 썸네일입니다")

        try:
            images = get_images(data.images)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 이미지가 포함되어 있습니다")

        try:
            post = Post.objects.create(
                title=data.title,
                category=category,
                content=data.content,
                text_content=data.text_content,
                thumbnail=thumbnail,
                is_hidden=data.is_hidden,
            )
            post.images.set(images)
            post.save()
        except (DatabaseError, IntegrityError):
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
    def mutate(self, info, **kwargs):
        post_id = localid(kwargs.get("id"))

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise NotFoundError("게시글을 찾을 수 없습니다")

        data = kwargs.get("data")
        post.title = data.get("title", post.title)
        if "category" in data:
            try:
                post.category = Category.objects.get(id=data.category, is_deleted=False)
            except Category.DoesNotExist:
                InvalidValueError("존재하지 않는 게시판입니다")
        else:
            post.category = None

        post.content = data.get("content", post.content)
        post.text_content = data.get("text_content", post.text_content)
        try:
            post.thumbnail = get_image(data.thumbnail)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 썸네일입니다")

        try:
            post.images.set(get_images(data.images))
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 이미지가 포함되어 있습니다")
        post.is_hidden = data.get("is_hidden", post.is_hidden)

        try:
            post.save()
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return UpdatePostMutation(success=True, updated_post=post)


class DeletePostMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        post_id = localid(kwargs.get("id"))

        try:
            post = Post.objects.get(id=post_id)
            post.is_deleted = True
            post.save(update_fields=["is_deleted"])
            return DeletePostMutation(success=True)
        except Post.DoesNotExist:
            raise NotFoundError("게시글을 찾을 수 없습니다")
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    create_post = CreatePostMutation.Field()
    update_post = UpdatePostMutation.Field()
    delete_post = DeletePostMutation.Field()
