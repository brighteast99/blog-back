import graphene

from blog.core.errors import NotFoundError
from blog.core.models import Draft
from blog.utils.decorators import login_required

from . import DraftType


class Query(graphene.ObjectType):
    draft = graphene.Field(DraftType, id=graphene.Int(required=True))
    drafts = graphene.List(DraftType)

    @staticmethod
    @login_required
    def resolve_draft(self, info, **kwargs):
        try:
            draft = Draft.objects.get(id=kwargs.get("id"))
        except Draft.DoesNotExist:
            raise NotFoundError("임시 저장본을 찾을 수 없습니다")

        return draft

    @staticmethod
    @login_required
    def resolve_drafts(self, info, **kwargs):
        return Draft.objects.all()
