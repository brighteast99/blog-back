from os.path import splitext

import graphene
from django.core.files.base import ContentFile
from django.db import DatabaseError, IntegrityError
from django.db.transaction import atomic
from graphene_file_upload.scalars import Upload

from blog.core.errors import InternalServerError, NotFoundError
from blog.core.models import Category
from blog.utils.decorators import login_required

from . import CategoryType


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    cover_image = Upload()
    subcategory_of = graphene.Int()


class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        data = CategoryInput(required=True)

    success = graphene.Boolean()
    created_category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        data = kwargs.get("data")

        if "subcategory_of" in data:
            try:
                supercategory = Category.objects.get(id=data.subcategory_of)
            except Category.DoesNotExist:
                raise NotFoundError("게시판을 찾을 수 없습니다")
        else:
            supercategory = None

        try:
            category = Category.objects.create(
                name=data.name,
                description=data.description,
                is_hidden=data.is_hidden,
                cover_image=data.cover_image,
                subcategory_of=supercategory,
            )
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return CreateCategoryMutation(success=True, created_category=category)


class UpdateCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = CategoryInput(required=True)

    success = graphene.Boolean()
    updated_category = graphene.Field(CategoryType)

    @staticmethod
    @login_required
    @atomic
    def mutate(self, info, **kwargs):
        category_id = kwargs.get("id")

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise NotFoundError("게시판을 찾을 수 없습니다")

        data = kwargs.get("data")
        category.name = data.get("name")
        if "subcategory_of" in data:
            try:
                category.subcategory_of = Category.objects.get(id=data.subcategory_of)
            except Category.DoesNotExist:
                raise NotFoundError("게시판을 찾을 수 없습니다")
        else:
            category.subcategory_of = None
        category.description = data.get("description")
        is_hidden = data.get("is_hidden")
        if is_hidden and not category.is_hidden:
            category.get_descendants().update(is_hidden=True)
        category.is_hidden = is_hidden

        if "cover_image" in data:
            cover_image = data.get("cover_image")
            category.cover_image.delete(save=False)
            if cover_image is not None:
                content_file = ContentFile(cover_image.read())
                _, ext = splitext(cover_image.name)
                category.cover_image.save(
                    f"{category.id}{ext}", content_file, save=False
                )

        try:
            category.save()
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return UpdateCategoryMutation(success=True, updated_category=category)


class DeleteCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        delete_posts = graphene.Boolean()

    success = graphene.Boolean()

    @staticmethod
    @atomic
    @login_required
    def mutate(self, info, **kwargs):
        category_id = kwargs.get("id")
        delete_posts = kwargs.get("delete_posts", False)

        try:
            category = Category.objects.get(id=category_id)
            for subcategory in category.get_descendants(include_self=True):
                subcategory.is_deleted = True
                subcategory.save(update_fields=["is_deleted"])
                for post in subcategory.posts.all():
                    if delete_posts:
                        post.is_deleted = True
                        post.save(update_fields=["is_deleted"])
                    else:
                        post.category = None
                        post.save(update_fields=["category"])

            return DeleteCategoryMutation(success=True)
        except Category.DoesNotExist:
            raise NotFoundError("게시판을 찾을 수 없습니다")
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()
