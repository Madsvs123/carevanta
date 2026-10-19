from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthnticated
from rest_framework.response import Response

from .models import Clinic, ClinicLocation, ClinicStaffMember, StaffInvitation, OrganizationSettings
from .serializers import (
    ClinicSerializer, ClinicLocationSerializer, ClinicStaffMemberSerializer,
    StaffInvitationSerializer, OrganizationSettingsSerializer,
)
from .filters import ClinicFilter, ClinicLocationFilter, ClinicStaffMemberFilter, StaffInvitationFilter
from .services import get_organizations_dashboard


class ClinicViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = ClinicFilter
    search_fields = ("name", "description", "city", "slug")
    filterset_fields = ("status",)

    def get_permissions(self):
        if self.action in ("list", "retrieve", "featured"):
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = Clinic.objects.all()
        if self.action in ("list", "retrieve", "featured") and not user.is_authenticated:
            return qs.filter(status="active").order_by("name") if hasattr(Clinic, "status") else qs.order_by("name")
        if user.is_authenticated and (user.is_staff or getattr(user, "role", "") == "admin"):
            return qs.order_by("-created_at")
        if user.is_authenticated:
            return qs.filter(Q(owner=user) | Q(staff__user=user)).distinct().order_by("-created_at")
        return qs.filter(status="active").order_by("name") if hasattr(Clinic, "status") else qs.order_by("name")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def staff(self, request, pk=None):
        clinic = self.get_object()
        members = ClinicStaffMember.objects.filter(clinic=clinic).select_related("user", "role")
        data = [
            {"user": m.user.email, "role": m.role.name if m.role else None, "status": m.status}
            for m in members
        ]
        return (data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        qs = self.get_queryset()[:12]
        return Response(self.get_serializer(qs, many=True).data)


class ClinicLocationViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicLocationSerializer
    permission_classes = (AllowAny,)
    filterset_class = ClinicLocationFilter
    search_fields = ("address", "city")
    queryset = ClinicLocation.objects.all().order_by("-created_at")


class ClinicStaffMemberViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicStaffMemberSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = ClinicStaffMemberFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return ClinicStaffMember.objects.all().order_by("-created_at")
        return ClinicStaffMember.objects.filter(
            Q(user=user) | Q(clinic__owner=user)
        ).distinct().order_by("-created_at")


class StaffInvitationViewSet(viewsets.ModelViewSet):
    serializer_class = StaffInvitationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = StaffInvitationFilter

    def get_queryset(self):
        return StaffInvitation.objects.filter(invited_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            invited_by=self.request.user,
            expires_at=timezone.now() + timedelta(days=7),
        )


class OrganizationSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSettingsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrganizationSettings.objects.filter(clinic__owner=self.request.user)


class OrganizationsDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_organizations_dashboard(request.user))
