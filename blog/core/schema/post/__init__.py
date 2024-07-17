from .type import PostType
from .query import Query
from .mutation import Mutation

import graphene


schema = graphene.Schema(query=Query, mutation=Mutation)
