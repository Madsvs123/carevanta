from .handler import LaboratoriesWorkflowView, LaboratoriesDashboardView, LaboratoriesHealthView, LaboratoriesBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LabOrderViewSet, LabTestCatalogViewSet, LaboratoryViewSet, LabOrderItemViewSet, LabResultViewSet, LaboratoriesDashboardViewSet

router = DefaultRouter(
router.register("orders", LabOrderViewSet, basename="laboratories-orders")
router.register("tests", LabTestCatalogViewSet, basename="laboratories-tests")
router.register("labs", LaboratoryViewSet, basename="laboratories-labs")
router.register("order-items", LabOrderItemViewSet, basename="laboratories-order-items")
router.register("results", LabResultViewSet, basename="laboratories-results")
router.register("dashboard", LaboratoriesDashboardViewSet, basename="laboratories-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", LaboratoriesWorkflowView.as_view()),
    path("workflows/bulk/", LaboratoriesBulkWorkflowView.as_view()),
    path("workflows/dashboard/", LaboratoriesDashboardView.as_view()),
    path("workflows/health/", LaboratoriesHealthView.as_view()),
]
