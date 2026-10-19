from .handlers import PrescriptionsWorkflowView, PrescriptionsDashboardView, PrescriptionsHealthView, PrescriptionsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrescriptionViewSet, PrescriptionItemViewSet, PrescriptionWarningViewSet, PharmacyViewSet, PrescriptionRefillRequestViewSet, PrescriptionsDashboardViewSet

router = DefaultRouter()
router.register("prescriptions", PrescriptionViewSet, basename="prescriptions-prescriptions")
router.register("items", PrescriptionItemViewSet, basename="prescriptions-items")
router.register("warnings", PrescriptionWarningViewSet, basename="prescriptions-warnings")
router.register("pharmacies", PharmacyViewSet, basename="prescriptions-pharmacies")
router.register("refill-requests", PrescriptionRefillRequestViewSet, basename="prescriptions-refill-requests")
router.register("dashboard", PrescriptionsDashboardViewSet, basename="prescriptions-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", PrescriptionsWorkflowView.as_view()),
    path("workflows/bulk/", PrescriptionsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", PrescriptionsDashboardView.as_view()),
    path("workflows/health/", PrescriptionsHealthView.as_view()),
]
