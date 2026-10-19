import django_filters
from .models import MedicalRecord, VitalSigns, Allergy, Medication, MedicalHistoryEntry, Referral


class MedicalRecordFilter(django_filters.FilterSet):
    class Meta:
        model = MedicalRecord
        fields = ["status"] if hasattr(MedicalRecord, status") else []


class VitalSignsFilter(django_filters.FilterSet):
    class Meta:
        model = VitalSigns
        fields = []


class AllergyFilter(django_filters.FilterSet):
    class Meta:
        model = Allergy
        fields = ["is_active", "severity"] if hasattr(Allergy, "severity") else ["is_active"]


class MedicationFilter(django_filters.FilterSet):
    class Meta:
        model = Medication
        fields = ["is_active"]


class MedicalHistoryEntryFilter(django_filters.FilterSet):
    class Meta:
        model = MedicalHistoryEntry
        fields = []


class ReferralFilter(django_filters.FilterSet):
    class Meta:
        model = Referral
        fields = ["status"] if hasattr(Referral, "status") else []
