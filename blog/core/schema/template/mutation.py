import graphene
from django.db import DatabaseError, IntegrityError

from blog.core.errors import InternalServerError, InvalidValueError, NotFoundError
from blog.core.models import Template
from blog.media.models import Image
from blog.media.utils import get_image, get_images
from blog.utils.decorators import login_required

from . import TemplateType


class TemplateInput(graphene.InputObjectType):
    template_name = graphene.String(required=True)
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    text_content = graphene.String(required=True)
    thumbnail = graphene.String(required=False)
    images = graphene.List(graphene.String, required=True, default=list)


class CreateTemplateMutation(graphene.Mutation):
    class Arguments:
        data = TemplateInput(required=True)

    success = graphene.Boolean()
    created_template = graphene.Field(TemplateType)

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        data = kwargs.get("data")

        try:
            thumbnail = get_image(data.thumbnail)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 썸네일입니다")

        try:
            images = get_images(data.images)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 이미지가 포함되어 있습니다")

        try:
            template = Template.objects.create(
                template_name=data.template_name,
                title=data.title,
                content=data.content,
                text_content=data.text_content,
                thumbnail=thumbnail,
            )
            template.images.set(images)
            template.save()
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return CreateTemplateMutation(success=True, created_template=template)


class UpdateTemplateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        data = TemplateInput(required=True)

    success = graphene.Boolean()
    updated_template = graphene.Field(TemplateType)

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        template_id = kwargs.get("id")

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise NotFoundError("템플릿을 찾을 수 없습니다")

        data = kwargs.get("data")
        template.template_name = data.get("template_name", template.template_name)
        template.title = data.get("title", template.title)
        template.content = data.get("content", template.content)
        template.text_content = data.get("text_content", template.text_content)
        try:
            template.thumbnail = get_image(data.thumbnail)
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 썸네일입니다")

        try:
            template.images.set(get_images(data.images))
        except Image.DoesNotExist:
            raise InvalidValueError("유효하지 않은 이미지가 포함되어 있습니다")

        try:
            template.save()
        except (DatabaseError, IntegrityError):
            raise InternalServerError()

        return UpdateTemplateMutation(success=True, updated_template=template)


class DeleteTemplateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **kwargs):
        template_id = kwargs.get("id")

        try:
            template = Template.objects.get(id=template_id)
            template.delete()
            return DeleteTemplateMutation(success=True)
        except Template.DoesNotExist:
            raise NotFoundError("템플릿을 찾을 수 없습니다")
        except DatabaseError:
            raise InternalServerError()


class Mutation(graphene.ObjectType):
    create_template = CreateTemplateMutation.Field()
    update_template = UpdateTemplateMutation.Field()
    delete_template = DeleteTemplateMutation.Field()
