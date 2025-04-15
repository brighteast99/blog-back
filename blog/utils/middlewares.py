from django.http import HttpResponseNotAllowed

from blog import settings


class DomainRouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        print(host, settings.PROXY_HOST)

        if host.startswith(settings.API_HOST):
            if (
                not settings.DEBUG
                and request.META["HTTP_X_FORWARDED_FOR"] not in settings.ADMIN_HOSTS
            ):
                return HttpResponseNotAllowed(["POST"])
            request.urlconf = "blog.urls_api"
        elif host.startswith(settings.ADMIN_HOST):
            request.urlconf = "blog.urls_admin"

        return self.get_response(request)
