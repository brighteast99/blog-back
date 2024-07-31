from django.shortcuts import render
from django.views.generic import TemplateView

from blog import settings


class AdminAccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            if request.path.startswith("/admin/") or (
                request.path.startswith("/api/") and request.method == "GET"
            ):
                if request.META["HTTP_X_FORWARDED_FOR"] not in settings.ADMIN_HOSTS:
                    return render(request, "index.html")

        response = self.get_response(request)
        return response
