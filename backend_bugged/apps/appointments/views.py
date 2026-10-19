from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .models import Appointment, AppointmentReminder, WaitingListEntry
from .serializers import (
    AppointmentSerializer, AppointmentDetailSerializer,
    AppointmentReminderSerializer, WaitingListEntrySerializer,
)
from .services import BookingError, book_appointment, reschedule_appointment, get_appointments_dashboard
from .filters import AppointmentFilter, AppointmentReminderFilter, WaitingListEntryFilter


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = AppointmentFilter
    search_fields = ["reason_for_visit", "notes", "symptoms"]
    ordering_fields = ("scheduled_start", "created_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AppointmentDetailSerializer
        return AppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.all().select_related("patient", "doctor", "doctor__user", "slot")
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-scheduled_start")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-scheduled_start")
        return qs.filter(patient=user).order_by("-scheduled_start")

    @action(detail=False, methods=["post"])
    def book(self, request):
        from apps.profiles.models import DoctorProfile
        from apps.scheduling.models import AvailabilitySlot

        try:
            doctor = DoctorProfile.objects.get(pk=request.data["doctor_id"])
            slot = AvailabilitySlot.objects.get(pk=request.data["slot_id"], doctor=doctor)
            appointment = book_appointment(
                patient=request.user,
                doctor=doctor,
                slot=slot,
                reason=request.data.get("reason", ""),
                symptoms=request.data.get("symptoms", ""),
                appointment_type=request.data.get("appointment_type", "initial"),
            )
            return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
        except (DoctorProfile.DoesNotExist, AvailabilitySlot.DoesNotExist):
            return Response({"detail": "Invalid doctor or slot."}, status=400)
        except BookingError as exc:
            return Response({"detail": str(exc)}, status=400)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appt = self.get_object()
        appt.status = Appointment.Status.CONFIRMED
        appt.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(appt).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appt = self.get_object()
        appt.cancel(reason=request.data.get("reason", ""))
        return Response(self.get_serializer(appt).data)

    @action(detail=True, methods=["post"], url_path="check-in")
    def check_in(self, request, pk=None):
        appt = self.get_object()
        appt.check_in()
        return Response(self.get_serializer(appt).data)

    @action(detail=True, methods=["post"])
    def reschedule(self, request, pk=None):
        appt = self.get_object()
        try:
            updated = reschedule_appointment(
                appt,
                new_start=request.data.get("scheduled_start"),
                new_end=request.data.get("scheduled_end"),
                slot_id=request.data.get("slot_id"),
            )
            return Response(self.get_serializer(updated).data)
        except BookingError as exc:
            return Response({"detail": str(exc)}, status=400)


class AppointmentReminderViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentReminderSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = AppointmentReminderFilter
    ordering_fields = ("scheduled_for", "created_at", "id")

    def get_queryset(self):
        qs = AppointmentReminder.objects.all().select_related("appointment")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-scheduled_for")
        return qs.filter(appointment__patient=user).order_by("-scheduled_for")


class WaitingListEntryViewSet(viewsets.ModelViewSet):
    serializer_class = WaitingListEntrySerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = WaitingListEntryFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = WaitingListEntry.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class AppointmentsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_appointments_dashboard(request.user))
