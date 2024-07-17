import graphene
from graphql_jwt.decorators import login_required

from blog.core.models import Template
from . import TemplateType


class Query(graphene.ObjectType):
    template_list = graphene.List(TemplateType)
    template = graphene.Field(TemplateType, id=graphene.Int(required=True))

    @staticmethod
    @login_required
    def resolve_template_list(root, info, **args):
        return Template.objects.all()

    @staticmethod
    @login_required
    def resolve_template(root, info, **args):
        try:
            template = Template.objects.get(id=args.get('id'))
        except Template.DoesNotExist:
            return None

        return template

        return draft
