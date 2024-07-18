import graphene
from graphql_jwt.decorators import login_required
from blog.core.errors import NotFoundError

from blog.core.models import Draft
from . import DraftType


class Query(graphene.ObjectType):
    draft = graphene.Field(DraftType, id=graphene.Int(required=True))
    drafts = graphene.List(DraftType)

    @staticmethod
    @login_required
    def resolve_draft(root, info, **args):
        try:
            draft = Draft.objects.get(id=args.get('id'))
        except Draft.DoesNotExist:
            raise NotFoundError()

        return draft

    @staticmethod
    @login_required
    def resolve_drafts(root, info, **args):
        return Draft.objects.all()
