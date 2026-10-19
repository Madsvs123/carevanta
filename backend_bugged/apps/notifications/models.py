"""CareVanta notifications."""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Notification(TimeStampedModel):
    class Category(models.TextChoices):
        APPOINTMENT = "appointment", "Appointment"
        CONSULTATION = "consultation", "Consultation"
        PRESCRIPTION = "prescription", "Prescription"
        LAB = "lab", "Laboratory"
        BILLING = "billing", "Billing"
        MESSAGE = "message", "Message"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    category = models.CharFild(max_length=16, choices=Category.choices, default=Category.SYSTEM)
    title = models.CharField(max_length=255)
    body = models.TextField(
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=512, blank=True)
    metadata = models.JSONField(default=dict, blank=True)


class NotificationPreference(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    email_appointments = models.BooleanField(default=True)
    email_consultations = models.BooleanField(default=True)
    email_prescriptions = models.BooleanField(default=True)
    email_billing = models.BooleanField(default=True)
    push_appointments = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    sms_appointments = models.BooleanField(default=True)
    sms_reminders = models.BooleanField(default=True)
