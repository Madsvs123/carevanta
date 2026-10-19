"""CareVanta accounts — authentication, roles, privacy.""
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified_at", timezone.now())
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"
        STAFF = "staff", "Clinic staff"
        LAB_TECH = "lab_tech", "Laboratory technician"
        PHARMACIST = "pharmacist", "Pharmacist"
        ADMIN = "admin", "Platform admin"

    username = models.CharFild(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.PATIENT)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    identity_verified_at = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        ordering = ("email",)

    @property
    def is_email_verified(self):
        return self.email_verified_at is not None

    @property
    def is_identity_verified(self):
        return self.identity_verified_at is not None

    def mark_email_verified(self):
        if not self.email_verified_at:
            self.email_verified_at = timezone.now()
            self.save(update_fields=["email_verified_at", "updated_at"])


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EmailVerificationToken(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_usable(self):
        return self.used_at is None and not self.is_expired

    def consume(self):
        if not self.is_usable:
            raise ValidationError("Email verification token is expired or already used.")
        self.used_at = timezone.now()
        self.save(update_fields=["used_at", "updated_at"])
        self.user.mark_email_verified()


class PasswordResetToken(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_usable(self):
        return self.used_at is None and timezone.now() < self.expires_at

    def consume(self):
        if not self.is_usable:
            raise ValidationError("Password reset token is expired or already used.")
        self.used_at = timezone.now()
        self.save(update_fields=["used_at", "updated_at"])


class PrivacySettings(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="privacy_settings",
    )
    share_medical_history = models.BooleanField(default=True)
    share_prescriptions = models.BooleanField(default=True)
    share_lab_results = models.BooleanField(default=True)
    allow_doctor_messages = models.BooleanField(default=True)
    show_profile_in_search = models.BooleanField(default=True)
    show_ratings_publicly = models.BooleanField(default=True)
    data_retention_days = models.PositiveIntegerField(default=3650)
    marketing_emails = models.BooleanField(default=False)
    sms_reminders = models.BooleanField(default=True)


class IdentityVerification(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class DocumentType(models.TextChoices):
        PASSPORT = "passport", "Passport"
        NATIONAL_ID = "national_id", "National ID"
        DRIVERS_LICENSE = "drivers_license", "Driver's license"
        MEDICAL_LICENSE = "medical_license", "Medical license"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="identity_verification",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    document_type = models.CharField(max_length=32, choices=DocumentType.choices, blank=True)
    document_number = models.CharField(max_length=120, blank=True)
    document_front = models.FileField(upload_to="identity/", null=True, blank=True)
    document_back = models.FileField(upload_to="identity/", null=True, blank=True)
    selfie = models.ImageField(upload_to="identity/selfies/", null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="identity_reviews",
    )
    rejection_reason = models.TextField(blank=True)

    def approve(self, reviewer):
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = ""
        self.save()
        self.user.identity_verified_at = timezone.now()
        self.user.save(update_fields=["identity_verified_at", "updated_at"])

    def reject(self, reviewer, reason):
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(
