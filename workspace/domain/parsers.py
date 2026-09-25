"""
domain/parsers.py
=================
Task T-801 — Data Parsers and Validators enforcing DDD contracts and ISO 8601 UTC.

Provides:
  • parse_registration_input   – Converts raw registration dict → UserAggregate.
  • parse_user_from_db_record  – Converts raw DB dict → UserInDB persistence model.
  • parse_user_public_from_dict – Converts raw dict → UserPublic outbound DTO.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping

from domain.user import UserAggregate, UserInDB, UserPublic, UserRole
from domain.value_objects import (
    EmailAddress,
    HashedPassword,
    Timestamp,
    UserId,
    Username,
)


# ---------------------------------------------------------------------------
# Timestamp helper
# ---------------------------------------------------------------------------

def _parse_timestamp(val: Any) -> datetime:
    """
    Parse a timestamp value (str, int, float, datetime) into a UTC datetime.
    Rejects malformed strings or non-UTC unaware datetimes.
    """
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val, tz=timezone.utc)

    if isinstance(val, str):
        # Delegate parsing and ISO 8601 validation to Timestamp value object
        ts = Timestamp.from_iso(val)
        return ts.dt

    raise TypeError(f"Cannot parse timestamp from {type(val).__name__}: {val!r}")


# ---------------------------------------------------------------------------
# 1. Registration Parser
# ---------------------------------------------------------------------------

def parse_registration_input(raw: Mapping[str, Any]) -> UserAggregate:
    """
    Parse and validate a raw registration dictionary into a UserAggregate.

    Required keys:
        username (str): 3-32 characters, valid format
        email    (str): valid RFC 5322 email
        password (str): plain-text password, min 8 characters

    Optional keys:
        role      (str | UserRole): defaults to UserRole.USER
        full_name (str): optional display name

    Raises:
        TypeError:  if input is not a mapping or fields have wrong types.
        KeyError:   if required keys are missing.
        ValueError: if validation invariants fail.
    """
    if not isinstance(raw, Mapping):
        raise TypeError(f"Registration payload must be a mapping, got {type(raw).__name__}")

    # Check required keys
    for req in ("username", "email", "password"):
        if req not in raw:
            raise KeyError(f"Missing required registration field: '{req}'")

    raw_username = raw["username"]
    raw_email = raw["email"]
    raw_password = raw["password"]

    if not isinstance(raw_username, str):
        raise TypeError(f"username must be a string, got {type(raw_username).__name__}")
    if not isinstance(raw_email, str):
        raise TypeError(f"email must be a string, got {type(raw_email).__name__}")
    if not isinstance(raw_password, str):
        raise TypeError(f"password must be a string, got {type(raw_password).__name__}")

    # Parse role
    role_val = raw.get("role", UserRole.USER)
    if isinstance(role_val, str):
        role = UserRole.from_str(role_val)
    elif isinstance(role_val, UserRole):
        role = role_val
    else:
        raise TypeError(f"Invalid role type: {type(role_val).__name__}")

    full_name = raw.get("full_name")
    if full_name is not None and not isinstance(full_name, str):
        raise TypeError(f"full_name must be a string or None, got {type(full_name).__name__}")

    return UserAggregate.register(
        username=raw_username,
        email=raw_email,
        plain_password=raw_password,
        role=role,
        full_name=full_name,
    )


# ---------------------------------------------------------------------------
# 2. Database Record Parser
# ---------------------------------------------------------------------------

def parse_user_from_db_record(raw: Mapping[str, Any]) -> UserInDB:
    """
    Parse a raw storage dictionary into a UserInDB persistence model.

    Required keys:
        username        (str)
        email           (str)
        hashed_password (str): must be PBKDF2 or standardized crypt hash

    Optional keys:
        id         (str)
        role       (str | UserRole)
        is_active  (bool)
        full_name  (str)
        created_at (str | datetime | float)
        updated_at (str | datetime | float)

    Raises:
        TypeError:  if input is not a mapping.
        KeyError:   if required keys are missing.
        ValueError: if invariants fail (e.g. plain-text password detected).
    """
    if not isinstance(raw, Mapping):
        raise TypeError(f"Database record must be a mapping, got {type(raw).__name__}")

    for req in ("username", "email", "hashed_password"):
        if req not in raw:
            raise KeyError(f"Missing required database record field: '{req}'")

    raw_hp = raw["hashed_password"]
    if not isinstance(raw_hp, str) or not raw_hp:
        raise ValueError("hashed_password must be a non-empty string.")

    # Invariant: reject plain text passwords stored in DB records
    if not (raw_hp.startswith("pbkdf2_") or raw_hp.startswith("$")):
        raise ValueError("Database record contains unhashed or invalid credentials.")

    # Parse role
    raw_role = raw.get("role", UserRole.USER)
    if isinstance(raw_role, str):
        role = UserRole.from_str(raw_role)
    elif isinstance(raw_role, UserRole):
        role = raw_role
    else:
        raise TypeError(f"Invalid role type: {type(raw_role).__name__}")

    # Parse timestamps
    created_at = (
        _parse_timestamp(raw["created_at"])
        if "created_at" in raw and raw["created_at"] is not None
        else datetime.now(timezone.utc)
    )
    updated_at = (
        _parse_timestamp(raw["updated_at"])
        if "updated_at" in raw and raw["updated_at"] is not None
        else datetime.now(timezone.utc)
    )

    kwargs: dict[str, Any] = {
        "username": raw["username"],
        "email": raw["email"],
        "hashed_password": raw_hp,
        "role": role,
        "is_active": raw.get("is_active", True),
        "full_name": raw.get("full_name"),
        "created_at": created_at,
        "updated_at": updated_at,
    }
    if "id" in raw and raw["id"] is not None:
        kwargs["id"] = str(raw["id"])

    return UserInDB(**kwargs)


# ---------------------------------------------------------------------------
# 3. Public DTO Parser
# ---------------------------------------------------------------------------

def parse_user_public_from_dict(raw: Mapping[str, Any]) -> UserPublic:
    """
    Parse a dictionary into a UserPublic outbound DTO.
    Rejects or denies any raw credentials present in the payload.
    """
    if not isinstance(raw, Mapping):
        raise TypeError(f"Payload must be a mapping, got {type(raw).__name__}")

    # Security check: fail fast if caller attempts to construct UserPublic with credentials
    for sensitive in ("password", "hashed_password", "plain_password", "salt", "secret"):
        if sensitive in raw:
            raise ValueError(
                f"Security violation: attempt to create UserPublic with sensitive field '{sensitive}'."
            )

    for req in ("id", "username", "email"):
        if req not in raw:
            raise KeyError(f"Missing required public user field: '{req}'")

    raw_role = raw.get("role", UserRole.USER)
    if isinstance(raw_role, str):
        role = UserRole.from_str(raw_role)
    elif isinstance(raw_role, UserRole):
        role = raw_role
    else:
        raise TypeError(f"Invalid role type: {type(raw_role).__name__}")

    created_at = (
        _parse_timestamp(raw["created_at"])
        if "created_at" in raw and raw["created_at"] is not None
        else datetime.now(timezone.utc)
    )
    updated_at = (
        _parse_timestamp(raw["updated_at"])
        if "updated_at" in raw and raw["updated_at"] is not None
        else datetime.now(timezone.utc)
    )

    return UserPublic(
        id=str(raw["id"]),
        username=str(raw["username"]),
        email=str(raw["email"]),
        role=role,
        is_active=bool(raw.get("is_active", True)),
        full_name=raw.get("full_name"),
        created_at=created_at,
        updated_at=updated_at,
    )
