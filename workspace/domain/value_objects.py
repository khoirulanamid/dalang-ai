"""
domain/value_objects.py
=======================
Task T-801 — Domain Value Objects following DDD and RFC/ISO standards.

Standards applied:
  • Domain-Driven Design (Eric Evans) – Value objects are immutable, identity-less,
    and self-validating (strict invariants enforced at instantiation).
  • ISO 8601 – Timestamps are strictly UTC and formatted as YYYY-MM-DDTHH:MM:SS.ffffffZ.
  • RFC 5322 – Email address format validation.
  • Cryptographic Salt & Hash Isolation – Salt is minimum 16 bytes from os.urandom;
    passwords are never stored as plaintext in value objects.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Union


# ---------------------------------------------------------------------------
# Timestamp Value Object (ISO 8601 UTC)
# ---------------------------------------------------------------------------

# ISO 8601 UTC pattern: YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+00:00)
_ISO_8601_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class Timestamp:
    """
    Immutable ISO 8601 UTC timestamp value object.

    Invariants:
      1. Always in UTC timezone.
      2. Strictly formatted as YYYY-MM-DDTHH:MM:SS.ffffffZ.
      3. Naive datetimes are rejected or explicitly converted to UTC.
    """

    dt: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.dt, datetime):
            raise TypeError(f"Timestamp requires datetime, got {type(self.dt).__name__}")
        # Enforce UTC timezone awareness
        if self.dt.tzinfo is None:
            raise ValueError("Timestamp requires a timezone-aware datetime (UTC).")
        # Normalize to UTC
        utc_dt = self.dt.astimezone(timezone.utc)
        # frozen=True requires object.__setattr__
        object.__setattr__(self, "dt", utc_dt)

    @classmethod
    def now(cls) -> Timestamp:
        """Create a Timestamp representing current UTC time."""
        return cls(datetime.now(timezone.utc))

    @classmethod
    def from_datetime(cls, dt: datetime) -> Timestamp:
        """Create a Timestamp from a datetime instance, converting naive to UTC."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(dt)

    @classmethod
    def from_iso(cls, iso_str: str) -> Timestamp:
        """
        Parse an ISO 8601 string and return a UTC Timestamp.
        Raises ValueError if format does not comply with ISO 8601.
        """
        if not isinstance(iso_str, str):
            raise TypeError(f"Expected str for ISO timestamp, got {type(iso_str).__name__}")
        iso_str = iso_str.strip()
        if not _ISO_8601_PATTERN.match(iso_str):
            raise ValueError(f"String '{iso_str}' is not a valid ISO 8601 timestamp.")
        # Normalize trailing Z for fromisoformat compatibility across Python versions
        parseable = iso_str.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(parseable)
        except ValueError as exc:
            raise ValueError(f"Malformed ISO 8601 timestamp: '{iso_str}'") from exc
        return cls(dt)

    def to_iso(self) -> str:
        """
        Return canonical ISO 8601 UTC string: YYYY-MM-DDTHH:MM:SS.ffffffZ
        """
        micro = f".{self.dt.microsecond:06d}"
        return self.dt.strftime(f"%Y-%m-%dT%H:%M:%S{micro}Z")

    def __str__(self) -> str:
        return self.to_iso()

    def __repr__(self) -> str:
        return f"Timestamp('{self.to_iso()}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Timestamp):
            return self.dt == other.dt
        if isinstance(other, datetime):
            return self.dt == (other if other.tzinfo else other.replace(tzinfo=timezone.utc))
        return False

    def __lt__(self, other: Union[Timestamp, datetime]) -> bool:
        other_dt = other.dt if isinstance(other, Timestamp) else other
        return self.dt < other_dt

    def __le__(self, other: Union[Timestamp, datetime]) -> bool:
        other_dt = other.dt if isinstance(other, Timestamp) else other
        return self.dt <= other_dt

    def __gt__(self, other: Union[Timestamp, datetime]) -> bool:
        other_dt = other.dt if isinstance(other, Timestamp) else other
        return self.dt > other_dt

    def __ge__(self, other: Union[Timestamp, datetime]) -> bool:
        other_dt = other.dt if isinstance(other, Timestamp) else other
        return self.dt >= other_dt


# ---------------------------------------------------------------------------
# Email Address Value Object (RFC 5322)
# ---------------------------------------------------------------------------

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


@dataclass(frozen=True)
class EmailAddress:
    """
    Immutable Email Address value object.

    Invariants:
      1. Must be a valid string conforming to email specification.
      2. Automatically lowercased and stripped upon initialization.
      3. Cannot be empty or malformed.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"EmailAddress requires str, got {type(self.value).__name__}")
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("EmailAddress cannot be empty.")
        if len(normalized) > 254:
            raise ValueError("EmailAddress exceeds RFC 5321 length limit (254 chars).")
        if not _EMAIL_REGEX.match(normalized):
            raise ValueError(f"Invalid email address format: '{self.value}'")
        object.__setattr__(self, "value", normalized)

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        return self.value.split("@")[0]

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"EmailAddress('{self.value}')"


# ---------------------------------------------------------------------------
# UserId Value Object (UUID)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UserId:
    """
    Immutable unique identifier value object (UUIDv4).

    Invariants:
      1. Must be a valid UUID.
      2. Canonical string representation is standard hyphenated lowercase UUID.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"UserId requires str, got {type(self.value).__name__}")
        try:
            parsed = uuid.UUID(self.value)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Invalid UUID for UserId: '{self.value}'") from exc
        object.__setattr__(self, "value", str(parsed))

    @classmethod
    def generate(cls) -> UserId:
        """Generate a new cryptographically random UUIDv4 UserId."""
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"UserId('{self.value}')"


