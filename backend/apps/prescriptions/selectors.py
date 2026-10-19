"""Query selectors for prescriptions."""
from django.db.models import QuerySet, Prefetch

from .models import Prescription, PrescriptionItem, PrescriptionWarning, Pharmacy, PrescriptionRefillRequest


def prescription_list_for_user(user) -> QuerySet:
    qs = Prescription.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(Prescription, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(Prescription, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(Prescription, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(Prescription, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def prescription_detail(pk: int, user) -> Prescription | None:
    try:
        return prescription_list_for_user(user).get(pk=pk)
    except Prescription.DoesNotExist:
        return None


def active_prescriptions_records(user) -> QuerySet:
    qs = prescription_list_for_user(user)
    if hasattr(Prescription, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
