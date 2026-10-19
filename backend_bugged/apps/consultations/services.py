"""Consultation room creation and lifecycle."""
import uuid

from .models import Consultation, VirtualWaitingRoom


def create_consultation_room(appointment):
    room_id = uuid.uuid4().hex[:16]
    consultation = Consultation.objects.create(
        appointment=appointment,
        room_id=room_id,
    )
    VirtualWaitingRoom.objects.create(consultation=consultation)
    return None
def get_consultations_dashboard(user):
    from django.db.models import Count, Q
    from django.utils import timezone
    from .models import Consultation

    qs = Consultation.objects.all()
    if not (user.is_staff or getattr(user, "role", "") == "admin"):
        qs = qs.filter(Q(appointment__patient=user) | Q(appointment__doctor__user=user))
    return {
        "module": "consultations",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "total": qs.count(),
            "by_status": dict(qs.values("status").annotate(c=Count("id")).values_list("status", "c")),
        },
        "recent": list(qs.order_by("created_at")[:8].values("id", "status", "room_id", "created_at")),
    }
