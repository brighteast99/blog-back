import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open("/run/secrets/django-secret-key", "r") as key:
    SECRET_KEY = key.read()

with open("/run/secrets/aws-access-key-id", "r") as key:
    AWS_ACCESS_KEY_ID = key.read()
with open("/run/secrets/aws-secret-access-key", "r") as key:
    AWS_SECRET_ACCESS_KEY = key.read()
AWS_S3_ENDPOINT_URL = f'https://{os.getenv("AWS_S3_ENDPOINT_URL")}'
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f'{os.getenv("AWS_S3_ENDPOINT_URL")}/{AWS_STORAGE_BUCKET_NAME}'
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_S3_FILE_OVERWRITE = False
AWS_LOCATION = ""
AWS_DEFAULT_ACL = "public-read"

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/static/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", os.getenv("PROXY_HOST")]

ADMIN_HOSTS = os.getenv("ADMIN_HOSTS", "").split()

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ["http://localhost", os.getenv("PROXY_ORIGIN")]
CORS_ALLOW_METHODS = (
    "GET",
    "OPTIONS",
    "POST",
)
CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "csrftoken",
    "x-requested-with",
)

CSRF_TRUSTED_ORIGINS = ["http://blog.localhost", os.getenv("PROXY_ORIGIN")]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "graphene_django",
    "django_filters",
    "graphene_file_upload.django",
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "blog.media",
    "blog.info",
    "blog.core",
    "blog.jwt",
    "mptt",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "blog.utils.middlewares.AdminAccessControlMiddleware",
]

ROOT_URLCONF = "blog.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "client")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "blog.wsgi.application"

try:
    with open("/run/secrets/postgres-user", "r") as key:
        POSTGRES_USER = key.read()

    with open("/run/secrets/postgres-password", "r") as key:
        POSTGRES_PASSWORD = key.read()

    with open("/postgres-host", "r") as key:
        POSTGRES_HOST = key.read()
except FileNotFoundError:
    POSTGRES_USER = "user"
    POSTGRES_PASSWORD = "pw"
    POSTGRES_HOST = "host"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "blog",
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

GRAPHENE = {
    "SCHEMA": "blog.schema.schema",
    "MIDDLEWARE": ["graphql_jwt.middleware.JSONWebTokenMiddleware"],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GRAPHQL_JWT = {"JWT_VERIFY_EXPIRATION": True, "JWT_LONG_RUNNING_REFRESH_TOKEN": True}

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, ".staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "client", "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
