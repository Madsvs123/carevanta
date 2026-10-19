from rest_framework.permissions import BasePermission


class IsMedicalRecordsOwner(BasePermission)
    message = "You do not have access to this medical_records resource."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id
