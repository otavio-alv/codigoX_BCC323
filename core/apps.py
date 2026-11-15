from django.apps import AppConfig


class CoreConfig(AppConfig):
    """layout comum e paginas de erro (templates/403.html, 404.html e 500.html)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Núcleo"
