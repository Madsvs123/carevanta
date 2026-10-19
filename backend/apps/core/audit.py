"""Lightweight request/domain audit helpers (replaces standalone audit app)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_EVENTS: list[dict[str, Any]] = []


@dataclass
class AuditEvent:
    action: str
    resource_type: str
    resource_id: str = ""
    actor_id: int | None = None
    is_phi_access: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
    user_agent: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def log_audit_event(
    *,
    actor=None,
    action: str = "view",
    resource_type: str = "",
    resource_id=None,
    is_phi_access: bool = False,
    metadata: dict | None = None,
    ip_address: str | None = None,
    user_agent: str = "",
):
    event = AuditEvent(
        action=action,
        resource_type=resource_type or "",
        resource_id=str(resource_id) if resource_id is not None else "",
        actor_id=getattr(actor, "id", None),
        is_phi_access=bool(is_phi_access),
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=(user_agent or "")[:512],
    )
    payload = event.__dict__.copy()
    _EVENTS.append(payload)
    if len(_EVENTS) > 5000:
        del _EVENTS[:1000]
    return payload


def recent_events(limit: int = 50) -> list[dict[str, Any]]:
    return list(reversed(_EVENTS[-limit:]))
