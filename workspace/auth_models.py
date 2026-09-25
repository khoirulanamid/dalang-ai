"""
auth_models.py
==============
Task T-101 — User schema and password hashing utility.

Provides:
  • UserRole        – Enum of valid user roles.
  • UserBase        – Shared user fields (dataclass).
  • UserCreate      – Input schema for registration (plain-text password).
  • UserInDB        – Persisted schema (hashed password, no plain-text).
  • UserPublic      – Safe outbound schema (no password fields at all).
  • PasswordHasher  – PBKDF2-HMAC-SHA256 hashing & verification utility.
  • parse_user_create – Parser / validator that converts raw dict → UserCreate.
  • parse_user_in_db  – Parser that converts raw dict → UserInDB.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


# ---------------------------------------------------------------------------
# Password Hashing Utility
# ---------------------------------------------------------------------------

class PasswordHasher:
    """
    PBKDF2-HMAC-SHA256 password hashing utility.

    Hash format (colon-separated):
        pbkdf2_sha256:<iterations>:<hex-salt>:<hex-digest>
    """

    ALGORITHM: str = "sha256"
    ITERATIONS: int = 260_000          # OWASP 2023 recommendation
    SALT_BYTES: int = 32               # 256-bit salt
    HASH_BYTES: int = 32               # 256-bit digest

    # Minimum password policy
    MIN_PASSWORD_LENGTH: int = 8

    @classmethod
    def _validate_plain(cls, password: str) -> None:
        if not isinstance(password, str):
            raise TypeError("Password must be a string.")
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long."
            )

    @classmethod
    def hash_password(cls, plain_password: str) -> str:
        """Hash *plain_password* and return the encoded hash string."""
        cls._validate_plain(plain_password)
        salt = os.urandom(cls.SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            cls.ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            cls.ITERATIONS,
            dklen=cls.HASH_BYTES,
        )
        return (
            f"pbkdf2_{cls.ALGORITHM}"
            f":{cls.ITERATIONS}"
            f":{salt.hex()}"
            f":{digest.hex()}"
        )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Return *True* if *plain_password* matches *hashed_password*.
        Uses constant-time comparison to prevent timing attacks.
        """
        if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
            return False
        try:
            parts = hashed_password.split(":")
            if len(parts) != 4:
                return False
            _, iterations_str, salt_hex, stored_hex = parts
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            stored_digest = bytes.fromhex(stored_hex)
        except (ValueError, AttributeError):
            return False

        candidate = hashlib.pbkdf2_hmac(
            cls.ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(stored_digest),
        )
        return hmac.compare_digest(candidate, stored_digest)

    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """Return *True* if the hash was produced with outdated parameters."""
        try:
            parts = hashed_password.split(":")
            if len(parts) != 4:
                return True
            _, iterations_str, salt_hex, _ = parts
            return int(iterations_str) < cls.ITERATIONS or len(bytes.fromhex(salt_hex)) < cls.SALT_BYTES
        except (ValueError, AttributeError):
            return True


# ---------------------------------------------------------------------------
# Schemas (dataclasses)
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")


def _validate_email(email: str) -> str:
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise ValueError(f"Invalid e-mail address: {email!r}")
    return email


def _validate_username(username: str) -> str:
    username = username.strip()
    if not _USERNAME_RE.match(username):
        raise ValueError(
            f"Username must be 3–64 characters and contain only letters, "
            f"digits, underscores, hyphens, or dots. Got: {username!r}"
        )
    return username


@dataclass
class UserBase:
    """Fields shared across all user schemas."""
    username: str
    email: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    full_name: Optional[str] = None

    def __post_init__(self) -> None:
        self.username = _validate_username(self.username)
        self.email = _validate_email(self.email)
        if not isinstance(self.role, UserRole):
            self.role = UserRole(self.role)


