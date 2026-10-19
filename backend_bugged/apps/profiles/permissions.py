from rest_framework.permissions import BasePermission


class IsProfilesOwner(BasePermission):
    message = "You do not have access to this profiles resource."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id
