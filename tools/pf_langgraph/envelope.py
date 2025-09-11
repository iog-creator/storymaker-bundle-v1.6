from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def envelope_ok(data: Dict[str, Any] | None = None, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "status": "ok",
        "data": data or {},
        "error": None,
        "meta": {"ts": datetime.now(timezone.utc).isoformat(), **(meta or {})},
    }


def envelope_err(code: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "status": "error",
        "data": None,
        "error": {"code": code, "message": message, "details": details or {}},
        "meta": {"ts": datetime.now(timezone.utc).isoformat()},
    }


def require_envelope(value: Any, where: str):
    if not isinstance(value, dict) or "status" not in value or "meta" not in value:
        raise ValueError(f"Non-envelope at {where}")
    return value


