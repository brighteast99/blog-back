from django.apps import AppConfig


class JWTConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog.jwt'

    def ready(self):
        import blog.jwt.signals
