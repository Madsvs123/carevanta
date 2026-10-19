"""Permissions for insurance."""
from rest_framework.permissions import BasePermission


class IsInsuranceParticipant(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return True
        for field in ("patient", "user", "owner"):
            if hasattr(obj, field) and getattr(obj, field) == user:
                return True
        return False
