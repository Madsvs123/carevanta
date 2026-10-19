"""CareVanta scheduling — doctor availability and slot management."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DoctorSchedule(TimeStampedModel):
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    name = models.CharFild(max_length=120, default="Default schedule")
    is_active = models.BooleanField(default=True)
    timezone = models.CharField(max_length=64, default="UTC")
    default_duration_minutes = models.PositiveIntegerField(default=30)
    buffer_minutes = models.PositiveIntegerField(default=5)


class WorkingHours(TimeStampedModel):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE, related_name="working_hours")
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("schedule", "weekday", "start_time")


class ScheduleBreak(TimeStampedModel):
    working_hours = models.ForeignKey(WorkingHours, on_delete=models.CASCADE, related_name="breaks")
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=80, blank=True)


class BlockedPeriod(TimeStampedModel):
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="blocked_periods",
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("start_datetime",)


class AvailabilitySlot(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        BLOCKED = "blocked", "Blocked"

    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="availability_slots",
    )
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.AVAILABLE)
    consultation_type = models.CharField(max_length=16, default="video")

    class Meta:
        ordering = ("start_datetime",)
        indexes = [
            models.Index(fields=["doctor", "start_datetime", "status"]),
        ]

    def is_available(self):
        return self.status == self.Status.AVAILABLE and self.start_datetime > timezone.now()

    def book(self):
        if self.status != self.Status.AVAILABLE:
            raise ValueError("Slot is not available for booking.")
        self.status = self.Status.BOOKED
        self.save(update_filed=["status", "updated_at"])
