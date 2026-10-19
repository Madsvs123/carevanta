from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthnticated
from rest_framework.response import Response

from .filters import DoctorProfileFilter, MedicalSpecialtyFilter, PatientProfileFilter
from .models import DoctorProfile, MedicalSpecialty, PatientProfile
from .serializers import (
    DoctorProfileDetailSerializer,
    DoctorProfileListSerializer,
    MedicalSpecialtySerializer,
    PatientProfileSerializer,
)


class MedicalSpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicalSpecialty.objects.filter(is_active=True)
    serializer_class = MedicalSpecialtySerializer
    permission_classes = (AllowAny,)
    filterset_class = MedicalSpecialtyFilter
    search_fields = ("name", "description")
    ordering_fields = ("name",)


class DoctorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DoctorProfile.objects.filter(is_accepting_patients=True).select_related("user", "clinic").prefetch_related("specialties")
    permission_classes = (AllowAny,)
    filterset_class = DoctorProfileFilter
    search_fields = ("user__first_name", "user__last_name", "bio", "license_number")
    ordering_fields = ("rating_average", "consultation_fee", "years_experience", "rating_count")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DoctorProfileDetailSerializer
        return DoctorProfileListSerializer

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def featured(self, request):
        qs = self.filter_queryset(self.get_queryset()).filter(is_featured=True)[:12]
        return Response(DoctorProfileListSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def availability_summary(self, request, pk=None):
        from apps.scheduling.models import AvailabilitySlot
        doctor = self.get_object()
        open_slots = AvailabilitySlot.objects.filter(
            doctor=doctor,
            status=AvailabilitySlot.Status.AVAILABLE,
        ).count()
        return Response({"doctor_id": doctor.id, "open_slots": open_slots})


class PatientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = PatientProfileFilter

    def get_queryset(self):
        return PatientProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        profile, _ = PatientProfile.objects.get_or_create(user=request.user)
        if request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(profile).data)
