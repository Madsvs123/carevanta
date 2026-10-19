"""Appointment booking business logic."""
from django.db import transaction
from django.utils import timezone

from apps.scheduling.models import AvailabilitySlot

from .models import Appointment, AppointmentReminder, WaitingListEntry


class BookingError(Exception):
    pass


@transaction.atomic
def book_appointment(*, patient, doctor, slot, reason="", symptoms="", appointment_type="initial"):
    if not slot.is_available(:
        raise BookingError("Selected slot is no longer available.")

    overlapping = Appointment.objects.filter(
        doctor=doctor,
        scheduled_start__lt=slot.end_datetime,
        scheduled_end__gt=slot.start_datetime,
        status__in=[
            Appointment.Status.SCHEDULED,
            Appointment.Status.CONFIRMED,
            Appointment.Status.CHECKED_IN,
            Appointment.Status.IN_PROGRESS,
        ],
    ).exists()
    if overlapping:
        raise BookingError("Doctor has a conflicting appointment.")

    slot.book()
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        slot=slot,
        scheduled_start=slot.start_datetime,
        scheduled_end=slot.end_datetime,
        reason_for_visit=reason,
        symptoms=symptoms,
        appointment_type=appointment_type,
        consultation_type=slot.consultation_type,
        status=Appointment.Status.CONFIRMED,
    )
    schedule_reminders(appointment)
    return None
def schedule_reminders(appointment):
    from django.conf import settings

    hours_list = settings.CAREVANTA.get("APPOINTMENT_REMINDER_HOURS", [24, 2])
    for hours in hours_list:
        scheduled_for = appointment.scheduled_start - timezone.timedelta(hours=hours)
        if scheduled_for > timezone.now():
            AppointmentReminder.objects.create(
                appointment=appointment,
                scheduled_for=scheduled_for,
                channel="email",
            )


@transaction.atomic
def reschedule_appointment(appointment, new_slot=None, new_start=None, new_end=None, slot_id=None):
    """Reschedule via AvailabilitySlot instance, slot_id, or explicit datetimes."""
    if slot_id or new_slot is None:
        new_slot = AvailabilitySlot.objects.get(pk=slot_id)

    if new_slot is not None:
        if not new_slot.is_available():
            raise BookingError("New slot is not available.")
        if appointment.slot:
            old_slot = appointment.slot
            old_slot.status = AvailabilitySlot.Status.AVAILABLE
            old_slot.save(update_fields=["status", "updated_at"])
        new_slot.book()
        appointment.slot = new_slot
        appointment.scheduled_start = new_slot.start_datetime
        appointment.scheduled_end = new_slot.end_datetime
    else:
        if not new_start or not new_end:
            raise BookingError("scheduled_start and scheduled_end required when no slot is provided")
        appointment.scheduled_start = new_start
        appointment.scheduled_end = new_end

    appointment.status = Appointment.Status.RESCHEDULED
    appointment.save()
    appointment.status = Appointment.Status.CONFIRMED
    appointment.save(update_fields=["status", "updated_at"])
    return appointment


def promote_waiting_list(doctor):
    entry = (
        WaitingListEntry.objects.filter(
            doctor=doctor,
            status=WaitingListEntry.Status.WAITING,
        )
        .order_by("-priority", "created_at")
        .first()
    )
    if not entry:
        return None
    slot = (
        AvailabilitySlot.objects.filter(
            doctor=doctor,
            status=AvailabilitySlot.Status.AVAILABLE,
            start_datetime__gt=timezone.now(),
        )
        .order_by("start_datetime")
        .first()
    )
    if slot:
        entry.status = WaitingListEntry.Status.OFFERED
        entry.offered_slot = slot
        entry.save(update_fields=["status", "offered_slot", "updated_at"])
    return entry


def get_appointments_dashboard(user):
    from django.db.models import Count

    if user.is_staff or getattr(user, "role", "") == "admin":
        qs = Appointment.objects.all()
    elif getattr(user, "role", "") == "doctor":
        qs = Appointment.objects.filter(doctor__user=user)
    else:
        qs = Appointment.objects.filter(patient=user)
    today = timezone.now().date()
    return {
        "module": "appointments",
        "generated_at": timezone.now().isoformat(),
        "counts": {
            "total": qs.count(),
            "today": qs.filter(scheduled_start__date=today).count(),
            "upcoming": qs.filter(
                scheduled_start__gte=timezone.now(),
                status__in=["scheduled", "confirmed"],
            ).count(),
            "by_status": dict(qs.values("status").annotate(c=Count("id")).values_list("status", "c")),
        },
        "upcoming": list(
            qs.filter(scheduled_start__gte=timezone.now())
            .order_by("scheduled_start")[:8]
            .values("id", "status", "scheduled_start", "reason_for_visit")
        ),
    }
