from graphql import GraphQLError


class NotFoundError(GraphQLError):
    def __init__(self, message='Target not found'):
        super().__init__(message, extensions={"errorCode": 404})


class PermissionDeniedError(GraphQLError):
    def __init__(self, message='You do not have permission to perform this action'):
        super().__init__(message, extensions={"errorCode": 403})
