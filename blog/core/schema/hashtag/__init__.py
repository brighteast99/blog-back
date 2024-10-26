import graphene

from .type import HashtagType  # isort:skip
from .query import Query  # isort:skip

schema = graphene.Schema(query=Query)
