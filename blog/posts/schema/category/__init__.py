from .type import CategoryType
from .query import Query
from .mutation import Mutation

import graphene


schema = graphene.Schema(query=Query, mutation=Mutation)
