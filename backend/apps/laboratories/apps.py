from django.app import AppConfig


class LaboratoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.laboratories"
    verbose_name = "Laboratories"

    def ready(self):
        from . import signals  # noqa: F401
