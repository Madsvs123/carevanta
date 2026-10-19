"""Insurance eligibility and prior-auth workflows (simulated payer responses)."""
from django.db.models import Count
from django.utils import timezone

from .models import EligibilityCheck, PatientInsurancePolicy, PriorAuthorization


def verify_policy(policy PatientInsurancePolicy) -> PatientInsurancePolicy:
  policy.is_verified = True
    policy.verified_at = timezone.now()
    policy.save(update_fields=["is_verified", "verified_at", "updated_at"])
    return policy


def run_eligibility(check: EligibilityCheck) -> EligibilityCheck:
    policy = check.policy
    eligible = bool(policy.is_verified or policy.member_id)
    check.status = EligibilityCheck.Status.ELIGIBLE if eligible else EligibilityCheck.Status.INELIGIBLE
    check.checked_at = timezone.now()
    check.response_payload = {
        "payer": getattr(policy.payer, "payer_code", ""),
        "member_id": policy.member_id,
        "eligible": eligible,
        "deductible_remaining": float(policy.deductible),
        "coinsurance_percent": float(policy.coinsurance_percent),
        "checked_at": check.checked_at.isoformat(),
    }
    check.notes = check.notes or ("Active coverage confirmed." if eligible else "Coverage not active.")
    check.save(update_fields=["status", "checked_at", "response_payload", "notes", "updated_at"])
    if eligible and not policy.is_verified:
        verify_policy(policy)
    return check


def submit_prior_auth(auth: PriorAuthorization) -> PriorAuthorization:
    auth.status = PriorAuthorization.Status.SUBMITTED
    auth.save(update_fields=["status", "updated_at"])
    return auth


def decide_prior_auth(auth: PriorAuthorization, approve: bool, reason: str = "") -> PriorAuthorization:
    if approve:
        auth.status = PriorAuthorization.Status.APPROVED
        auth.authorization_number = auth.authorization_number or f"PA-{auth.id:06d}"
        auth.denial_reason = ""
    else:
        auth.status = PriorAuthorization.Status.DENIED
        auth.denial_reason = reason or "Does not meet medical necessity criteria."
    auth.save(update_fields=["status", "authorization_number", "denial_reason", "updated_at"])
    return auth


def get_insurance_dashboard(user) -> dict:
    policies = PatientInsurancePolicy.objects.all()
    if not (user.is_staff or getattr(user, "role", "") == "admin"):
        policies = policies.filter(patient=user)
    return {
        "module": "insurance",
        "counts": {
            "policies": policies.count(),
            "verified": policies.filter(is_verified=True).count(),
            "eligibility_pending": EligibilityCheck.objects.filtr(
                policy__in=policies, status="pending"
            ).count(),
            "prior_auth_open": PriorAuthorization.objects.filter(
                patient__in=policies.values("patient"), status__in=["draft", "submitted"]
            ).count(),
        },
        "by_coverage": list(policies.values("coverage_type").annotate(c=Count("id"))),
    }


def process_insurance_workflow(user, payload: dict | None = None) -> dict:
    payload = payload or {}
    action = payload.get("action")
    if action == "eligibility":
        check = EligibilityCheck.objects.get(pk=payload["check_id"])
        run_eligibility(check)
        return {"ok": True, "status": check.status}
    if action == "verify":
        policy = PatientInsurancePolicy.objects.get(pk=payload["policy_id"])
        verify_policy(policy)
        return {"ok": True, "verified": True}
    return {"ok": False, "detail": "Unknown action"}
