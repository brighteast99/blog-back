import graphene
import graphql_jwt
from blog.posts.schema import Query as PostQuery, Mutation as PostMutation


class AuthMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


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
