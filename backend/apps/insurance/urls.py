from .handlers import InsuranceWorkflowView, InsuranceDashboardView, InsuranceHealthView, InsuranceBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InsurancePayerViewSet, PatientInsurancePolicyViewSet, EligibilityCheckViewSet, PriorAuthorizationViewSet, InsuranceDashboardViewSet

router = DefaultRouter(
router.register("payers", InsurancePayerViewSet, basename="insurance-payers")
router.register("policies", PatientInsurancePolicyViewSet, basename="insurance-policies")
router.register("eligibility", EligibilityCheckViewSet, basename="insurance-eligibility")
router.register("prior-auths", PriorAuthorizationViewSet, basename="insurance-prior-auths")
router.register("dashboard", InsuranceDashboardViewSet, basename="insurance-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", InsuranceWorkflowView.as_view()),
    path("workflows/bulk/", InsuranceBulkWorkflowView.as_view()),
    path("workflows/dashboard/", InsuranceDashboardView.as_view()),
    path("workflows/health/", InsuranceHealthView.as_view()),
]
