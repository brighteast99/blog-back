import graphene
from django.db import DatabaseError, IntegrityError

from blog.core.errors import InternalServerError, NotFoundError
from blog.core.models import Template
from blog.utils.decorators import login_required

from . import TemplateType


class TemplateInput(graphene.InputObjectType):
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
    def mutate(root, info, **args):
        data = args.get("data")

        try:
            template = Template.objects.create(
                title=data.title,
                content=data.content,
                text_content=data.text_content,
                thumbnail=data.thumbnail,
                images=data.images,
            )
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
    def mutate(root, info, **args):
        template_id = args.get("id")

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise NotFoundError("템플릿을 찾을 수 없습니다")

        data = args.get("data")
        template.title = data.get("title", template.title)
        template.content = data.get("content", template.content)
        template.text_content = data.get("text_content", template.text_content)
        template.thumbnail = data.get("thumbnail")
        template.images = data.get("images", template.images)

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
    def mutate(self, info, **args):
        template_id = args.get("id")

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
