import graphene
from blog.info.schema import Query as InfoQuery, Mutation as InfoMutation
from blog.core.schema import Query as PostQuery, Mutation as PostMutation
from blog.jwt.schema import Mutation as AuthMutation


class Query(
    InfoQuery,
    PostQuery,
    graphene.ObjectType
):
    pass


class Mutation(
    InfoMutation,
    AuthMutation,
    PostMutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