# ---------------------------------------------------------------------------
# Username Value Object
# ---------------------------------------------------------------------------

_USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{1,30}[a-zA-Z0-9]$")


@dataclass(frozen=True)
class Username:
    """
    Immutable Username value object.

    Invariants:
      1. Length between 3 and 32 characters.
      2. Alphanumeric, underscores, hyphens only.
      3. Must not start or end with a hyphen or underscore.
      4. Stored stripped.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError(f"Username requires str, got {type(self.value).__name__}")
        stripped = self.value.strip()
        if len(stripped) < 3 or len(stripped) > 32:
            raise ValueError("Username must be between 3 and 32 characters.")
        if not _USERNAME_REGEX.match(stripped):
            raise ValueError(
                "Username may only contain letters, numbers, underscores, and hyphens, "
                "and cannot start or end with a hyphen or underscore."
            )
        object.__setattr__(self, "value", stripped)

    @property
    def canonical(self) -> str:
        """Case-insensitive canonical form for storage keys / indexing."""
        return self.value.lower()

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Username('{self.value}')"


# ---------------------------------------------------------------------------
# HashedPassword Value Object (Security-by-Design)
# ---------------------------------------------------------------------------

# Accepted hash formats:
# 1. pbkdf2_sha256:<iterations>:<hex-salt>:<hex-digest>
# 2. $pbkdf2-sha256$i=<iterations>,l=<len>$<b64/hex-salt>$<hash> (modular crypt format)
_COLON_HASH_PATTERN = re.compile(r"^pbkdf2_sha256:\d+:[0-9a-fA-F]{32,}:[0-9a-fA-F]{64}$")
_MODULAR_HASH_PATTERN = re.compile(r"^\$[a-zA-Z0-9_-]+\$\d+\$[a-zA-Z0-9+/=._-]+\$[a-zA-Z0-9+/=._-]+$")


@dataclass(frozen=True)
class HashedPassword:
    """
    Immutable HashedPassword value object.

    Invariants:
      1. NEVER contains plaintext password.
      2. Encapsulates hash algorithm, iteration count, salt, and digest.
      3. Salt must be cryptographically random and at least 16 bytes (32 hex characters).
      4. Verification uses hmac.compare_digest for timing-attack resistance.
    """

    hash_value: str

    # Security parameters
    DEFAULT_ALGO: str = "sha256"
    DEFAULT_ITERATIONS: int = 260_000
    MIN_SALT_BYTES: int = 16
    DEFAULT_SALT_BYTES: int = 32

    def __post_init__(self) -> None:
        if not isinstance(self.hash_value, str):
            raise TypeError(f"HashedPassword requires str, got {type(self.hash_value).__name__}")
        if not self._is_valid_hash_format(self.hash_value):
            raise ValueError(
                "Invalid hashed password format. Plaintext passwords must not be wrapped "
                "in HashedPassword directly. Use HashedPassword.create(plaintext)."
            )

    @classmethod
    def _is_valid_hash_format(cls, val: str) -> bool:
        if _COLON_HASH_PATTERN.match(val):
            # Check minimum salt length (16 bytes = 32 hex chars)
            parts = val.split(":")
            salt_hex = parts[2]
            return len(salt_hex) >= cls.MIN_SALT_BYTES * 2
        if _MODULAR_HASH_PATTERN.match(val):
            return True
        return False

    @classmethod
    def create(cls, plain_password: str, salt_bytes: int = 32, iterations: int = 260_000) -> HashedPassword:
        """
        Hash a plain-text password using PBKDF2-HMAC-SHA256 with cryptographically
        random salt (minimum 16 bytes, default 32 bytes from os.urandom).
        """
        if not isinstance(plain_password, str):
            raise TypeError("Password must be a string.")
        if len(plain_password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if len(plain_password.encode("utf-8")) > 1024:
            raise ValueError("Password exceeds maximum allowed size.")
        if salt_bytes < cls.MIN_SALT_BYTES:
            raise ValueError(f"Salt must be at least {cls.MIN_SALT_BYTES} bytes.")

        salt = os.urandom(salt_bytes)
        derived = hashlib.pbkdf2_hmac(
            cls.DEFAULT_ALGO,
            plain_password.encode("utf-8"),
            salt,
            iterations,
            dklen=32,
        )
        hash_str = f"pbkdf2_{cls.DEFAULT_ALGO}:{iterations}:{salt.hex()}:{derived.hex()}"
        return cls(hash_str)

    def verify(self, plain_password: str) -> bool:
        """
        Verify candidate plain password against this hash in constant time.
        """
        if not isinstance(plain_password, str) or not plain_password:
            return False

        if self.hash_value.startswith("pbkdf2_sha256:"):
            try:
                algo, iter_str, salt_hex, digest_hex = self.hash_value.split(":")
                iterations = int(iter_str)
                salt = bytes.fromhex(salt_hex)
                expected_digest = bytes.fromhex(digest_hex)
            except (ValueError, TypeError):
                return False

            actual_digest = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(expected_digest),
            )
            return hmac.compare_digest(actual_digest, expected_digest)

        return False

    def __str__(self) -> str:
        # Redact the actual digest to prevent accidental logging in string conversions
        return "[REDACTED_HASHED_PASSWORD]"

    def get_raw_hash(self) -> str:
        """Explicit getter for persistence layer only."""
        return self.hash_value

    def __repr__(self) -> str:
        return "HashedPassword('[REDACTED]')"
