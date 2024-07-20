from graphql import GraphQLError


class InformativeGraphQLError(GraphQLError):
    def __init__(self, message, code):
        super().__init__(message, extensions={
            "type": self.__class__.__name__, "code": code})


class InvalidValueError(InformativeGraphQLError):
    def __init__(self, message='유효하지 않은 요청입니다'):
        super().__init__(message, code=400)


class NotFoundError(InformativeGraphQLError):
    def __init__(self, message='항목을 찾을 수 없습니다'):
        super().__init__(message, code=404)


class PermissionDeniedError(InformativeGraphQLError):
    def __init__(self, message='권한이 없습니다'):
        super().__init__(message, code=403)


class InternalServerError(InformativeGraphQLError):
    def __init__(self, message='요청을 처리하지 못했습니다'):
        super().__init__(message, code=500)
