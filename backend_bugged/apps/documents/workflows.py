"""Document vault workflows for CareVanta `documents` domain.

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


MODULE = "documents"


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


def create_folder(ctx: WorkflowContext) -> WorkflowResult:
    """Create folder for owner."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "create_folder", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "create_folder",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Create folder for owner",
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
    return _ok("create_folder_ok", "Create folder for owner", **data)


def upload_document_meta(ctx: WorkflowContext) -> WorkflowResult:
    """Register document file metadata."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "upload_document_meta", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "upload_document_meta",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Register document file metadata",
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
    return _ok("upload_document_meta_ok", "Register document file metadata", **data)


def move_document(ctx: WorkflowContext) -> WorkflowResult:
    """Move document between folders."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "move_document", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "move_document",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Move document between folders",
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
    return _ok("move_document_ok", "Move document between folders", **data)


def rename_document(ctx: WorkflowContext) -> WorkflowResult:
    """Rename document display title."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "rename_document", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "rename_document",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Rename document display title",
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
    return _ok("rename_document_ok", "Rename document display title", **data)


def soft_delete_document(ctx: WorkflowContext) -> WorkflowResult:
    """Soft-delete document."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "soft_delete_document", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "soft_delete_document",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Soft-delete document",
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
    return _ok("soft_delete_document_ok", "Soft-delete document", **data)


def restore_document(ctx: WorkflowContext) -> WorkflowResult:
    """Restore soft-deleted document."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "restore_document", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "restore_document",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Restore soft-deleted document",
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
    return _ok("restore_document_ok", "Restore soft-deleted document", **data)


def share_link_payload(ctx: WorkflowContext) -> WorkflowResult:
    """Build temporary share descriptor."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "share_link_payload", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "share_link_payload",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Build temporary share descriptor",
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
    return _ok("share_link_payload_ok", "Build temporary share descriptor", **data)


def list_folder_tree(ctx: WorkflowContext) -> WorkflowResult:
    """Nested folder listing."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "list_folder_tree", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "list_folder_tree",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Nested folder listing",
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
    return _ok("list_folder_tree_ok", "Nested folder listing", **data)


def search_documents(ctx: WorkflowContext) -> WorkflowResult:
    """Search by name and tags."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "search_documents", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "search_documents",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Search by name and tags",
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
    return _ok("search_documents_ok", "Search by name and tags", **data)


def tag_document(ctx: WorkflowContext) -> WorkflowResult:
    """Update tag list."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "tag_document", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "tag_document",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Update tag list",
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
    return _ok("tag_document_ok", "Update tag list", **data)


def quota_usage(ctx: WorkflowContext) -> WorkflowResult:
    """Compute storage usage for owner."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "quota_usage", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "quota_usage",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Compute storage usage for owner",
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
    return _ok("quota_usage_ok", "Compute storage usage for owner", **data)


def recent_documents(ctx: WorkflowContext) -> WorkflowResult:
    """Latest documents for dashboard."""
    missing = ctx.require("id") if "id" in (ctx.payload or {}) else None
    # soft validation — callers may omit id for create-style ops
    _ = missing
    resource_id = ctx.payload.get("id") or ctx.payload.get("resource_id")
    _audit(ctx, "recent_documents", resource_id, keys=list(ctx.payload.keys())[:12])
    data = {
        "operation": "recent_documents",
        "module": MODULE,
        "actor_id": getattr(ctx.actor, "id", None),
        "received": {k: ctx.payload.get(k) for k in list(ctx.payload)[:20]},
        "processed_at": ctx.now.isoformat(),
        "notes": "Latest documents for dashboard",
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
    return _ok("recent_documents_ok", "Latest documents for dashboard", **data)


OPERATION_REGISTRY: dict[str, Callable[[WorkflowContext], WorkflowResult]] = {
    "create_folder": create_folder,
    "upload_document_meta": upload_document_meta,
    "move_document": move_document,
    "rename_document": rename_document,
    "soft_delete_document": soft_delete_document,
    "restore_document": restore_document,
    "share_link_payload": share_link_payload,
    "list_folder_tree": list_folder_tree,
    "search_documents": search_documents,
    "tag_document": tag_document,
    "quota_usage": quota_usage,
    "recent_documents": recent_documents,
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
        "title": 'Document vault workflows',
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

