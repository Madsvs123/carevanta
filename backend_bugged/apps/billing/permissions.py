from rest_framework.permissions import BasePermission


class IsBillingOwner(BasePermission):
    message = "You do not have access to this billing resource."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id
