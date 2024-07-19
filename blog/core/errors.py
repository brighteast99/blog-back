from graphql import GraphQLError


class InvalidValueError(GraphQLError):
    def __init__(self, message='Invalid value'):
        super().__init__(message, extensions={
            "type": self.__class__.__name__, "errorCode": 400})


class NotFoundError(GraphQLError):
    def __init__(self, message='Target not found'):
        super().__init__(message, extensions={
            "type": self.__class__.__name__, "errorCode": 404})


class PermissionDeniedError(GraphQLError):
    def __init__(self, message='You do not have permission to perform this action'):
        super().__init__(message, extensions={
            "type": self.__class__.__name__, "errorCode": 403})
