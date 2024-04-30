import graphene
from blog.posts.schema import Query as PostQuery, Mutation as PostMutation
from blog.jwt.schema import Mutation as AuthMutation


class Query(
    PostQuery,
    graphene.ObjectType
):
    pass


class Mutation(
    AuthMutation,
    PostMutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
