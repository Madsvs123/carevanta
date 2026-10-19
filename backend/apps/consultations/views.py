from rest_framewor import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .models import Consultation, ConsultationMessage, ConsultationNote
from .serializers import ConsultationSerializer, ConsultationMessageSerializer, ConsultationNoteSerializer, ConsultationDetailSerializer
from .services import create_consultation_room, get_consultations_dashboard
from .filters import ConsultationFilter, ConsultationMessageFilter, ConsultationNoteFilter


class ConsultationViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = ConsultationFilter
    ordering_fields = ("created_at", "started_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConsultationDetailSerializer
        return ConsultationSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Consultation.objects.all().select_related("appointment", "appointment__patient", "appointment__doctor")
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(
            Q(appointment__patient=user) | Q(appointment__doctor__user=user)
        ).distinct().order_by("-created_at")

    @action(detail=False, methods=["post"], url_path="create-room")
    def create_room(self, request):
        from apps.appointments.models import Appointment
        appointment = Appointment.objects.get(pk=request.data["appointment_id"])
        consultation = create_consultation_room(appointment)
        return (self.get_serializer(consultation).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        c = self.get_object()
        c.status = getattr(c.Status, "IN_PROGRESS", "in_progress") if hasattr(c, "Status") else "in_progress"
        c.started_at = timezone.now()
        c.save(update_fields=["status", "started_at", "updated_at"])
        return Response(self.get_serializer(c).data)

    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        c = self.get_object()
        c.status = getattr(c.Status, "COMPLETED", "completed") if hasattr(c, "Status") else "completed"
        c.ended_at = timezone.now()
        c.save(update_fields=["status", "ended_at", "updated_at"])
        return Response(self.get_serializer(c).data)


class ConsultationMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationMessageSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = ConsultationMessageFilter
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = ConsultationMessage.objects.all().select_related("consultation")
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("created_at")
        return qs.filter(
            Q(consultation__appointment__patient=user) | Q(consultation__appointment__doctor__user=user)
        ).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ConsultationNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationNoteSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = ConsultationNoteFilter
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = ConsultationNote.objects.all()
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(author=user).order_by("-created_at")
        return qs.filter(consultation__appointment__patient=user, is_private=False).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ConsultationsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_consultations_dashboard(request.user))
