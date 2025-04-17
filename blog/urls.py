"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import requests
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from .settings import AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME


def minio_static_response(request):
    res = requests.get(
        f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/staticfiles/index.html"
    )
    return HttpResponse(res.text, content_type="text/html")


@method_decorator(csrf_exempt, name="dispatch")
class CsrfExemptGraphQLView(GraphQLView):
    pass


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", CsrfExemptGraphQLView.as_view(graphiql=True)),
]

urlpatterns.append(re_path(r"^.*$", minio_static_response))
