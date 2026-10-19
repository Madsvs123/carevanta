"""CareVanta profiles — patients, doctors, specialties."""
from django.conf impor settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MedicalSpecialty(TimeStampedModel):
    name = models.CharFild(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "medical specialties"

    def __str__(self):
        return self.name


class PatientProfile(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT = "prefer_not", "Prefer not to say"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, choices=Gender.choices, blank=True)
    blood_type = models.CharField(max_length=8, blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=32, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2, blank=True)
    insurance_provider = models.CharField(max_length=160, blank=True)
    insurance_policy_number = models.CharField(max_length=80, blank=True)
    medical_summary = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.email}"


class DoctorProfile(TimeStampedModel):
    class ConsultationType(models.TextChoices):
        VIDEO = "video", "Video"
        IN_PERSON = "in_person", "In person"
        BOTH = "both", "Video and in person"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    title = models.CharField(max_length=32, default="Dr.")
    license_number = models.CharField(max_length=80, unique=True)
    license_state = models.CharField(max_length=80, blank=True)
    license_country = models.CharField(max_length=2, default="US")
    bio = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    consultation_type = models.CharField(
        max_length=16,
        choices=ConsultationType.choices,
        default=ConsultationType.BOTH,
    )
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    follow_up_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_appointment_duration = models.PositiveIntegerField(default=30)
    languages = models.JSONField(default=list, blank=True)
    specialties = models.ManyToManyField(MedicalSpecialty, related_name="doctors", blank=True)
    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    rating_count = models.PositiveIntegerField(default=0)
    is_accepting_patients = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    clinic = models.ForeignKey(
        "organizations.Clinic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="doctors",
    )

    def __str__(self):
        return f"{self.title} {self.user.get_full_name() or self.user.email}"


class DoctorLanguage(TimeStampedModel):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="spoken_languages")
    language_code = models.CharField(max_length=10)
    proficiency = models.CharField(max_length=32, default="fluent")

    class Meta:
        unique_together = ("doctor", "language_code")


class DoctorEducation(TimeStampedModel):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=120)
    field_of_study = models.CharField(max_length=120, blank=True)
    year_completed = models.PositiveIntegerField(null=True, blank=True)


class DoctorCertification(TimeStampedModel):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=255)
    issuing_body = models.CharField(max_length=255)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
