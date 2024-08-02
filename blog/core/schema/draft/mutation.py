import graphene
from django.db import DatabaseError, IntegrityError

from blog.core.errors import InternalServerError, InvalidValueError, NotFoundError
from blog.core.models import Category, Draft
from blog.utils.decorators import login_required

from . import DraftType


class DraftInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int(required=True)
    content = graphene.String(required=True)
    text_content = graphene.String(required=True)
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
        data = args.get("data")

        if data.category > 0:
            try:
                category = Category.objects.get(id=data.category, is_deleted=False)
            except Category.DoesNotExist:
                NotFoundError("게시판을 찾을 수 없습니다")
        else:
            category = None

        try:
            draft = Draft.objects.create(
                title=data.title,
                category=category,
                content=data.content,
                text_content=data.text_content,
                is_hidden=data.is_hidden,
                thumbnail=data.thumbnail,
                images=data.images,
            )
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return CreateDraftMutation(success=True, created_draft=draft)


class DeleteDraftMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        draft_id = args.get("id")

        try:
            draft = Draft.objects.get(id=draft_id)
            draft.delete()
            return DeleteDraftMutation(success=True)
        except Draft.DoesNotExist:
            raise NotFoundError("임시 저장본을 찾을 수 없습니다")
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    create_draft = CreateDraftMutation.Field()
    delete_draft = DeleteDraftMutation.Field()
