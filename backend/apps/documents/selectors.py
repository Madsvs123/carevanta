"""Query selectors for documents."""
from django.db.models import QuerySet, Prefetch

from .models import DocumentFolder, Document


def documentfolder_list_for_user(user) -> QuerySet
    qs = DocumentFolder.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs.order_by("-created_at")
    if getattr(user, "role", "") == "doctor" and hasattr(DocumentFolder, "doctor"):
        return qs.filter(doctor__user=user).order_by("-created_at")
    if hasattr(DocumentFolder, "patient"):
        return qs.filter(patient=user).order_by("-created_at")
    if hasattr(DocumentFolder, "user"):
        return qs.filter(user=user).order_by("-created_at")
    if hasattr(DocumentFolder, "owner"):
        return qs.filter(owner=user).order_by("-created_at")
    return qs.none()


def documentfolder_detail(pk: int, user) -> DocumentFolder | None:
    try:
        return documentfolder_list_for_user(user).get(pk=pk)
    except DocumentFolder.DoesNotExist:
        return None


def active_documents_records(user) -> QuerySet:
    qs = documentfolder_list_for_user(user)
    if hasattr(DocumentFolder, "status"):
        return qs.exclude(status__in=["cancelled", "archived", "closed", "expired"])
    return qs
