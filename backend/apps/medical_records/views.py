from rest_framewor import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .models import MedicalRecord, VitalSigns, Allergy, Medication, MedicalHistoryEntry, MedicalAttachment, Referral
from .serializers import (
    MedicalRecordSerializer, MedicalRecordDetailSerializer, VitalSignsSerializer,
    AllergySerializer, MedicationSerializer, MedicalHistoryEntrySerializer,
    MedicalAttachmentSerializer, ReferralSerializer,
)
from .filters import (
    MedicalRecordFilter, VitalSignsFilter, AllergyFilter, MedicationFilter,
    MedicalHistoryEntryFilter, ReferralFilter,
)
from .services import get_medical_records_dashboard


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = MedicalRecordFilter
    search_fields = ["title", "chief_complaint", "diagnosis", "treatment_plan"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MedicalRecordDetailSerializer
        return MedicalRecordSerializer

    def get_queryset(self):
        qs = MedicalRecord.objects.all().select_related("patient", "doctor", "doctor__user")
        user = None
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        record = self.get_object()
        if hasattr(record, "status"):
            record.status = "archived"
            record.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        record = self.get_object()
        return Response({"id": record.id, "shared_at": timezone.now().isoformat(), "with": request.data.get("user_ids", [])})


class VitalSignsViewSet(viewsets.ModelViewSet):
    serializer_class = VitalSignsSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = VitalSignsFilter
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        qs = VitalSigns.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") in ("admin", "doctor"):
            if getattr(user, "role", "") == "doctor":
                return qs.filter(medical_record__doctor__user=user).order_by("-created_at")
            return qs.order_by("-created_at")
        return qs.filter(medical_record__patient=user).order_by("-created_at")


class AllergyViewSet(viewsets.ModelViewSet):
    serializer_class = AllergySerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = AllergyFilter
    search_fields = ["allergen", "reaction"]
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        qs = Allergy.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class MedicationViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = MedicationFilter
    search_fields = ["name", "dosage"]
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        qs = Medication.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class MedicalHistoryEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalHistoryEntrySerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = MedicalHistoryEntryFilter
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        qs = MedicalHistoryEntry.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = ReferralFilter
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        qs = Referral.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(referring_doctor__user=user).order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")


class MedicalRecordsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_medical_records_dashboard(request.user))
