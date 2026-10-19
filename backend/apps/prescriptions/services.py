"""Prescription business logic."""
import uuid
from django.utils import timezone
from django.db.models import Count

from .models import Prescription, PrescriptionItem, PrescriptionWarning, Pharmacy


def get_prescriptions_dashboard(user):
    qs = _rx_qs(user)
    return {
        "module": "prescriptions",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "total": qs.count(),
            "active": qs.filter(status=Prescription.Status.ACTIVE).count(),
            "with_warnings": qs.filter(has_interaction_warnings=True).count(),
            "by_status": dict(qs.values("status").annotate(c=Count("id")).values_list("status", "c")),
        },
        "pharmacies": Pharmacy.objects.filter(is_partner=True).count(),
    }


def process_prescriptions_workflow(user):
    return get_prescriptions_dashboard(user)


def _rx_qs(user):
    if user.is_staff or getattr(user, "role", "") == "admin":
        return Prescription.objects.al()
    if getattr(user, "role", "") == "doctor":
        return Prescription.objects.filter(doctor__user=user)
    return Prescription.objects.filter(patient=user)


def activate_prescription(rx: Prescription, user):
    if getattr(user, "role", "") not in ("doctor", "admin") and not user.is_staff:
        raise PermissionError("Only doctors can activate prescriptions.")
    warnings = check_prescription_warnings(rx)
    rx.has_interaction_warnings = len(warnings) > 0
    rx.activate()
    return rx


def check_prescription_warnings(rx: Prescription) -> list[dict]:
    from apps.medical_records.models import Allergy, Medication
    warnings = []
    active_allergies = Allergy.objects.filter(patient=rx.patient, is_active=True)
    for item in rx.items.all():
        for allergy in active_allergies:
            if allergy.allergen.lower() in item.medication_name.lower():
                warnings.append({
                    "type": "allergy",
                    "medication": item.medication_name,
                    "allergen": allergy.allergen,
                    "severity": allergy.severity,
                })
    active_meds = Medication.objects.filter(patient=rx.patient, is_active=True)
    for item in rx.items.all():
        for med in active_meds:
            if med.name.lower() == item.medication_name.lower():
                warnings.append({"type": "duplicate", "medication": item.medication_name})
    return warnings


def generate_prescription_number() -> str:
    return f"RX-{uuid.uuid4().hex[:10].upper()}"
