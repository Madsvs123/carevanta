from .handlers import OrganizationsWorkflowView, OrganizationsDashboardView, OrganizationsHealthView, OrganizationsBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
  ClinicViewSet, ClinicLocationViewSet, ClinicStaffMemberViewSet,
    StaffInvitationViewSet, OrganizationSettingsViewSet, OrganizationsDashboardViewSet,
)

router = DefaultRouter()
router.register("clinics", ClinicViewSet, basename="clinic")
router.register("locations", ClinicLocationViewSet, basename="clinic-location")
router.register("staff", ClinicStaffMemberViewSet, basename="clinic-staff")
router.register("invitations", StaffInvitationViewSet, basename="staff-invitation")
router.register("settings", OrganizationSettingsViewSet, basename="org-settings")
router.register("dashboard", OrganizationsDashboardViewSet, basename="organizations-dashboard")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", OrganizationsWorkflowView.as_view()),
    path("workflows/bulk/", OrganizationsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", OrganizationsDashboardView.as_view()),
    path("workflows/health/", OrganizationsHealthView.as_view()),
]
