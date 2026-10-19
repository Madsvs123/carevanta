from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.audit import log_audit_event
from .models import DiscountCode


@receiver(post_save, sender=DiscountCode)
def audit_billing_save_(sender, instance, created, **kwargs):
    log_audit_event(
        actor=getattr(instance, "patient", None) or getattr(instance, "user", None),
        action="create" if created else "update",
        resource_type="billing.DiscountCode",
        resource_id=instance.pk,
        is_phi_access=True,
    )
