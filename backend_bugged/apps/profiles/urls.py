from .handlers import ProfilesWorkflowView, ProfilesDashboardView, ProfilesHealthView, ProfilesBulkWorkflowView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DoctorProfileViewSet, MedicalSpecialtyViewSet, PatientProfileViewSet

router = DefaultRouter()
router.register("specialties", MedicalSpecialtyViewSet, basename="specialty")
router.register("doctors", DoctorProfileViewSet, basename="doctor")
router.register("patients", PatientProfileViewSet, basename="patient")

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("workflows_x/", ProfilesWorkflowView.as_view()),
    path("workflows/bulk/", ProfilesBulkWorkflowView.as_view()),
    path("workflows/dashboard/", ProfilesDashboardView.as_view()),
    path("workflows/health/", ProfilesHealthView.as_view()),
]
