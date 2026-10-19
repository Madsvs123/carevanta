"""CareVanta Insurance domain models.""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InsurancePayer(TimeStampedModel):
    name = models.CharFild(max_length=255)
    payer_code = models.CharField(max_length=64, unique=True)
    phone = models.CharField(max_length=32, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    supports_electronic = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.payer_code})"


class PatientInsurancePolicy(TimeStampedModel):
    class CoverageType(models.TextChoices):
        PRIMARY = "primary", "Primary"
        SECONDARY = "secondary", "Secondary"
        TERTIARY = "tertiary", "Tertiary"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="insurance_policies")
    payer = models.ForeignKey(InsurancePayer, on_delete=models.PROTECT, related_name="policies")
    member_id = models.CharField(max_length=64)
    group_number = models.CharField(max_length=64, blank=True)
    coverage_type = models.CharField(max_length=16, choices=CoverageType.choices, default=CoverageType.PRIMARY)
    plan_name = models.CharField(max_length=255, blank=True)
    effective_from = models.DateField(
    effective_to = models.DateField(null=True, blank=True)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coinsurance_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)


class EligibilityCheck(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ELIGIBLE = "eligible", "Eligible"
        INELIGIBLE = "ineligible", "Ineligible"
        ERROR = "error", "Error"

    policy = models.ForeignKey(PatientInsurancePolicy, on_delete=models.CASCADE, related_name="eligibility_checks")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    checked_at = models.DateTimeField(null=True, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)


class PriorAuthorization(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        EXPIRED = "expired", "Expired"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="prior_auths")
    policy = models.ForeignKey(PatientInsurancePolicy, on_delete=models.CASCADE, related_name="prior_auths")
    service_code = models.CharField(max_length=32)
    service_description = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    authorization_number = models.CharField(max_length=64, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="prior_auth_requests")
    expires_at = models.DateField(null=True, blank=True)
    denial_reason = models.TextField(blank=True)
