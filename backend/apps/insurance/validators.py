"""Validators for insurance."""
from django.core.exceptions import ValidationError


def require_authenticated(user):
  if not user or not user.is_authenticated:
        raise ValidationError("Authentication required for Insurance.")


def require_staff(user):
    require_authenticated(user)
    if not (user.is_staff or getattr(user, "role", "") in ("admin", "staff")):
        raise ValidationError("Staff access required.")
