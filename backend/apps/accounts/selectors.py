"""Read-optimized queries for accounts."""
from django.db.models import QuerySet


def base_queryset() -> QuerySet:
    from . import models
    names = [n for n in dir(models) if n[0].isupper() and not n.startswith("_")]
    model = getattr(models, names[0]) if names else None
    return model.objects.all() if model else QuerySet.none()


def for_user(user) -> QuerySet:
    qs = base_queryset()
    if not qs.model:
        return qs
    if hasattr(qs.model, "patient"):
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        return qs.filter(patient=user)
    if hasattr(qs.model, "user"):
        return qs.filter(user=user)
    if hasattr(qs.model, "owner"):
        return qs.filter(owner=user)
    return qs.none()


def active_only(qs: QuerySet) -> QuerySet:
    if hasattr(qs.model, "status"):
        return qs.exclude(status__in=["archived", "cancelled", "removed"])
    if hasattr(qs.model, "is_active"):
        return qs.filter(is_active=True)
    return qs
