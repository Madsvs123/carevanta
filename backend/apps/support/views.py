from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .filters import SupportTicketFilter, TicketMessageFilter, TicketAttachmentFilter
from .models import SupportTicket, TicketMessage, TicketAttachment
from .serializers import (
    SupportTicketSerializer, TicketMessageSerializer, TicketAttachmentSerializer, SupportTicketDetailSerializer,
)
from .services import get_support_dashboard


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = SupportTicketFilter
    search_fields = ["subject", "ticket_number"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SupportTicketDetailSerializer
        return SupportTicketSerializer

    def get_queryset(self):
        qs = SupportTicket.objects.all(
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") in ("admin", "staff"):
            return qs.order_by("-created_at")
        return qs.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = ticket.Status.CLOSED
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        ticket.status = ticket.Status.OPEN if hasattr(ticket.Status, "OPEN") else "open"
        ticket.resolved_at = None
        ticket.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(self.get_serializer(ticket).data)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        assignee_id = request.data.get("assignee_id")
        if hasattr(ticket, "assignee_id") and assignee_id:
            ticket.assignee_id = assignee_id
            ticket.save(update_fields=["assignee_id", "updated_at"])
        return Response(self.get_serializer(ticket).data)


class TicketMessageViewSet(viewsets.ModelViewSet):
    serializer_class = TicketMessageSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = TicketMessageFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = TicketMessage.objects.all()
        if user.is_staff or getattr(user, "role", "") in ("admin", "staff"):
            return qs.order_by("created_at")
        return qs.filter(ticket__user=user).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TicketAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = TicketAttachmentSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = TicketAttachmentFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = TicketAttachment.objects.all()
        if user.is_staff or getattr(user, "role", "") in ("admin", "staff"):
            return qs.order_by("-created_at")
        return qs.filter(ticket__user=user).order_by("-created_at")


class SupportDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_support_dashboard(request.user))
