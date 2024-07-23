import graphene

from .mutation import Mutation
from .query import Query
from .type import TemplateType

schema = graphene.Schema(query=Query, mutation=Mutation)
