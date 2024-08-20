import graphene

from blog.core.errors import NotFoundError
from blog.core.models import Template
from blog.utils.decorators import login_required

from . import TemplateType


class Query(graphene.ObjectType):
    template = graphene.Field(TemplateType, id=graphene.Int(required=True))
    templates = graphene.List(TemplateType)

    @staticmethod
    @login_required
    def resolve_template(self, info, **kwargs):
        try:
            template = Template.objects.get(id=kwargs.get("id"))
        except Template.DoesNotExist:
            raise NotFoundError("템플릿을 찾을 수 없습니다")

        return template

    @staticmethod
    @login_required
    def resolve_templates(self, info, **kwargs):
        return Template.objects.all()
