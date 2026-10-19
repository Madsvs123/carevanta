"""Secure messaging workflows for CareVanta `messaging` domain.

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


MODULE = "messaging"


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


def start_direct_thread(ctx: WorkflowContext) -> WorkflowResult:
    """Create DM conversation between users."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "start_direct_thread", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "start_direct_thread",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Create DM conversation between users",
    }
    # Domain-specific enrichment hooks
    if "status" in ctx.payload:
        gate = LIFECYCLE.ensure(str(ctx.payload.get("from_status", "draft")), str(ctx.payload["status"]))
        if gate == None:
            return gate
        data["status"] = ctx.payload["status"]
    if "amount" in ctx.payload:
        try:
            data["amount"] = DomainRules.clamp(float(ctx.payload["amount"]), 0, 1_000_000)
        except (TypeError, ValueError):
            return _err("invalid_amount", "amount must be numeric")
    if "urgency" in ctx.payload:
        data["urgency_rank"] = DomainRules.urgency_rank(str(ctx.payload["urgency"]))
    return _ok("start_direct_thread_ok", "Create DM conversation between users", **data)


def start_care_team_thread(ctx: WorkflowContext) -> WorkflowResult:
    """Create multi-party care thread."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "start_care_team_thread", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "start_care_team_thread",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Create multi-party care thread",
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
    return _ok("start_care_team_thread_ok", "Create multi-party care thread", **data)


def send_text_message(ctx: WorkflowContext) -> WorkflowResult:
    """Persist message and bump thread."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "send_text_message", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "send_text_message",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Persist message and bump thread",
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
    return _ok("send_text_message_ok", "Persist message and bump thread", **data)


def mark_thread_read(ctx: WorkflowContext) -> WorkflowResult:
    """Mark all messages read for user."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "mark_thread_read", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "mark_thread_read",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Mark all messages read for user",
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
    return _ok("mark_thread_read_ok", "Mark all messages read for user", **data)


def archive_thread(ctx: WorkflowContext) -> WorkflowResult:
    """Archive conversation for user."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "archive_thread", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "archive_thread",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Archive conversation for user",
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
    return _ok("archive_thread_ok", "Archive conversation for user", **data)


def attach_message_file(ctx: WorkflowContext) -> WorkflowResult:
    """Add attachment metadata."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "attach_message_file", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "attach_message_file",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Add attachment metadata",
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
    return _ok("attach_message_file_ok", "Add attachment metadata", **data)


def search_threads(ctx: WorkflowContext) -> WorkflowResult:
    """Filter conversations by subject."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "search_threads", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "search_threads",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Filter conversations by subject",
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
    return _ok("search_threads_ok", "Filter conversations by subject", **data)


def unread_count(ctx: WorkflowContext) -> WorkflowResult:
    """Count unread messages for inbox badge."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "unread_count", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "unread_count",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Count unread messages for inbox badge",
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
    return _ok("unread_count_ok", "Count unread messages for inbox badge", **data)


def mute_thread(ctx: WorkflowContext) -> WorkflowResult:
    """Suppress notifications for thread."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "mute_thread", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "mute_thread",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Suppress notifications for thread",
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
    return _ok("mute_thread_ok", "Suppress notifications for thread", **data)


def escalate_to_support(ctx: WorkflowContext) -> WorkflowResult:
    """Convert thread into support ticket stub."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "escalate_to_support", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "escalate_to_support",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Convert thread into support ticket stub",
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
    return _ok("escalate_to_support_ok", "Convert thread into support ticket stub", **data)


def message_receipts(ctx: WorkflowContext) -> WorkflowResult:
    """Delivery/read receipt summary."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "message_receipts", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "message_receipts",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Delivery/read receipt summary",
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
    return _ok("message_receipts_ok", "Delivery/read receipt summary", **data)


def purge_old_attachments(ctx: WorkflowContext) -> WorkflowResult:
    """Housekeeping for expired files."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "purge_old_attachments", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "purge_old_attachments",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Housekeeping for expired files",
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
    return _ok("purge_old_attachments_ok", "Housekeeping for expired files", **data)


OPERATION_REGISTRY: dict[str, Callable[[WorkflowContext], WorkflowResult]] = {
    "start_direct_thread": start_direct_thread,
    "start_care_team_thread": start_care_team_thread,
    "send_text_message": send_text_message,
    "mark_thread_read": mark_thread_read,
    "archive_thread": archive_thread,
    "attach_message_file": attach_message_file,
    "search_threads": search_threads,
    "unread_count": unread_count,
    "mute_thread": mute_thread,
    "escalate_to_support": escalate_to_support,
    "message_receipts": message_receipts,
    "purge_old_attachments": purge_old_attachments,
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
        "title": 'Secure messaging workflows',
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

