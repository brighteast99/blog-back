from blog.core.errors import PermissionDeniedError
from functools import wraps
from graphql_jwt.decorators import user_passes_test

login_required = user_passes_test(
    lambda u: u.is_authenticated, PermissionDeniedError)
