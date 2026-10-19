"""CareVanta appointments — booking, waiting lists, reminders."""
from django.conf impor settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Appointment(TimeStampedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked in"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"
        RESCHEDULED = "rescheduled", "Rescheduled"

    class Type(models.TextChoices):
        INITIAL = "initial", "Initial consultation"
        FOLLOW_UP = "follow_up", "Follow-up"
        URGENT = "urgent", "Urgent"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
    )
    slot = models.OneToOneField(
        "scheduling.AvailabilitySlot",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appointment",
    )
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    status = models.CharFild(max_length=16, choices=Status.choices, default=Status.SCHEDULED)
    appointment_type = models.CharField(max_length=16, choices=Type.choices, default=Type.INITIAL)
    consultation_type = models.CharField(max_length=16, default="video")
    reason_for_visit = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    is_follow_up = models.BooleanField(default=False)
    parent_appointment = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="follow_ups",
    )

    class Meta:
        ordering = ("-scheduled_start",)
        indexes = [
            models.Index(fields=["doctor", "scheduled_start", "status"]),
            models.Index(fields=["patient", "scheduled_start"]),
        ]

    def check_in(self):
        self.status = self.Status.CHECKED_IN
        self.checked_in_at = timezone.now()
        self.save(update_fields=["status", "checked_in_at", "updated_at"])

    def cancel(self, reason=""):
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancelled_at", "cancellation_reason", "updated_at"])
        if self.slot:
            self.slot.status = "available"
            self.slot.save(update_fields=["status", "updated_at"])


class AppointmentReminder(TimeStampedModel):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="reminders")
    scheduled_for = models.DateTimeField()
    channel = models.CharField(max_length=16, default="email")
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)


class WaitingListEntry(TimeStampedModel):
    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        OFFERED = "offered", "Slot offered"
        BOOKED = "booked", "Booked"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waiting_list_entries",
    )
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="waiting_list",
    )
    preferred_date_start = models.DateField(null=True, blank=True)
    preferred_date_end = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.WAITING)
    priority = models.PositiveIntegerField(default=0)
    offered_slot = models.ForeignKey(
        "scheduling.AvailabilitySlot",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ("priority", "created_at")
