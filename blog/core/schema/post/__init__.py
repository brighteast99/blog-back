import graphene

from .mutation import Mutation
from .query import Query
from .type import PostType

schema = graphene.Schema(query=Query, mutation=Mutation)
