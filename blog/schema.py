import graphene

from blog.core.schema import Mutation as PostMutation
from blog.core.schema import Query as PostQuery
from blog.info.schema import Mutation as InfoMutation
from blog.info.schema import Query as InfoQuery
from blog.jwt.schema import Mutation as AuthMutation


class Query(InfoQuery, PostQuery, graphene.ObjectType):
    pass


class Mutation(InfoMutation, AuthMutation, PostMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
