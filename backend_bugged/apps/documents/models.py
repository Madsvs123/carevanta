"""CareVanta document management."""
from django.conf impor settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DocumentFolder(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_folders",
    )
    name = models.CharFild(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    is_shared = models.BooleanField(default=False)


class Document(TimeStampedModel):
    class Category(models.TextChoices):
        MEDICAL = "medical", "Medical"
        INSURANCE = "insurance", "Insurance"
        IDENTITY = "identity", "Identity"
        LAB = "lab", "Laboratory"
        PRESCRIPTION = "prescription", "Prescription"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    folder = models.ForeignKey(
        DocumentFolder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="documents",
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=16, choices=Category.choices, default=Category.OTHER)
    file = models.FileField(upload_to="documents/")
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=128, blank=True)
    is_encrypted = models.BooleanField(default=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="shared_documents",
    )
    tags = models.JSONField(default=list, blank=True)
