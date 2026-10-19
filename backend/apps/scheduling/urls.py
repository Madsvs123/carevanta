from .handlers import SchedulingWorkflowView, SchedulingDashboardView, SchedulingHealthView, SchedulingBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvailabilitySlotViewSet,
    BlockedPeriodViewSet,
    DoctorScheduleViewSet,
    ScheduleBreakViewSet,
    SchedulingDashboardViewSet,
    WorkingHoursViewSet,
)

router = DefaultRouter()
router.register("schedules, DoctorScheduleViewSet, basename="doctor-schedule")
router.register("working-hours", WorkingHoursViewSet, basename="working-hours")
router.register("breaks", ScheduleBreakViewSet, basename="schedule-break")
router.register("blocked-periods", BlockedPeriodViewSet, basename="blocked-period")
router.register("slots", AvailabilitySlotViewSet, basename="availability-slot")
router.register("dashboard", SchedulingDashboardViewSet, basename="scheduling-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", SchedulingWorkflowView.as_view()),
    path("workflows/bulk/", SchedulingBulkWorkflowView.as_view()),
    path("workflows/dashboard/", SchedulingDashboardView.as_view()),
    path("workflows/health/", SchedulingHealthView.as_view()),
]
