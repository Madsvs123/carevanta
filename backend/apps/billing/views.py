from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import CanAccessPHI
from .filters import (
    InvoiceFilter, PaymentFilter, RefundFilter, InsuranceClaimFilter,
    DoctorPayoutFilter, DiscountCodeFilter, TransactionHistoryFilter,
)
from .models import Invoice, Payment, Refund, InsuranceClaim, DoctorPayout, DiscountCode, TransactionHistory
from .serializers import (
    InvoiceSerializer, PaymentSerializer, RefundSerializer, InsuranceClaimSerializer,
    DoctorPayoutSerializer, DiscountCodeSerializer, TransactionHistorySerializer, InvoiceDetailSerializer,
)
from .services import get_billing_dashboard, process_payment, send_invoice_reminder, apply_discount


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = InvoiceFilter
    search_fields = ["invoice_number, "notes"]
    ordering_fields = ("created_at", "updated_at", "id", "due_date", "total")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return InvoiceDetailSerializer
        return InvoiceSerializer

    def get_queryset(self):
        qs = Invoice.objects.all().select_related("patient", "doctor", "appointment")
        user = self.request.user
        if user.is_staff and getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(doctor__user=user).order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        invoice = self.get_object()
        payment = process_payment(
            invoice,
            request.data.get("amount", invoice.total),
            method=request.data.get("method", "card"),
        )
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"], url_path="send-reminder")
    def send_reminder(self, request, pk=None):
        return Response(send_invoice_reminder(self.get_object()))

    @action(detail=True, methods=["post"], url_path="apply-discount")
    def apply_discount_code(self, request, pk=None):
        invoice = apply_discount(self.get_object(), request.data.get("code", ""))
        return Response(self.get_serializer(invoice).data)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = PaymentFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = Payment.objects.all().select_related("invoice")
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        if getattr(user, "role", "") == "doctor":
            return qs.filter(invoice__doctor__user=user).order_by("-created_at")
        return qs.filter(invoice__patient=user).order_by("-created_at")


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = RefundFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = Refund.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(payment__invoice__patient=user).order_by("-created_at")


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    serializer_class = InsuranceClaimSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = InsuranceClaimFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = InsuranceClaim.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(patient=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)


class DoctorPayoutViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorPayoutSerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = DoctorPayoutFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = DoctorPayout.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(doctor__user=user).order_by("-created_at")


class DiscountCodeViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountCodeSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = DiscountCodeFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return DiscountCode.objects.all().order_by("-created_at")
        return DiscountCode.objects.none()


class TransactionHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionHistorySerializer
    permission_classes = (CanAccessPHI,)
    filterset_class = TransactionHistoryFilter
    ordering_fields = ("created_at", "updated_at", "id")

    def get_queryset(self):
        qs = TransactionHistory.objects.all()
        user = self.request.user
        if user.is_staff or getattr(user, "role", "") == "admin":
            return qs.order_by("-created_at")
        return qs.filter(user=user).order_by("-created_at")


class BillingDashboardViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response(get_billing_dashboard(request.user))
