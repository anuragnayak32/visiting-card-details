"""Shared helper utilities."""

import uuid
from datetime import datetime, timezone


def generate_contact_id() -> str:
    return str(uuid.uuid4())


def generate_session_id() -> str:
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""
    return "".join(char for char in phone if char.isdigit())


def normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()
