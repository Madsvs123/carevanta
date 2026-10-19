"""Query selectors for billing."""
from django.db.models import QuerySet, Prefetch

from .models import Invoice, Payment, Refund, InsuranceClaim, DoctorPayout, DiscountCode, TransactionHistory


def invoice_list_for_user(user) -> QuerySet:
    qs = Invoice.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(Invoice, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(Invoice, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(Invoice, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(Invoice, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def invoice_detail(pk: int, user) -> Invoice | None:
    try:
        return invoice_list_for_user(user).get(pk=pk)
    except Invoice.DoesNotExist:
        return None


def active_billing_records(user) -> QuerySet:
    qs = invoice_list_for_user(user)
    if hasattr(Invoice, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"]
    return qs
