import graphene
from django.db import DatabaseError, IntegrityError
from django.db.transaction import atomic
from django.core.files.base import ContentFile
from graphql import GraphQLError
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

from blog.posts.models import Category
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
    def mutate(root, info, **args):
        data = args.get('data')

        if 'subcategory_of' in data:
            try:
                supercategory = Category.objects.get(id=data.subcategory_of)
            except Category.DoesNotExist:
                raise GraphQLError(
                    f'Category with id {data.subcategory_of} does not exist.')
        else:
            supercategory = None

        try:
            category = Category.objects.create(name=data.name,
                                               description=data.description,
                                               is_hidden=data.is_hidden,
                                               cover_image=data.cover_image,
                                               subcategory_of=supercategory)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create category: {e}')

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
    def mutate(root, info, **args):
        category_id = args.get('id')

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return UpdateCategoryMutation(success=False, updated_category=None)

        data = args.get('data')
        category.name = data.get('name')
        if 'subcategory_of' in data:
            try:
                category.subcategory_of = Category.objects.get(
                    id=data.subcategory_of)
            except Category.DoesNotExist:
                raise GraphQLError(
                    f'Category with id {data.subcategory_of} does not exist.')
        else:
            category.subcategory_of = None
        category.description = data.get('description')
        is_hidden = data.get('is_hidden')
        if is_hidden and not category.is_hidden:
            category.get_descendants().update(is_hidden=True)
        category.is_hidden = is_hidden

        if 'cover_image' in data:
            cover_image = data.get('cover_image')
            if cover_image is None:
                category.cover_image.delete()
            else:
                content_file = ContentFile(cover_image.read())
                category.cover_image.save(
                    cover_image.name, content_file, save=True)

        try:
            category.save()
        except (DatabaseError, IntegrityError) as e:
            return UpdateCategoryMutation(success=False, updated_category=None)

        return UpdateCategoryMutation(success=True, updated_category=category)


class DeleteCategoryMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @atomic
    @login_required
    def mutate(self, info, **args):
        category_id = args.get('id')

        try:
            category = Category.objects.get(id=category_id)
            category.get_descendants().update(is_deleted=True)
            category.is_deleted = True
            category.save()
            return DeleteCategoryMutation(success=True)
        except Category.DoesNotExist:
            raise GraphQLError(f'Post with id {category_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(
                f'Failed to delete category with id {category_id}')


class Mutation(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
    update_category = UpdateCategoryMutation.Field()
    delete_category = DeleteCategoryMutation.Field()
