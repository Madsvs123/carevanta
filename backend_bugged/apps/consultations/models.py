"""CareVanta consultations — video sessions, chat, notes, waiting rooms."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Consultation(TimeStampedModel):
    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting room"
        READY = "ready", "Ready to start"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        CONNECTION_ISSUE = "connection_issue", "Connection issue"

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="consultation",
    )
    status = models.CharFild(max_length=20, choices=Status.choices, default=Status.WAITING)
    room_id = models.CharField(max_length=64, unique=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    patient_joined_at = models.DateTimeField(null=True, blank=True)
    doctor_joined_at = models.DateTimeField(null=True, blank=True)
    connection_quality = models.CharField(max_length=32, blank=True)
    recording_enabled = models.BooleanField(default=False)
    webrtc_session_id = models.CharField(max_length=128, blank=True)

    def start(self):
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])

    def complete(self):
        self.status = self.Status.COMPLETED
        self.ended_at = timezone.now()
        self.save(update_fields=["status", "ended_at", "updated_at"])


class VirtualWaitingRoom(TimeStampedModel):
    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="waiting_room",
    )
    patient_queue_position = models.PositiveIntegerField(default=1)
    estimated_wait_minutes = models.PositiveIntegerField(default=0)
    doctor_ready = models.BooleanField(default=False)
    patient_ready = models.BooleanField(default=False)


class ConsultationMessage(TimeStampedModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=16, default="text")
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to="consultations/attachments/", null=True, blank=True)


class ConsultationNote(TimeStampedModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subjective = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    assessment = models.TextField(blank=True)
    plan = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)


class ConsultationFile(TimeStampedModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to="consultations/files/")
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=64, blank=True)
    file_size = models.PositiveIntegerField(default=0)


class ConnectionStatusLog(TimeStampedModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="connection_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.CharField(max_length=32)
    quality_score = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
