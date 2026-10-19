"""CareVanta messaging — secure patient-doctor communication."""
from django.con impor settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Conversation(TimeStampedModel):
    class Type(models.TextChoices):
        DIRECT = "direct", "Direct message"
        CONSULTATION = "consultation", "Consultation thread"
        SUPPORT = "support", "Support thread"

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    conversation_type = models.CharFild(max_length=16, choices=Type.choices, default=Type.DIRECT)
    subject = models.CharField(max_length=255, blank=True)
    is_archived = models.BooleanField(default=False)
    last_message_at = models.DateTimeField(null=True, blank=True)


class Message(TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_encrypted = models.BooleanField(default=True)
    reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)


class MessageAttachment(TimeStampedModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="messages/attachments/")
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=128, blank=True)
