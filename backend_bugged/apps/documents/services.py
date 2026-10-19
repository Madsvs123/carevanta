"""Business logic for documents."""
from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import DocumentFolder, Document


def get_documents_dashboard(user):
    summary = {
        "module": "documents",
        "generated_at": timezone.now().isoformat(),
        "counts": {},
        "recent": [],
    }
    qs = _queryset_for_user(DocumentFolder, user)
    summary["counts"]["total"] = qs.count()
    if hasattr(DocumentFolder, "status"):
        summary["counts"]["by_status"] = dict(
            qs.values("status").annotate(c=Count("id")).values_list("status", "c")
        )
    summary["recent"] = list(qs.order_by("-created_at")[:5].values("id", "created_at"))
    return summary


def process_documents_workflow(user):
    return get_documents_dashboard(user)


def _queryset_for_user(model, user):
    qs = model.objects.all()
    if user.is_staff or getattr(user, "role", "") == "admin":
        return qs
    if hasattr(model, "patient"):
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        return qs.filter(patient=user)
    if hasattr(model, "user"):
        return qs.filter(user=user)
    if hasattr(model, "owner"):
        return qs.filter(owner=user)
    return qs.none()
