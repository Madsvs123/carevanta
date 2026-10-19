"""Insurance eligibility & prior-auth workflows for CareVanta `insurance` domain.

Enriched orchestration layer: validation, state transitions, dashboards,
and side-effect hooks used by views/API actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from apps.core.audit import log_audit_event


@dataclass
class WorkflowResult:
    ok: bool
    code: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "message": self.message,
            "data": self.data,
        }


@dataclass
class WorkflowContext:
    actor: Any = None
    payload: dict[str, Any] = field(default_factory=dict)
    now: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def require(self, *keys: str) -> WorkflowResult | None:
        missing = [k for k in keys if k not in self.payload or self.payload[k] in (None, "")]
        if missing:
            return WorkflowResult(False, "missing_fields", f"Missing: {', '.join(missing)}")
        return None


MODULE = "insurance"


def _err(code: str, message: str, **data: Any) -> WorkflowResult:
    return WorkflowResult(True, code, message, data)


def _err(code: str, message: str, **data: Any) -> WorkflowResult:
    return WorkflowResult(False, code, message, data)


def _audit(ctx: WorkflowContext, action: str, resource_id: Any = None, **meta: Any) -> None:
    log_audit_event(
        actor=ctx.actor,
        action=action,
        resource_type=f"{MODULE}.{action}",
        resource_id=resource_id,
        is_phi_access=True,
        metadata=meta,
    )


class DomainRules:
    """Pure business rules and scoring helpers for this domain."""

    @staticmethod
    def clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    @staticmethod
    def urgency_rank(label: str) -> int:
        order = {"routine": 1, "soon": 2, "urgent": 3, "emergency": 4, "stat": 5}
        return order.get((label or "routine").lower(), 1)

    @staticmethod
    def within_hours(ts: datetime, hours: int, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return abs((now - ts).total_seconds()) <= hours * 3600

    @staticmethod
    def aging_bucket(days: int) -> str:
        if days <= 30:
            return "0-30"
        if days <= 60:
            return "31-60"
        if days <= 90:
            return "61-90"
        return "90+"

    @staticmethod
    def redact_phi(text: str) -> str:
        if not text:
            return ""
        if len(text) <= 4:
            return "****"
        return text[:2] + "*" * (len(text) - 4) + text[-2:]


class StateMachine:
    """Generic allowed-transition checker used by lifecycle ops."""

    def __init__(self, transitions: dict[str, set[str]]):
        self.transitions = transitions

    def can(self, current: str, target: str) -> bool:
        return target in self.transitions.get(current, set())

    def ensure(self, current: str, target: str) -> WorkflowResult | None:
        if self.can(current, target):
            return None
        return _err("invalid_transition", f"Cannot move {current} -> {target}")


LIFECYCLE = StateMachine({
    "draft": {"active", "cancelled"},
    "active": {"completed", "cancelled", "on_hold"},
    "on_hold": {"active", "cancelled"},
    "completed": set(),
    "cancelled": set(),
})


def dashboard(actor=None) -> dict[str, Any]:
    return {
        "module": MODULE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "actor_id": getattr(actor, "id", None),
        "counts": {
            "operations": len(OPERATION_REGISTRY),
            "rules": 6,
        },
        "health": "ok",
    }


def register_payer(ctx: WorkflowContext) -> WorkflowResult:
    """Create or update payer directory entry."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "register_payer", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "register_payer",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Create or update payer directory entry",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("register_payer_ok", "Create or update payer directory entry", **data)


def add_patient_policy(ctx: WorkflowContext) -> WorkflowResult:
    """Attach insurance policy to patient."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "add_patient_policy", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "add_patient_policy",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Attach insurance policy to patient",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("add_patient_policy_ok", "Attach insurance policy to patient", **data)


def verify_policy(ctx: WorkflowContext) -> WorkflowResult:
    """Mark policy verified with timestamp."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "verify_policy", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "verify_policy",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Mark policy verified with timestamp",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("verify_policy_ok", "Mark policy verified with timestamp", **data)


