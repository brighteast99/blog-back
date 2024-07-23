import graphene

from .mutation import Mutation
from .query import Query
from .type import DraftType

schema = graphene.Schema(query=Query, mutation=Mutation)
