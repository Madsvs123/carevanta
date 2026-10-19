from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import CanAccessPHI
from .filters import InsurancePayerFilter, PatientInsurancePolicyFilter, EligibilityCheckFilter, PriorAuthorizationFilter
from .models import EligibilityCheck, InsurancePayer, PatientInsurancePolicy, PriorAuthorization
from .serializers import (
    EligibilityCheckSerializer, InsurancePayerSerializer,
    PatientInsurancePolicySerializer, PriorAuthorizationSerializer,
)
from .services import (
    decide_prior_auth, get_insurance_dashboard, process_insurance_workflow,
    run_eligibility, submit_prior_auth, verify_policy,
)


class InsurancePayerViewSet(viewsets.ModelViewSet):
    serializer_class = InsurancePayerSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = InsurancePayerFilter
    search_fields = ("name", "payer_code")
    ordering_fields = ("name", "created_at", "id")

    def get_queryset(self):
        qs = InsurancePayer.objects.all().order_by("name")
        if self.request.query_params.get("active") == "1":
            qs = qs.filter(is_active=True)
        return qs


class PatientInsurancePolicyViewSet(viewsets.ModelViewSet):
    serializer_class = PatientInsurancePolicySerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PatientInsurancePolicyFilter
    search_fields = ("member_id", "plan_name", "group_number")
    ordering_fields = ("effective_from", "created_at", "id")

    def get_queryset(self):
        user = None
        qs = PatientInsurancePolicy.objects.select_related("payer", "patient")
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=serializer.validated_data.get("patient") or self.request.user)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        return Response(PatientInsurancePolicySerializer(verify_policy(self.get_object())).data)


class EligibilityCheckViewSet(viewsets.ModelViewSet):
    serializer_class = EligibilityCheckSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = EligibilityCheckFilter
    ordering_fields = ("checked_at", "created_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = EligibilityCheck.objects.select_related("policy", "policy__payer")
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(policy__patient=user).order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="run")
    def run_check(self, request, pk=None):
        return Response(EligibilityCheckSerializer(run_eligibility(self.get_object())).data)


class PriorAuthorizationViewSet(viewsets.ModelViewSet):
    serializer_class = PriorAuthorizationSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PriorAuthorizationFilter
    search_fields = ("service_code", "service_description", "authorization_number")
    ordering_fields = ("created_at", "id")

    def get_queryset(self):
        user = self.request.user
        qs = PriorAuthorization.objects.select_related("policy", "patient")
        if user.is_staff or getattr(user, "role", "") in ("admin", "doctor"):
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(
            patient=serializer.validated_data.get("patient") or self.request.user,
            requested_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        return Response(PriorAuthorizationSerializer(submit_prior_auth(self.get_object())).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return Response(PriorAuthorizationSerializer(decide_prior_auth(self.get_object(), True)).data)

    @action(detail=True, methods=["post"])
    def deny(self, request, pk=None):
        return Response(
            PriorAuthorizationSerializer(
                decide_prior_auth(self.get_object(), False, request.data.get("reason", ""))
            ).data
        )


class InsuranceDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_insurance_dashboard(request.user))

    @action(detail=False, methods=["post"], url_path="run-workflow")
    def run_workflow(self, request):
        return Response(process_insurance_workflow(request.user, request.data))