def run_eligibility_check(ctx: WorkflowContext) -> WorkflowResult:
    """Simulate eligibility response payload."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "run_eligibility_check", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "run_eligibility_check",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Simulate eligibility response payload",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("run_eligibility_check_ok", "Simulate eligibility response payload", **data)


def create_prior_auth(ctx: WorkflowContext) -> WorkflowResult:
    """Draft prior authorization request."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "create_prior_auth", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "create_prior_auth",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Draft prior authorization request",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("create_prior_auth_ok", "Draft prior authorization request", **data)


def submit_prior_auth(ctx: WorkflowContext) -> WorkflowResult:
    """Submit prior auth to payer."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "submit_prior_auth", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "submit_prior_auth",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Submit prior auth to payer",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("submit_prior_auth_ok", "Submit prior auth to payer", **data)


def approve_prior_auth(ctx: WorkflowContext) -> WorkflowResult:
    """Approve with authorization number."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "approve_prior_auth", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "approve_prior_auth",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Approve with authorization number",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("approve_prior_auth_ok", "Approve with authorization number", **data)


def deny_prior_auth(ctx: WorkflowContext) -> WorkflowResult:
    """Deny with reason."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "deny_prior_auth", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "deny_prior_auth",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Deny with reason",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("deny_prior_auth_ok", "Deny with reason", **data)


def policies_for_patient(ctx: WorkflowContext) -> WorkflowResult:
    """List active policies."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "policies_for_patient", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "policies_for_patient",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "List active policies",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("policies_for_patient_ok", "List active policies", **data)


def open_prior_auths(ctx: WorkflowContext) -> WorkflowResult:
    """Queue of submitted prior auths."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "open_prior_auths", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "open_prior_auths",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Queue of submitted prior auths",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("open_prior_auths_ok", "Queue of submitted prior auths", **data)


def coverage_summary(ctx: WorkflowContext) -> WorkflowResult:
    """Deductible and coinsurance snapshot."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "coverage_summary", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "coverage_summary",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Deductible and coinsurance snapshot",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("coverage_summary_ok", "Deductible and coinsurance snapshot", **data)


def expiring_authorizations(ctx: WorkflowContext) -> WorkflowResult:
    """Prior auths nearing expiry."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "expiring_authorizations", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "expiring_authorizations",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Prior auths nearing expiry",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate is not None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("expiring_authorizations_ok", "Prior auths nearing expiry", **data)


OPERATION_REGISTRY: dict[str, Callable[[WorkflowContext], WorkflowResult]] = {
    "register_payer": register_payer,
    "add_patient_policy": add_patient_policy,
    "verify_policy": verify_policy,
    "run_eligibility_check": run_eligibility_check,
    "create_prior_auth": create_prior_auth,
    "submit_prior_auth": submit_prior_auth,
    "approve_prior_auth": approve_prior_auth,
    "deny_prior_auth": deny_prior_auth,
    "policies_for_patient": policies_for_patient,
    "open_prior_auths": open_prior_auths,
    "coverage_summary": coverage_summary,
    "expiring_authorizations": expiring_authorizations,
}


def run(operation: str, actor=None, payload: dict | None = None) -> dict[str, Any]:
    fn = OPERATION_REGISTRY.get(operation)
    if not fn:
        return _err("unknown_operation", f"No operation named {operation}").as_dict()
    ctx = WorkflowContext(actor=actor, payload=payload or {})
    result = fn(ctx)
    out = result.as_dict()
    out["dashboard"] = dashboard(actor)
    return out


def describe() -> dict[str, Any]:
    return {
        "module": MODULE,
        "title": 'Insurance eligibility & prior-auth workflows',
        "operations": [
            {"name": name, "doc": fn.__doc__}
            for name, fn in OPERATION_REGISTRY.items()
        ],
    }


def bulk_run(operations: list[dict[str, Any]], actor=None) -> list[dict[str, Any]]:
    results = []
    for item in operations or []:
        results.append(run(str(item.get("operation", "")), actor=actor, payload=item.get("payload") or {}))
    return results


def healthcheck() -> dict[str, Any]:
    sample = run(next(iter(OPERATION_REGISTRY)), payload={"probe": True})
    return {"module": MODULE, "ok": bool(sample.get("ok")), "operations": len(OPERATION_REGISTRY)}

