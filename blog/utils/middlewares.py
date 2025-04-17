from blog import settings
from blog.urls import minio_static_response


class AdminAccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            if request.META["HTTP_X_FORWARDED_FOR"] not in settings.ADMIN_HOSTS:
                if request.path.startswith("/admin/"):
                    return minio_static_response(request)
        return self.get_response(request)
