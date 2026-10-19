from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.audit import log_audit_event
from .models import Laboratory


@receiver(post_save, sender=Laboratory)
def audit_laboratories_save(sender, instance, created, **kwargs)
    log_audit_event(
        actor=getattr(instance, "patient", None) or getattr(instance, "user", None),
        action="create" if created else "update",
        resource_type="laboratories.Laboratory",
        resource_id=instance.pk,
        is_phi_access=True,
    )
