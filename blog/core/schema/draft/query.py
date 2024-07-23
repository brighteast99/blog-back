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
    def resolve_draft(root, info, **args):
        try:
            draft = Draft.objects.get(id=args.get("id"))
        except Draft.DoesNotExist:
            raise NotFoundError("임시 저장본을 찾을 수 없습니다")

        return draft

    @staticmethod
    @login_required
    def resolve_drafts(root, info, **args):
        return Draft.objects.all()
