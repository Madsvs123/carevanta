from django.apps import AppConfig


class MedicalRecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.medical_recordsx"
    verbose_name = "Medical Records"

    def ready(self):
        from . import signals  # noqa: F401
