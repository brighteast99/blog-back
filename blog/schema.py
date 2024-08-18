import graphene

from blog.core.schema import Mutation as CoreMutation
from blog.core.schema import Query as CoreQuery
from blog.info.schema import Mutation as InfoMutation
from blog.info.schema import Query as InfoQuery
from blog.jwt.schema import Mutation as AuthMutation
from blog.media.schema import Mutation as MediaMutation
from blog.media.schema import Query as MediaQuery


class Query(MediaQuery, InfoQuery, CoreQuery, graphene.ObjectType):
    pass


class Mutation(
    MediaMutation, InfoMutation, CoreMutation, AuthMutation, graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
