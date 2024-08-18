import graphene
from django.db import DatabaseError, IntegrityError

from blog.core.errors import InternalServerError, InvalidValueError, NotFoundError
from blog.core.models import Category, Draft
from blog.media.models import Image
from blog.media.utils import get_image, get_images
from blog.utils.decorators import login_required

from . import DraftType


class DraftInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.Int()
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

        if "category" in data:
            try:
                category = Category.objects.get(id=data.category, is_deleted=False)
            except Category.DoesNotExist:
                InvalidValueError("게시판을 찾을 수 없습니다")
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
            draft = Draft.objects.create(
                title=data.title,
                category=category,
                content=data.content,
                text_content=data.text_content,
                thumbnail=thumbnail,
                is_hidden=data.is_hidden,
            )
            draft.images.set(images)
            draft.save()
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
