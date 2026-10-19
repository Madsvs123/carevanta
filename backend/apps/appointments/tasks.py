from django.utils import timezone

from .models import AppointmentReminder


def send_appointment_reminders():
    due = AppointmentReminder.objects.filter(is_sent=False, scheduled_for__lte=timezone.now())
    count = 0
    for reminder in due.select_related("appointment", "appointment__patient"):
        from django.core.mail import send_mail
        from django.conf import settings

        appt = reminder.appointment
        send_mail(
            subject="CareVanta appointment reminder",
            message=f"Reminder: appointment with {appt.doctor} at {appt.scheduled_start}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appt.patient.email],
            fail_silently=True,
        )
        reminder.is_sent = True
        reminder.sent_at = timezone.now()
        reminder.save(update_fields=["is_sent", "sent_at", "updated_at"])
        count += 1
    return count


def sync_appointments_data(record_id: int) -> int:
    return record_id
