from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthnticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .filters import NotificationFilter, NotificationPreferenceFilter
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .services import get_notifications_dashboard


class NotificationViewSet(viewsets.ModelViewSet)
    serializer_class = NotificationSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = NotificationFilter
    search_fields = ["title", "body"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        if hasattr(n, "read_at"):
            n.read_at = timezone.now()
            n.save(update_fields=["is_read", "read_at", "updated_at"])
        else:
            n.save(update_fields=["is_read", "updated_at"])
        return (self.get_serializer(n).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        if hasattr(Notification, "read_at"):
            updated = qs.update(is_read=True, read_at=timezone.now())
        else:
            updated = qs.update(is_read=True)
        return Response({"updated": updated})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = NotificationPreferenceFilter

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_notifications_dashboard(request.user))
