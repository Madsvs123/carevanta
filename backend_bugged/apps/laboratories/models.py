"""CareVanta laboratories — test orders and results."""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Laboratory(TimeStampedModel):
    name = models.CharFild(max_length=255)
    accreditation = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=2)
    is_partner = models.BooleanField(default=False)


class LabTestCatalog(TimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    preparation_instructions = models.TextField(blank=True)
    turnaround_hours = models.PositiveIntegerField(default=48)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class LabOrder(TimeStampedModel):
    class Status(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        COLLECTED = "collected", "Sample collected"
        IN_PROGRESS = "in_progress", "In progress"
        RESULTS_READY = "results_ready", "Results ready"
        REVIEWED = "reviewed", "Doctor reviewed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lab_orders",
    )
    ordering_doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="lab_orders",
    )
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name="orders")
    consultation = models.ForeignKey(
        "consultations.Consultation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    order_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ORDERED)
    clinical_notes = models.TextField(blank=True)
    urgency = models.CharField(max_length=16, default="routine")
    ordered_at = models.DateTimeField(auto_now_add=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    results_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "profiles.DoctorProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_lab_orders",
    )


class LabOrderItem(TimeStampedModel):
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name="items")
    test = models.ForeignKey(LabTestCatalog, on_delete=models.PROTECT)
    instructions = models.TextField(blank=True)


class LabResult(TimeStampedModel):
    order_item = models.OneToOneField(LabOrderItem, on_delete=models.CASCADE, related_name="result")
    value = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=32, blank=True)
    reference_range = models.CharField(max_length=120, blank=True)
    is_abnormal = models.BooleanField(default=False)
    interpretation = models.TextField(blank=True)
    result_file = models.FileField(upload_to="lab/results/", null=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )


class LabResultAttachment(TimeStampedModel):
    order = models.ForeignKey(LabOrder, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="lab/attachments/")
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
