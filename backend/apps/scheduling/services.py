"""Business logic for scheduling — slot generation and dashboards."""
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone

from .models import AvailabilitySlot, BlockedPeriod, DoctorSchedule, WorkingHours


def generate_slots_for_doctor(doctor, days: int = 14, consultation_type: str = "video") -> int:
  """Materialize availability slots from active schedules for the next N days."""
    schedule = (
        DoctorSchedule.objects.filtr(doctor=doctor, is_active=True)
        .prefetch_related("working_hours__breaks")
        .first()
    )
    if not schedule:
        return 0

    duration = timedelta(minutes=schedule.default_duration_minutes or 30)
    buffer = timedelta(minutes=schedule.buffer_minutes or 0)
    created = 0
    today = timezone.localdate()

    for offset in range(max(1, int(days))):
        day = today + timedelta(days=offset)
        weekday = day.weekday()
        hours = [wh for wh in schedule.working_hours.all() if wh.weekday == weekday]
        for wh in hours:
            start_dt = timezone.make_aware(datetime.combine(day, wh.start_time))
            end_dt = timezone.make_aware(datetime.combine(day, wh.end_time))
            breaks = list(wh.breaks.all())
            cursor = start_dt
            while cursor + duration <= end_dt:
                slot_end = cursor + duration
                in_break = any(
                    timezone.make_aware(datetime.combine(day, b.start_time))
                    < slot_end
                    and timezone.make_aware(datetime.combine(day, b.end_time)) > cursor
                    for b in breaks
                )
                blocked = BlockedPeriod.objects.filter(
                    doctor=doctor, start_datetime__lt=slot_end, end_datetime__gt=cursor
                ).exists()
                if not in_break and not blocked:
                    _, was_created = AvailabilitySlot.objects.get_or_create(
                        doctor=doctor,
                        start_datetime=cursor,
                        end_datetime=slot_end,
                        defaults={
                            "duration_minutes": schedule.default_duration_minutes,
                            "status": AvailabilitySlot.Status.AVAILABLE,
                            "consultation_type": consultation_type,
                        },
                    )
                    if was_created:
                        created += 1
                cursor = slot_end + buffer
    return created


def process_scheduling_workflow(user, payload: dict | None = None):
    payload = payload or {}
    summary = {"timestamp": timezone.now().isoformat(), "counts": {}}
    qs = DoctorSchedule.objects.al()
    if getattr(user, "role", "") == "doctor":
        qs = qs.filter(doctor__user=user)
    summary["counts"]["schedules"] = qs.count()
    summary["counts"]["open_slots"] = AvailabilitySlot.objects.filter(
        status=AvailabilitySlot.Status.AVAILABLE, start_datetime__gte=timezone.now()
    ).count()
    if payload.get("doctor_id") and payload.get("action") == "generate":
        from apps.profiles.models import DoctorProfile

        doctor = DoctorProfile.objects.get(pk=payload["doctor_id"])
        summary["generated"] = generate_slots_for_doctor(doctor, int(payload.get("days", 14)))
    return summary


def validate_scheduling_access(user, instance) -> bool:
    if user.is_staff or getattr(user, "role", "") == "admin":
        return True
    if hasattr(instance, "doctor") and getattr(user, "role", "") == "doctor":
        return instance.doctor.user_id == user.id
    return False
