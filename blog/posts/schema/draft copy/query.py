import graphene
from graphql_jwt.decorators import login_required

from blog.posts.models import Draft
from . import DraftType


class Query(graphene.ObjectType):
    draft_list = graphene.List(DraftType)
    draft = graphene.Field(DraftType, id=graphene.Int(required=True))

    @staticmethod
    @login_required
    def resolve_draft_list(root, info, **args):
        return Draft.objects.all()

    @staticmethod
    @login_required
    def resolve_draft(root, info, **args):
        try:
            draft = Draft.objects.get(id=args.get('id'))
        except Draft.DoesNotExist:
            return None

        return draft
