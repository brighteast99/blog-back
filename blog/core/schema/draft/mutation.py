import graphene
from django.db import DatabaseError, IntegrityError
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from blog.core.models import Category, Draft
from . import DraftType


class DraftInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=False)
    content = graphene.String(required=True)
    is_hidden = graphene.Boolean(required=True)
    thumbnail = graphene.String(required=False)
    images = graphene.List(graphene.String, required=True, default=list)


class CreateDraftMutation(graphene.Mutation):
    class Arguments:
        data = DraftInput(required=True)

    success = graphene.Boolean()
    created_draft = graphene.Field(DraftType)

    @staticmethod
    @login_required
    def mutate(root, info, **args):
        data = args.get('data')

        if 'category' in data:
            try:
                category = Category.objects.get(id=data.category)
            except Category.DoesNotExist:
                raise GraphQLError(
                    f'Category with id {data.category} does not exist.')
        else:
            category = None

        try:
            draft = Draft.objects.create(title=data.title,
                                         category=category,
                                         content=data.content,
                                         is_hidden=data.is_hidden,
                                         thumbnail=data.thumbnail,
                                         images=data.images)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create post: {e}')

        return CreateDraftMutation(success=True, created_draft=draft)


class DeleteDraftMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        draft_id = args.get('id')

        try:
            draft = Draft.objects.get(id=draft_id)
            draft.delete()
            return DeleteDraftMutation(success=True)
        except Draft.DoesNotExist:
            raise GraphQLError(f'Draft with id {draft_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(f'Failed to delete draft with id {draft_id}')


class Mutation(graphene.ObjectType):
    create_draft = CreateDraftMutation.Field()
    delete_draft = DeleteDraftMutation.Field()
