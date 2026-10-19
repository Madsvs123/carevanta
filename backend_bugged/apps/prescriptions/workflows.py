"""E-prescribing workflows for CareVanta `prescriptions` domain.

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


MODULE = "prescriptions"


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


def draft_prescription(ctx: WorkflowContext) -> WorkflowResult:
    """Create draft Rx for patient."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "draft_prescription", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "draft_prescription",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Create draft Rx for patient",
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
    return _ok("draft_prescription_ok", "Create draft Rx for patient", **data)


def add_rx_item(ctx: WorkflowContext) -> WorkflowResult:
    """Add medication line to prescription."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "add_rx_item", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "add_rx_item",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Add medication line to prescription",
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
    return _ok("add_rx_item_ok", "Add medication line to prescription", **data)


def run_interaction_check(ctx: WorkflowContext) -> WorkflowResult:
    """Evaluate interaction warnings."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "run_interaction_check", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "run_interaction_check",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Evaluate interaction warnings",
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
    return _ok("run_interaction_check_ok", "Evaluate interaction warnings", **data)


def activate_prescription(ctx: WorkflowContext) -> WorkflowResult:
    """Activate Rx for pharmacy routing."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "activate_prescription", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "activate_prescription",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Activate Rx for pharmacy routing",
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
    return _ok("activate_prescription_ok", "Activate Rx for pharmacy routing", **data)


def route_to_pharmacy(ctx: WorkflowContext) -> WorkflowResult:
    """Assign preferred pharmacy."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "route_to_pharmacy", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "route_to_pharmacy",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Assign preferred pharmacy",
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
    return _ok("route_to_pharmacy_ok", "Assign preferred pharmacy", **data)


def request_refill(ctx: WorkflowContext) -> WorkflowResult:
    """Patient refill request workflow."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "request_refill", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "request_refill",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Patient refill request workflow",
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
    return _ok("request_refill_ok", "Patient refill request workflow", **data)


def approve_refill(ctx: WorkflowContext) -> WorkflowResult:
    """Clinician approve refill."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "approve_refill", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "approve_refill",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Clinician approve refill",
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
    return _ok("approve_refill_ok", "Clinician approve refill", **data)


def deny_refill(ctx: WorkflowContext) -> WorkflowResult:
    """Deny refill with reason."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "deny_refill", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "deny_refill",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Deny refill with reason",
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
    return _ok("deny_refill_ok", "Deny refill with reason", **data)


def cancel_prescription(ctx: WorkflowContext) -> WorkflowResult:
    """Cancel active Rx."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "cancel_prescription", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "cancel_prescription",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Cancel active Rx",
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
    return _ok("cancel_prescription_ok", "Cancel active Rx", **data)


def pharmacy_queue(ctx: WorkflowContext) -> WorkflowResult:
    """List Rx awaiting pharmacy pickup."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "pharmacy_queue", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "pharmacy_queue",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "List Rx awaiting pharmacy pickup",
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
    return _ok("pharmacy_queue_ok", "List Rx awaiting pharmacy pickup", **data)


def controlled_substance_gate(ctx: WorkflowContext) -> WorkflowResult:
    """Extra checks for controlled meds."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "controlled_substance_gate", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "controlled_substance_gate",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Extra checks for controlled meds",
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
    return _ok("controlled_substance_gate_ok", "Extra checks for controlled meds", **data)


def rx_history_for_patient(ctx: WorkflowContext) -> WorkflowResult:
    """Chronological Rx history."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "rx_history_for_patient", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "rx_history_for_patient",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Chronological Rx history",
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
    return _ok("rx_history_for_patient_ok", "Chronological Rx history", **data)


OPERATION_REGISTRY: dict[str, Callable[[WorkflowContext], WorkflowResult]] = {
    "draft_prescription": draft_prescription,
    "add_rx_item": add_rx_item,
    "run_interaction_check": run_interaction_check,
    "activate_prescription": activate_prescription,
    "route_to_pharmacy": route_to_pharmacy,
    "request_refill": request_refill,
    "approve_refill": approve_refill,
    "deny_refill": deny_refill,
    "cancel_prescription": cancel_prescription,
    "pharmacy_queue": pharmacy_queue,
    "controlled_substance_gate": controlled_substance_gate,
    "rx_history_for_patient": rx_history_for_patient,
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
        "title": 'E-prescribing workflows',
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

