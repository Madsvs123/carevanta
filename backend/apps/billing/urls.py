from .handlers import BillingWorkflowView, BillingDashboardView, BillingHealthView, BillingBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, PaymentViewSet, RefundViewSet, InsuranceClaimViewSet, DoctorPayoutViewSet, DiscountCodeViewSet, TransactionHistoryViewSet, BillingDashboardViewSet

router = DefaultRouter()
router.register("invoices", InvoiceViewSet, basename="billing-invoices")
router.register("payments", PaymentViewSet, basename="billing-payments")
router.register("refunds", RefundViewSet, basename="billing-refunds")
router.register("insurance-claims", InsuranceClaimViewSet, basename="billing-insurance-claims")
router.register("payouts", DoctorPayoutViewSet, basename="billing-payouts")
router.register("discount-codes", DiscountCodeViewSet, basename="billing-discount-codes")
router.register("transactions", TransactionHistoryViewSet, basename="billing-transactions")
router.register("dashboard", BillingDashboardViewSet, basename="billing-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", BillingWorkflowView.as_view()),
    path("workflows/bulk/", BillingBulkWorkflowView.as_view()),
    path("workflows/dashboard/", BillingDashboardView.as_view()),
    path("workflows/health/", BillingHealthView.as_view()),
]
