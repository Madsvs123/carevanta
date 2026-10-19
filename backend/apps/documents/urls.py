from .handlers import DocumentsWorkflowView, DocumentsDashboardView, DocumentsHealthView, DocumentsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentFolderViewSet, DocumentViewSet, DocumentsDashboardViewSet

router = DefaultRouter()
router.register("folders", DocumentFolderViewSet, basename="documents-folders")
router.register("documents", DocumentViewSet, basename="documents-documents")
router.register("dashboard", DocumentsDashboardViewSet, basename="documents-dashboard")

urlpatterns = [
  path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", DocumentsWorkflowView.as_view()),
    path("workflows/bulk/", DocumentsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", DocumentsDashboardView.as_view()),
    path("workflows/health/", DocumentsHealthView.as_view()),
]
