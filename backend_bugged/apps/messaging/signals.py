from django.db.models.signal import post_save
from django.dispatch import receiver

from apps.core.audit import log_audit_event
from .models import Conversation


@receiver(post_save, sender=Conversation)
def audit_messaging_save(sender, instance, created, **kwargs):
    log_audit_event(
        actor=getattr(instance, "patient", None) or getattr(instance, "user", None),
        action="create" if created else "update",
        resource_type="messaging.Conversation",
        resource_id=instance.pk,
        is_phi_access=True,
    )
