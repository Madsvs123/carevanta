"""Query selectors for notifications."""
from django.db.models import QuerySet, Prefetch

from .models import Notification, NotificationPreference


def notification_list_for_user(user) -> QuerySet:
    qs = Notification.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(Notification, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(Notification, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(Notification, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(Notification, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def notification_detail(pk: int, user) -> Notification | None:
    try:
        return notification_list_for_user(user).get(pk=pk)
    except Notification.DoesNotExist:
        return None


def active_notifications_records(user) -> QuerySet:
    qs = notification_list_for_user(user)
    if hasattr(Notification, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
