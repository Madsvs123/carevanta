from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import CanAccessPHI
from .filters import (
    PrescriptionFilter, PrescriptionItemFilter, PrescriptionWarningFilter,
    PharmacyFilter, PrescriptionRefillRequestFilter,
)
from .models import Prescription, PrescriptionItem, PrescriptionWarning, Pharmacy, PrescriptionRefillRequest
from .serializers import (
    PrescriptionSerializer, PrescriptionItemSerializer, PrescriptionWarningSerializer,
    PharmacySerializer, PrescriptionRefillRequestSerializer, PrescriptionDetailSerializer,
)
from .services import process_prescriptions_workflow, get_prescriptions_dashboard


class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PrescriptionFilter
    search_fields = ["prescription_number", "notes"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PrescriptionDetailSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        qs = Prescription.objects.all().select_related("patient", "doctor", "doctor__user", "pharmacy")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(patient_id=0).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        rx = self.get_object()
        from .services import activate_prescription
        activate_prescription(rx, request.user)
        return Response(self.get_serializer(rx).data)

    @action(detail=True, methods=["get"])
    def check_warnings(self, request, pk=None):
        rx = self.get_object()
        from .services import check_prescription_warnings
        return Response({"warnings": check_prescription_warnings(rx)})


class PrescriptionItemViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionItemSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PrescriptionItemFilter
    search_fields = ["medication_name", "generic_name"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = PrescriptionItem.objects.all().select_related("prescription")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(prescription__doctor__user=user).order_by("-created_at")
        return qs.filter(prescription__patient=user).order_by("-created_at")


class PrescriptionWarningViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionWarningSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PrescriptionWarningFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = PrescriptionWarning.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(prescription__doctor__user=user).order_by("-created_at")
        return qs.filter(prescription__patient=user).order_by("-created_at")


class PharmacyViewSet(viewsets.ModelViewSet):
    serializer_class = PharmacySerializer
    permission_classes = (AllowAny,)
    filterset_class = PharmacyFilter
    search_fields = ["name", "city"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return Pharmacy.objects.all().order_by("-created_at")


class PrescriptionRefillRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionRefillRequestSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PrescriptionRefillRequestFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = PrescriptionRefillRequest.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(prescription_item__prescription__doctor__user=user).order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class PrescriptionsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_prescriptions_dashboard(request.user))
