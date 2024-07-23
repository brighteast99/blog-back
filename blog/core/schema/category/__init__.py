import graphene

from .type import CategoryType  # isort:skip
from .mutation import Mutation  # isort:skip
from .query import Query  # isort:skip

schema = graphene.Schema(query=Query, mutation=Mutation)
