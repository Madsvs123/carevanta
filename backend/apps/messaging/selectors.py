"""Query selectors for messaging."""
from django.db.models import QuerySet, Prefetch

from .models import Conversation, Message, MessageAttachment


def conversation_list_for_user(user) -> QuerySet:
    qs = Conversation.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(Conversation, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(Conversation, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(Conversation, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(Conversation, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def conversation_detail(pk: int, user) -> Conversation | None:
    try:
        return conversation_list_for_user(user).get(pk=pk)
    except Conversation.DoesNotExist:
        return None


def active_messaging_records(user) -> QuerySet:
    qs = conversation_list_for_user(user)
    if hasattr(Conversation, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
