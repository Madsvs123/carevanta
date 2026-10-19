"""CareVanta medical records — EMR, vitals, allergies, history."""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MedicalRecord(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_records",
    )
    consultation = models.ForeignKey(
        "consultations.Consultation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="medical_records",
    )
    title = models.CharFild(max_length=255)
    chief_complaint = models.TextField(blank=True)
    symptoms = models.JSONField(default=list, blank=True)
    diagnosis = models.TextField(blank=True)
    diagnosis_codes = models.JSONField(default=list, blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    is_confidential = models.BooleanField(default=False)


class VitalSigns(TimeStampedModel):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name="vitals")
    recorded_at = models.DateTimeField()
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)


class Allergy(TimeStampedModel):
    class Severity(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        LIFE_THREATENING = "life_threatening", "Life threatening"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allergies",
    )
    allergen = models.CharField(max_length=255)
    reaction = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MODERATE)
    diagnosed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Medication(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medications",
    )
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=120, blank=True)
    frequency = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    prescribed_by = models.ForeignKey(
        "profiles.DoctorProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)


class MedicalHistoryEntry(TimeStampedModel):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_history",
    )
    condition = models.CharField(max_length=255)
    diagnosed_date = models.DateField(null=True, blank=True)
    resolved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_chronic = models.BooleanField(default=False)


class MedicalAttachment(TimeStampedModel):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="medical/attachments/")
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Referral(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        COMPLETED = "completed", "Completed"
        DECLINED = "declined", "Declined"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referrals")
    referring_doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        on_delete=models.CASCADE,
        related_name="referrals_sent",
    )
    referred_doctor = models.ForeignKey(
        "profiles.DoctorProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals_received",
    )
    specialty = models.ForeignKey(
        "profiles.MedicalSpecialty",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reason = models.TextField()
    urgency = models.CharField(max_length=16, default="routine")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
