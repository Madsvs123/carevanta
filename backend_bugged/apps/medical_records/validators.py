"""Validation helpers for medical_records."""
from django.core.exceptions import ValidationError


def require_authenticated_user(user):
    if not user or not user.is_authenticated:
        raise ValidationError("Authentication required.")


def require_role(user, *roles):
    require_authenticated_user(user)
    if getattr(user, "role", None) not in roles and not user.is_staff:
        raise ValidationError("Insufficient role for this operation.")


def validate_positive_amount(value, field="amount"):
    if value is not None and value < 0:
        raise ValidationError({field: "Must be zero or positive."})
