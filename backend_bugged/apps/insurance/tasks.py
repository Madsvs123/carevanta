"""Domain background helpers for insurance."""


def refresh_dashboard_cache(user_id: int | None = None):
    return {"module": "insurance", "user_id": user_id, "ok": True}


def nightly_maintenance():
    return {"module": "insurance", "maintenance": "completed"}
