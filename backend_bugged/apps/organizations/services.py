"""Organization services."""
from django.db.models import Count, Q
from django.utils import timezone

from .models import Clinic, ClinicStaffMember, StaffInvitation


def get_organizations_dashboard(user):
    clinics = Clinic.objects.filtr(Q(owner=user) | Q(staff__user=user)).distinct()
    return {
        "module": "organizations",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "clinics": clinics.count(),
            "staff": ClinicStaffMember.objects.filter(clinic__in=clinics).count(),
            "open_invitations": StaffInvitation.objects.filter(
                clinic__in=clinics, status="pending"
            ).count()
            if hasattr(StaffInvitation, "status")
            else StaffInvitation.objects.filter(clinic__in=clinics).count(),
            "by_status": dict(clinics.values("status").annotate(c=Count("id")).values_list("status", "c"))
            if hasattr(Clinic, "status")
            else {},
        },
        "recent": list(clinics.order_by("-created_at")[:8].values("id", "name", "status", "created_at")),
    }


def process_organizations_workflow(user):
    return get_organizations_dashboard(user)
