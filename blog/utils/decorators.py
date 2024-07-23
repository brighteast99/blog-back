from graphql_jwt.decorators import user_passes_test

from blog.core.errors import PermissionDeniedError

login_required = user_passes_test(lambda u: u.is_authenticated, PermissionDeniedError)
