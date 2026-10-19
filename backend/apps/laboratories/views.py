from rest_framework impor viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from apps.accounts.permissions import CanAccessPHI
from .filters import LabOrderFilter, LabTestCatalogFilter, LaboratoryFilter, LabOrderItemFilter, LabResultFilter
from .models import LabOrder, LabTestCatalog, Laboratory, LabOrderItem, LabResult
from .serializers import (
    LabOrderSerializer, LabTestCatalogSerializer, LaboratorySerializer,
    LabOrderItemSerializer, LabResultSerializer, LabOrderDetailSerializer,
)
from .services import get_laboratories_dashboard


class LabOrderViewSet(viewsets.ModelViewSet):
    serializer_class = LabOrderSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = LabOrderFilter
    search_fields = ["order_number", "clinical_notes"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LabOrderDetailSerializer
        return LabOrderSerializer

    def get_queryset(self):
        qs = LabOrder.objects.all().select_related("patient", "ordering_doctor", "laboratory")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(ordering_doctor__user=user).order_by("-created_at")
        return qs.filter(patient_id=0).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-collected")
    def mark_collected(self, request, pk=None):
        order = self.get_object()
        order.status = order.Status.COLLECTED
        order.collected_at = timezone.now()
        order.save(update_fields=["status", "collected_at", "updated_at"])
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="mark-reviewed")
    def mark_reviewed(self, request, pk=None):
        order = self.get_object()
        if hasattr(order.Status, "REVIEWED"):
            order.status = order.Status.REVIEWED
        else:
            order.status = "reviewed"
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


class LabTestCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = LabTestCatalogSerializer
    permission_classes = (AllowAny,)
    filterset_class = LabTestCatalogFilter
    search_fields = ["name", "code", "category"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return LabTestCatalog.objects.all().order_by("-created_at")


class LaboratoryViewSet(viewsets.ModelViewSet):
    serializer_class = LaboratorySerializer
    permission_classes = (AllowAny,)
    filterset_class = LaboratoryFilter
    search_fields = ["name", "city"]
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        return Laboratory.objects.all().order_by("-created_at")


class LabOrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = LabOrderItemSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = LabOrderItemFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = LabOrderItem.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(order__ordering_doctor__user=user).order_by("-created_at")
        return qs.filter(order__patient=user).order_by("-created_at")


class LabResultViewSet(viewsets.ModelViewSet):
    serializer_class = LabResultSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = LabResultFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = LabResult.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(order_item__order__ordering_doctor__user=user).order_by("-created_at")
        return qs.filter(order_item__order__patient=user).order_by("-created_at")


class LaboratoriesDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_laboratories_dashboard(request.user))
