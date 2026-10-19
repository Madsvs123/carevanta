from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prescriptionsx"
    verbose_name = "Prescriptions"

    def ready(self):
        from . import signals  # noqa: F401
