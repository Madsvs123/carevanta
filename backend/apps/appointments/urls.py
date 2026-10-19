from .handlers import AppointmentsWorkflowView, AppointmentsDashboardView, AppointmentsHealthView, AppointmentsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet, AppointmentReminderViewSet,
    WaitingListEntryViewSet, AppointmentsDashboardViewSet,
)

router = DefaultRouter()
router.register("appointments", AppointmentViewSet, basename="appointments")
router.register("reminders", AppointmentReminderViewSet, basename="appointment-reminders")
router.register("waiting-list", WaitingListEntryViewSet, basename="waiting-list")
router.register("dashboard", AppointmentsDashboardViewSet, basename="appointments-dashboard")

urlpatterns = [path("", include(router.urls))]

urlpatterns += [
    path("workflows_x/", AppointmentsWorkflowView.as_view()),
    path("workflows/bulk/", AppointmentsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", AppointmentsDashboardView.as_view()),
    path("workflows/health/", AppointmentsHealthView.as_view()),
]
