"""Role-based permission classes."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") == "patient"


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") == "doctor"


class IsClinicStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", "") in ("staff", "admin")


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, "role", "") == "admin"
        )


class IsOwnerOrDoctor(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return True
        if hasattr(obj, "patient_id") and obj.patient_id == user.id:
            return True
        if hasattr(obj, "doctor") and obj.doctor.user_id == user.id:
            return True
        if hasattr(obj, "owner_id" and obj.owner_id == user.id:
            return True
        return False
