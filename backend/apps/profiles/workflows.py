"""Doctor & patient profile workflows for CareVanta `profiles` domain.

Enriched orchestration layer: validation, state transitions, dashboards,
and side-effect hooks used by views/API actions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from apps.core.audit import log_audit_event


@dataclass
class WorkflowResult
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
MODULE = "profiles"


def _ok(code: str, message: str, **data: Any) -> WorkflowResult:
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


def publish_doctor_profile(ctx: WorkflowContext) -> WorkflowResult:
    """Mark doctor searchable and accepting patients."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "publish_doctor_profile", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "publish_doctor_profile",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Mark doctor searchable and accepting patients",
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
    return _ok("publish_doctor_profile_ok", "Mark doctor searchable and accepting patients", **data)


def unpublish_doctor_profile(ctx: WorkflowContext) -> WorkflowResult:
    """Hide doctor from public discovery."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "unpublish_doctor_profile", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "unpublish_doctor_profile",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Hide doctor from public discovery",
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
    return _ok("unpublish_doctor_profile_ok", "Hide doctor from public discovery", **data)


def update_consultation_fee(ctx: WorkflowContext) -> WorkflowResult:
    """Set fee and currency for visits."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "update_consultation_fee", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "update_consultation_fee",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Set fee and currency for visits",
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
    return _ok("update_consultation_fee_ok", "Set fee and currency for visits", **data)


def attach_specialty(ctx: WorkflowContext) -> WorkflowResult:
    """Link specialty to doctor profile."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "attach_specialty", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "attach_specialty",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Link specialty to doctor profile",
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
    return _ok("attach_specialty_ok", "Link specialty to doctor profile", **data)


def detach_specialty(ctx: WorkflowContext) -> WorkflowResult:
    """Remove specialty association."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "detach_specialty", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "detach_specialty",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Remove specialty association",
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
    return _ok("detach_specialty_ok", "Remove specialty association", **data)


def add_education_entry(ctx: WorkflowContext) -> WorkflowResult:
    """Append education credential."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "add_education_entry", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "add_education_entry",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Append education credential",
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
    return _ok("add_education_entry_ok", "Append education credential", **data)


def add_certification(ctx: WorkflowContext) -> WorkflowResult:
    """Append board certification."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "add_certification", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "add_certification",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Append board certification",
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
    return _ok("add_certification_ok", "Append board certification", **data)


def update_languages(ctx: WorkflowContext) -> WorkflowResult:
    """Replace spoken languages list."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "update_languages", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "update_languages",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Replace spoken languages list",
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
    return _ok("update_languages_ok", "Replace spoken languages list", **data)


def patient_demographics_patch(ctx: WorkflowContext) -> WorkflowResult:
    """Update patient demographics safely."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "patient_demographics_patch", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "patient_demographics_patch",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Update patient demographics safely",
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
    return _ok("patient_demographics_patch_ok", "Update patient demographics safely", **data)


def availability_summary(ctx: WorkflowContext) -> WorkflowResult:
    """Count open slots for doctor."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "availability_summary", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "availability_summary",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Count open slots for doctor",
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
    return _ok("availability_summary_ok", "Count open slots for doctor", **data)


def featured_doctors(ctx: WorkflowContext) -> WorkflowResult:
    """Rank doctors by rating and activity."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "featured_doctors", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "featured_doctors",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Rank doctors by rating and activity",
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
    return _ok("featured_doctors_ok", "Rank doctors by rating and activity", **data)


def search_doctors(ctx: WorkflowContext) -> WorkflowResult:
    """Filter doctors by specialty, fee, language."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "search_doctors", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "search_doctors",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Filter doctors by specialty, fee, language",
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
    return _ok("search_doctors_ok", "Filter doctors by specialty, fee, language", **data)


OPERATION_REGISTRY: dict[str, Callable[[WorkflowContext], WorkflowResult]] = {
    "publish_doctor_profile": publish_doctor_profile,
    "unpublish_doctor_profile": unpublish_doctor_profile,
    "update_consultation_fee": update_consultation_fee,
    "attach_specialty": attach_specialty,
    "detach_specialty": detach_specialty,
    "add_education_entry": add_education_entry,
    "add_certification": add_certification,
    "update_languages": update_languages,
    "patient_demographics_patch": patient_demographics_patch,
    "availability_summary": availability_summary,
    "featured_doctors": featured_doctors,
    "search_doctors": search_doctors,
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
        "title": 'Doctor & patient profile workflows',
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

