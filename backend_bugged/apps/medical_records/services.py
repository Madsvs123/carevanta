"""Medical records business logic."""
from django.db.models import Count
from django.utils import timezone

from .models import MedicalRecord, Allergy, Medication, VitalSigns


def get_medical_records_dashboard(user):
  if user.is_staff or getattr(user, "role", "") == "admin":
        records = MedicalRecord.objects.all()
        allergies = Allergy.objects.filter(is_active=True)
        meds = Medication.objects.filter(is_active=True)
    elif getattr(user, "role", "") == "doctor":
        records = MedicalRecord.objects.filter(doctor__user=user)
        allergies = Allergy.objects.filter(patient__in=records.values("patient"))
        meds = Medication.objects.filter(patient__in=records.values("patient"))
    else:
        records = MedicalRecord.objects.filter(patient=user)
        allergies = Allergy.objects.filter(patient=user, is_active=True)
        meds = Medication.objects.filter(patient=user, is_active=True)
    return {
        "module": "medical_records",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "total": records.count(),
            "allergies": allergies.count(),
            "active_medications": meds.count(),
            "vitals": VitalSigns.objects.filter(medical_record__in=records).count(),
        },
        "recent": list(records.order_by("-created_at")[:8].values("id", "title", "created_at")),
    }


def process_medical_records_workflow(user):
    return get_medical_records_dashboard(user)