@dataclass
class UserCreate(UserBase):
    """
    Input schema used during user registration.
    Carries the plain-text password — never persisted.
    """
    password: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        PasswordHasher._validate_plain(self.password)

    def to_user_in_db(self) -> "UserInDB":
        """Hash the plain password and return a *UserInDB* instance."""
        return UserInDB(
            username=self.username,
            email=self.email,
            role=self.role,
            is_active=self.is_active,
            full_name=self.full_name,
            hashed_password=PasswordHasher.hash_password(self.password),
        )


@dataclass
class UserInDB(UserBase):
    """
    Persisted user record.
    Stores the hashed password; the plain-text password is never kept.
    """
    hashed_password: str = field(default="", repr=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.hashed_password:
            raise ValueError("hashed_password must not be empty.")

    def verify_password(self, plain_password: str) -> bool:
        """Convenience wrapper around PasswordHasher.verify_password."""
        return PasswordHasher.verify_password(plain_password, self.hashed_password)

    def to_public(self) -> "UserPublic":
        """Return a safe outbound representation with no password data."""
        return UserPublic(
            id=self.id,
            username=self.username,
            email=self.email,
            role=self.role,
            is_active=self.is_active,
            full_name=self.full_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


@dataclass
class UserPublic:
    """
    Outbound / API-safe user representation.
    Contains no password fields whatsoever.
    """
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_user_create(data: dict) -> UserCreate:
    """
    Parse and validate a raw dictionary into a *UserCreate* instance.

    Expected keys:
        username (str)          – required
        email    (str)          – required
        password (str)          – required
        role     (str|UserRole) – optional, default "user"
        is_active (bool)        – optional, default True
        full_name (str|None)    – optional

    Raises:
        TypeError  – if *data* is not a dict.
        KeyError   – if a required key is missing.
        ValueError – if any value fails validation.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__!r}.")

    missing = [k for k in ("username", "email", "password") if k not in data]
    if missing:
        raise KeyError(f"Missing required field(s): {missing}")

    return UserCreate(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", UserRole.USER),
        is_active=bool(data.get("is_active", True)),
        full_name=data.get("full_name"),
    )


def parse_user_in_db(data: dict) -> UserInDB:
    """
    Parse and validate a raw dictionary (e.g. from a database row) into a
    *UserInDB* instance.

    Expected keys:
        username         (str)          – required
        email            (str)          – required
        hashed_password  (str)          – required
        id               (str)          – optional, auto-generated if absent
        role             (str|UserRole) – optional, default "user"
        is_active        (bool)         – optional, default True
        full_name        (str|None)     – optional
        created_at       (str|datetime) – optional, default now
        updated_at       (str|datetime) – optional, default now

    Raises:
        TypeError  – if *data* is not a dict.
        KeyError   – if a required key is missing.
        ValueError – if any value fails validation.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__!r}.")

    missing = [k for k in ("username", "email", "hashed_password") if k not in data]
    if missing:
        raise KeyError(f"Missing required field(s): {missing}")

    def _parse_dt(value) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Cannot parse datetime from {value!r}")

    now = datetime.now(timezone.utc)

    return UserInDB(
        username=data["username"],
        email=data["email"],
        hashed_password=data["hashed_password"],
        id=data.get("id", str(uuid.uuid4())),
        role=data.get("role", UserRole.USER),
        is_active=bool(data.get("is_active", True)),
        full_name=data.get("full_name"),
        created_at=_parse_dt(data["created_at"]) if "created_at" in data else now,
        updated_at=_parse_dt(data["updated_at"]) if "updated_at" in data else now,
    )


# ---------------------------------------------------------------------------
# Self-test (run directly: python3 auth_models.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    PASS = "\033[32m✓\033[0m"
    FAIL = "\033[31m✗\033[0m"
    errors: list[str] = []

    def check(label: str, condition: bool) -> None:
        status = PASS if condition else FAIL
        print(f"  {status}  {label}")
        if not condition:
            errors.append(label)

    print("\n=== PasswordHasher ===")
    h = PasswordHasher.hash_password("S3cur3P@ss!")
    check("hash_password returns non-empty string", bool(h))
    check("hash starts with 'pbkdf2_sha256'", h.startswith("pbkdf2_sha256:"))
    check("verify_password correct → True", PasswordHasher.verify_password("S3cur3P@ss!", h))
    check("verify_password wrong   → False", not PasswordHasher.verify_password("WrongPass1", h))
    check("verify_password empty   → False", not PasswordHasher.verify_password("", h))
    check("needs_rehash fresh hash → False", not PasswordHasher.needs_rehash(h))
    check("needs_rehash garbage    → True", PasswordHasher.needs_rehash("garbage"))

    try:
        PasswordHasher.hash_password("short")
        check("short password raises ValueError", False)
    except ValueError:
        check("short password raises ValueError", True)

    print("\n=== UserCreate ===")
    uc = parse_user_create({
        "username": "alice",
        "email": "Alice@Example.COM",
        "password": "MyP@ssw0rd",
        "role": "admin",
        "full_name": "Alice Smith",
    })
    check("username normalised", uc.username == "alice")
    check("email lowercased", uc.email == "alice@example.com")
    check("role parsed to enum", uc.role == UserRole.ADMIN)
    check("full_name preserved", uc.full_name == "Alice Smith")

    try:
        parse_user_create({"username": "bob", "email": "bob@x.com"})
        check("missing password raises KeyError", False)
    except KeyError:
        check("missing password raises KeyError", True)

    try:
        parse_user_create({"username": "x", "email": "bad", "password": "P@ssw0rd1"})
        check("bad username raises ValueError", False)
    except ValueError:
        check("bad username raises ValueError", True)

    print("\n=== UserCreate → UserInDB ===")
    uid = uc.to_user_in_db()
    check("UserInDB has hashed_password", bool(uid.hashed_password))
    check("plain password not stored", not hasattr(uid, "password") or uid.hashed_password != "MyP@ssw0rd")
    check("verify_password via UserInDB", uid.verify_password("MyP@ssw0rd"))
    check("wrong password via UserInDB", not uid.verify_password("WrongPass!"))
    check("id is UUID-like", len(uid.id) == 36)
    check("created_at is datetime", isinstance(uid.created_at, datetime))

    print("\n=== UserPublic ===")
    pub = uid.to_public()
    check("UserPublic has no hashed_password attr", not hasattr(pub, "hashed_password"))
    check("UserPublic has no password attr", not hasattr(pub, "password"))
    d = pub.to_dict()
    check("to_dict contains 'role' as string", d["role"] == "admin")
    check("to_dict contains 'created_at' as ISO string", isinstance(d["created_at"], str))

    print("\n=== parse_user_in_db ===")
    raw_db = {
        "username": "charlie",
        "email": "charlie@example.com",
        "hashed_password": uid.hashed_password,
        "id": "00000000-0000-0000-0000-000000000001",
        "role": "moderator",
        "created_at": "2024-01-15T10:30:00+00:00",
        "updated_at": "2024-06-01T08:00:00+00:00",
    }
    db_user = parse_user_in_db(raw_db)
    check("id preserved", db_user.id == "00000000-0000-0000-0000-000000000001")
    check("role parsed", db_user.role == UserRole.MODERATOR)
    check("created_at parsed", db_user.created_at.year == 2024)

    try:
        parse_user_in_db({"username": "x", "email": "x@x.com"})
        check("missing hashed_password raises KeyError", False)
    except KeyError:
        check("missing hashed_password raises KeyError", True)

    try:
        parse_user_in_db("not a dict")
        check("non-dict input raises TypeError", False)
    except TypeError:
        check("non-dict input raises TypeError", True)

    print()
    if errors:
        print(f"FAILED — {len(errors)} test(s) failed: {errors}")
        sys.exit(1)
    else:
        print("All tests passed ✓")
        sys.exit(0)
