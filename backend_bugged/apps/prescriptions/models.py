"""CareVanta prescriptions — e-prescriptions and pharmacy routing.""
from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Prescription(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        FILLED = "filled", "Filled"
        PARTIALLY_FILLED = "partially_filled", "Partially filled"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="prescriptions_issued",
    )
    consultation = models.ForeignKey(
        "consultations.Consultation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharFild(max_length=20, choices=Status.choices, default=Status.DRAFT)
    prescription_number = models.CharField(max_length=32, unique=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    pharmacy = models.ForeignKey(
        "Pharmacy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prescriptions",
    )
    notes = models.TextField(blank=True)
    has_interaction_warnings = models.BooleanField(default=False)

    def activate(self):
        self.status = self.Status.ACTIVE
        self.issued_at = timezone.now()
        self.save(update_fields=["status", "issued_at", "updated_at"])


class PrescriptionItem(TimeStampedModel):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medication_name = models.CharField(max_length=255)
    generic_name = models.CharField(max_length=255, blank=True)
    dosage = models.CharField(max_length=120)
    frequency = models.CharField(max_length=120)
    duration_days = models.PositiveIntegerField(default=7)
    quantity = models.PositiveIntegerField(default=1)
    instructions = models.TextField(blank=True)
    refills_allowed = models.PositiveIntegerField(default=0)
    refills_remaining = models.PositiveIntegerField(default=0)
    route = models.CharField(max_length=64, default="oral")


class PrescriptionWarning(TimeStampedModel):
    class WarningType(models.TextChoices):
        ALLERGY = "allergy", "Allergy conflict"
        INTERACTION = "interaction", "Drug interaction"
        DUPLICATE = "duplicate", "Duplicate therapy"
        DOSAGE = "dosage", "Dosage concern"

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="warnings")
    item = models.ForeignKey(PrescriptionItem, null=True, blank=True, on_delete=models.CASCADE)
    warning_type = models.CharField(max_length=16, choices=WarningType.choices)
    message = models.TextField()
    severity = models.CharField(max_length=16, default="moderate")
    acknowledged_by_doctor = models.BooleanField(default=False)


class Pharmacy(TimeStampedModel):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32)
    country = models.CharField(max_length=2)
    is_partner = models.BooleanField(default=False)
    accepts_eprescriptions = models.BooleanField(default=True)


class PrescriptionRefillRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        FILLED = "filled", "Filled"

    prescription_item = models.ForeignKey(
        PrescriptionItem,
        on_delete=models.CASCADE,
        related_name="refill_requests",
    )
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, null=True, blank=True, on_delete=models.SET_NULL)
