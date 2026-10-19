"""Selectors for insurance."""
from django.db.models import QuerySet

from .models import InsurancePayer, PatientInsurancePolicy, EligibilityCheck, PriorAuthorization


def insurancepayer_for_user(user) -> QuerySet:
    qs = InsurancePayer.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    for field in ("patient", "user", "owner"):
        if hasattr(InsurancePayer, field):
            return qs.filter(**{field: user}).order_by("-created_at")
    return qs.none()
