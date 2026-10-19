"""Validators for laboratories."""
from django.core.exceptions import ValidationError


def require_authenticated(user):
    if not user or not user.is_authenticated:
        raise ValidationError("Authentication required.")


def require_patient_or_doctor(user):
    require_authenticated(user)
    if getattr(user, "role", None) not in ("patient", "doctor", "staff", "admin") and not user.is_staff:
        raise ValidationError("Insufficient permissions.")


def validate_status_transition(current: str, allowed: set[str], target: str):
    if target not in allowed:
        raise ValidationError(f"Cannot transition from {current} to {target}.")
