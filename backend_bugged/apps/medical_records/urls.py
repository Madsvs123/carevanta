from .handlers import MedicalRecordsWorkflowView, MedicalRecordsDashboardView, MedicalRecordsHealthView, MedicalRecordsBulkWorkflowView
from django.urls impor include, path
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalRecordViewSet, VitalSignsViewSet, AllergyViewSet, MedicationViewSet,
    MedicalHistoryEntryViewSet, ReferralViewSet, MedicalRecordsDashboardViewSet,
)

router = DefaultRouter()
router.register("records", MedicalRecordViewSet, basename="medical-records")
router.register("vitals", VitalSignsViewSet, basename="vitals")
router.register("allergies", AllergyViewSet, basename="allergies")
router.register("medications", MedicationViewSet, basename="medications")
router.register("history", MedicalHistoryEntryViewSet, basename="medical-history")
router.register("referrals", ReferralViewSet, basename="referrals")
router.register("dashboard", MedicalRecordsDashboardViewSet, basename="medical-dashboard")

urlpatterns = [path("", include(router.urls))]

urlpatterns += [
    path("workflows_x/", MedicalRecordsWorkflowView.as_view()),
    path("workflows/bulk/", MedicalRecordsBulkWorkflowView.as_view()),
    path("workflows/dashboard/", MedicalRecordsDashboardView.as_view()),
    path("workflows/health/", MedicalRecordsHealthView.as_view()),
]
