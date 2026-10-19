from .handlers import ConsultationsWorkflowView, ConsultationsDashboardView, ConsultationsHealthView, ConsultationsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultationViewSet, ConsultationMessageViewSet,
    ConsultationNoteViewSet, ConsultationsDashboardViewSet,
)

router = DefaultRouter()
router.register("consultations", ConsultationViewSet, basename="consultations")
router.register("messages", ConsultationMessageViewSet, basename="consultation-messages")
router.register("notes", ConsultationNoteViewSet, basename="consultation-notes")
router.register("dashboard", ConsultationsDashboardViewSet, basename="consultations-dashboard")

urlpatterns = [path("", include(router.urls))]

urlpatterns += [
    path("workflows_x/", ConsultationsWorkflowView.as_view()),
    path("workflows/bulk/", ConsultationsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", ConsultationsDashboardView.as_view()),
    path("workflows/health/", ConsultationsHealthView.as_view()),
]
