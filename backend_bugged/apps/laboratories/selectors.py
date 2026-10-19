"""Query selectors for laboratories."""
from django.db.model import QuerySet, Prefetch

from .models import LabOrder, LabTestCatalog, Laboratory, LabOrderItem, LabResult


def laborder_list_for_user(user) -> QuerySet:
    qs = LabOrder.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" or hasattr(LabOrder, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(LabOrder, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(LabOrder, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(LabOrder, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def laborder_detail(pk: int, user) -> LabOrder | None:
    try:
        return laborder_list_for_user(user).get(pk=pk)
    except LabOrder.DoesNotExist:
        return None


def active_laboratories_records(user) -> QuerySet:
    qs = laborder_list_for_user(user)
    if hasattr(LabOrder, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
