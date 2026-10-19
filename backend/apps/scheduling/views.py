from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsDoctor
from .filters import (
    AvailabilitySlotFilter,
    BlockedPeriodFilter,
    DoctorScheduleFilter,
    ScheduleBreakFilter,
    WorkingHoursFilter,
)
from .models import AvailabilitySlot, BlockedPeriod, DoctorSchedule, ScheduleBreak, WorkingHours
from .serializers import (
    AvailabilitySlotSerializer,
    BlockedPeriodSerializer,
    DoctorScheduleDetailSerializer,
    DoctorScheduleSerializer,
    ScheduleBreakSerializer,
    WorkingHoursSerializer,
)
from .services import generate_slots_for_doctor, process_scheduling_workflow


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorScheduleSerializer
    filterset_class = DoctorScheduleFilter
    search_fields = ("name",)
    ordering_fields = ("created_at", "name")

    def get_queryset(self):
        qs = DoctorSchedule.objects.select_related("doctor", "doctor__user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        doctor_id = self.request.query_params.get("doctor_id")
        if doctor_id:
            return qs.filter(doctor_id=doctor_id, is_active=True)
        return qs.none()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DoctorScheduleDetailSerializer
        return DoctorScheduleSerializer


class WorkingHoursViewSet(viewsets.ModelViewSet):
    serializer_class = WorkingHoursSerializer
    filterset_class = WorkingHoursFilter

    def get_queryset(self):
        qs = WorkingHours.objects.select_related("schedule", "schedule__doctor")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(schedule__doctor__user=user)
        return qs.none()


class ScheduleBreakViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleBreakSerializer
    filterset_class = ScheduleBreakFilter

    def get_queryset(self):
        qs = ScheduleBreak.objects.select_related("working_hours__schedule__doctor")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(working_hours__schedule__doctor__user=user)
        return qs.none()


class BlockedPeriodViewSet(viewsets.ModelViewSet):
    serializer_class = BlockedPeriodSerializer
    filterset_class = BlockedPeriodFilter
    ordering_fields = ("start_datetime",)

    def get_queryset(self):
        qs = BlockedPeriod.objects.select_related("doctor", "doctor__user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        return qs.none()

    def perform_create(self, serializer):
        from apps.profiles.models import DoctorProfile

        doctor = DoctorProfile.objects.get(user=self.request.user)
        serializer.save(doctor=doctor, created_by=self.request.user)


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySlotSerializer
    filterset_class = AvailabilitySlotFilter
    ordering_fields = ("start_datetime", "status")
    ordering = ("start_datetime",)

    def get_queryset(self):
        qs = AvailabilitySlot.objects.select_related("doctor", "doctor__user")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user)
        doctor_id = self.request.query_params.get("doctor_id")
        if doctor_id:
            return qs.filter(doctor_id=doctor_id, status=AvailabilitySlot.Status.AVAILABLE)
        return qs.none()

    @action(detail=False, methods=["post"], url_path="generate-slots", permission_classes=[IsDoctor])
    def generate_slots(self, request):
        from apps.profiles.models import DoctorProfile

        doctor = DoctorProfile.objects.get(user=request.user)
        if request.data.get("doctor_id") or (request.user.is_staff or getattr(request.user, "role", "") == "admin"):
            doctor = DoctorProfile.objects.get(pk=request.data["doctor_id"])
        days = int(request.data.get("days_ahead", 30))
        slots = generate_slots_for_doctor(doctor, days_ahead=days)
        return ({"created": len(slots), "doctor_id": doctor.id})


class SchedulingDashboardViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"module": "scheduling", "summary": process_scheduling_workflow(request.user)})
