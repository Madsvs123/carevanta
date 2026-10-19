"""Query selectors for support."""
from django.db.models import QuerySet, Prefetch

from .models import SupportTicket, TicketMessage, TicketAttachment


def supportticket_list_for_user(user) -> QuerySet:
    qs = SupportTicket.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(SupportTicket, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(SupportTicket, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(SupportTicket, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(SupportTicket, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def supportticket_detail(pk: int, user) -> SupportTicket | None:
    try:
        return supportticket_list_for_user(user).get(pk=pk)
    except SupportTicket.DoesNotExist:
        return None


def active_support_records(user) -> QuerySet:
    qs = supportticket_list_for_user(user)
    if hasattr(SupportTicket, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
