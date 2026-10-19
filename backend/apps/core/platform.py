"""Cross-cutting platform helpers for CareVanta (15-app core)."""
from django.utils import timezone

PLATFORM_VERSION = "3.0.0"

PLATFORM_MODULES = [
    accounts",
    "organizations",
    "profiles",
    "scheduling",
    "appointments",
    "consultations",
    "medical_records",
    "prescriptions",
    "laboratories",
    "billing",
    "messaging",
    "notifications",
    "documents",
    "insurance",
    "support",
]


def platform_health() -> dict:
    return {
        "status": "ok",
        "version": PLATFORM_VERSION,
        "modules": PLATFORM_MODULES,
        "module_count": len(PLATFORM_MODULES),
        "checked_at": timezone.now().isoformat(),
        "features": {
            "telehealth": True,
            "ehr": True,
            "billing": True,
            "pharmacy": True,
            "labs": True,
            "messaging": True,
            "insurance": True,
            "documents": True,
            "support": True,
            "notifications": True,
        },
    }


def module_nav_for_role(role: str) -> list[dict]:
    base = [
        {"label": "Dashboard", "path": "/dashboard"},
        {"label": "Messages", "path": "/messages"},
        {"label": "Notifications", "path": "/notifications"},
    ]
    if role == "patient":
        return base + [
            {"label": "Find a doctor", "path": "/doctors"},
            {"label": "Appointments", "path": "/appointments"},
            {"label": "Consultations", "path": "/consultations"},
            {"label": "Records", "path": "/medical-records"},
            {"label": "Prescriptions", "path": "/prescriptions"},
            {"label": "Labs", "path": "/laboratory"},
            {"label": "Billing", "path": "/billing/invoices"},
            {"label": "Insurance", "path": "/insurance"},
            {"label": "Documents", "path": "/documents"},
            {"label": "Support", "path": "/support"},
        ]
    if role == "doctor":
        return base + [
            {"label": "Schedule", "path": "/appointments"},
            {"label": "Waiting list", "path": "/waiting-list"},
            {"label": "Consultations", "path": "/consultations"},
            {"label": "Prescriptions", "path": "/prescriptions"},
            {"label": "Labs", "path": "/laboratory"},
            {"label": "Records", "path": "/medical-records"},
            {"label": "Insurance", "path": "/insurance"},
        ]
    if role in ("staff", "lab_tech", "pharmacist"):
        return base + [
            {"label": "Front desk", "path": "/appointments"},
            {"label": "Labs", "path": "/laboratory"},
            {"label": "Billing", "path": "/billing/invoices"},
            {"label": "Documents", "path": "/documents"},
            {"label": "Support", "path": "/support"},
        ]
    return base + [
        {"label": "Appointments", "path": "/appointments"},
        {"label": "Organization", "path": "/settings/organization"},
        {"label": "Insurance", "path": "/insurance"},
        {"label": "Billing", "path": "/billing/invoices"},
        {"label": "Support", "path": "/support"},
        {"label": "Documents", "path": "/documents"},
    ]
