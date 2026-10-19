from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "patient"


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "doctor"


class IsStaffMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) in (
            "staff",
            "lab_tech",
            "pharmacist",
            "admin",
        )


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, "role", None) == "admin"
        )


class IsEmailVerified(BasePermission):
    message = "Email verification required."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_email_verified


class IsIdentityVerified(BasePermission):
    message = "Identity verification required for this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_identity_verified


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, "user_id"):
            return obj.user_id == request.user.id
        if hasattr(obj, "owner_id"):
            return obj.owner_id == request.user.id
        if hasattr(obj, "patient_id"):
            return obj.patient_id == request.user.id
        return False


class CanAccessPHI(BasePermission):
    """Patients own data; doctors with relationship; staff with clinic membership."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return True
        if hasattr(obj, "patient_id") and obj.patient_id == user.id:
            return True
        if hasattr(obj, "doctor") and obj.doctor.user_id == user.id:
            return True
        return False
