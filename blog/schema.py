import graphene
from blog.posts.schema import Query as PostQuery, Mutation as PostMutation
# import blog.posts.schema.Query


class Query(
    PostQuery,
    graphene.ObjectType
):
    pass


class Mutation(
    PostMutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)