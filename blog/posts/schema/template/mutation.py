import graphene
from django.db import DatabaseError, IntegrityError
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from blog.posts.models import Template
from . import TemplateType


class TemplateInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    content = graphene.String(required=True)
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
        data = args.get('data')

        try:
            template = Template.objects.create(name=data.name,
                                               content=data.content,
                                               thumbnail=data.thumbnail,
                                               images=data.images)
        except (DatabaseError, IntegrityError) as e:
            raise GraphQLError(f'Failed to create template: {e}')

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
        template_id = args.get('id')

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            return UpdateTemplateMutation(success=False, updated_template=None)

        data = args.get('data')
        template.name = data.get('name', template.name)
        template.content = data.get('content', template.content)
        template.thumbnail = data.get('thumbnail')
        template.images = data.get('images', template.images)

        try:
            template.save()
        except (DatabaseError, IntegrityError) as e:
            return UpdateTemplateMutation(success=False, updated_template=None)

        return UpdateTemplateMutation(success=True, updated_template=template)


class DeleteTemplateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, **args):
        template_id = args.get('id')

        try:
            template = Template.objects.get(id=template_id)
            template.delete()
            return DeleteTemplateMutation(success=True)
        except Template.DoesNotExist:
            raise GraphQLError(
                f'Tempalte with id {template_id} does not exist.')
        except DatabaseError:
            raise GraphQLError(
                f'Failed to delete template with id {template_id}')


class Mutation(graphene.ObjectType):
    create_template = CreateTemplateMutation.Field()
    update_template = UpdateTemplateMutation.Field()
    delete_template = DeleteTemplateMutation.Field()
