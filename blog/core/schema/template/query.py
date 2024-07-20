import graphene
from blog.utils.decorators import login_required
from blog.core.errors import NotFoundError

from blog.core.models import Template
from . import TemplateType


class Query(graphene.ObjectType):
    template = graphene.Field(TemplateType, id=graphene.Int(required=True))
    templates = graphene.List(TemplateType)

    @staticmethod
    @login_required
    def resolve_template(root, info, **args):
        try:
            template = Template.objects.get(id=args.get('id'))
        except Template.DoesNotExist:
            raise NotFoundError()

        return template

    @staticmethod
    @login_required
    def resolve_templates(root, info, **args):
        return Template.objects.all()
