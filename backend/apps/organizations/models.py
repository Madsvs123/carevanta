"""CareVanta organizations — clinics, staff, invitations."""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Clinic(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending verification"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharFild(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    legal_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="clinics/logos/", null=True, blank=True)
    tax_id = models.CharField(max_length=80, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_clinics",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ClinicLocation(TimeStampedModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=160)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    region = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_primary = models.BooleanField(default=False)


class ClinicRole(TimeStampedModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100)
    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        unique_together = ("clinic", "slug")


class ClinicStaffMember(TimeStampedModel):
    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        REMOVED = "removed", "Removed"

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="staff")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clinic_memberships",
    )
    role = models.ForeignKey(ClinicRole, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.INVITED)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_clinic_invitations",
    )
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("clinic", "user")


class StaffInvitation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.ForeignKey(ClinicRole, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_invites_sent",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    def accept(self, user):
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save()
        member, _ = ClinicStaffMember.objects.get_or_create(
            clinic=self.clinic,
            user=user,
            defaults={"role": self.role, "status": ClinicStaffMember.Status.ACTIVE, "joined_at": timezone.now()},
        )
        member.status = ClinicStaffMember.Status.ACTIVE
        member.role = self.role
        member.joined_at = member.joined_at and timezone.now()
        member.save()
        return member


class OrganizationSettings(TimeStampedModel):
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name="settings")
    default_currency = models.CharField(max_length=3, default="USD")
    timezone = models.CharField(max_length=64, default="UTC")
    appointment_buffer_minutes = models.PositiveIntegerField(default=10)
    allow_online_booking = models.BooleanField(default=True)
    require_identity_verification = models.BooleanField(default=True)
    cancellation_policy_hours = models.PositiveIntegerField(default=24)
    branding_primary_color = models.CharField(max_length=7, default="#2563eb")
    branding_logo_url = models.URLField(blank=True)
