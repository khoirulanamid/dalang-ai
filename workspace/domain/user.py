"""
domain/user.py
==============
Task T-801 — User Aggregate, Persistence Model (UserInDB), and Safe Public DTO (UserPublic).

Architecture & DDD Standards:
  • Ubiquitous Language: Class, field, and method names reflect core auth business concepts.
  • Entity / Aggregate Root: `UserAggregate` enforces consistency boundaries and domain rules.
  • Strict Projection:
      - `UserInDB`: Persistence layer model containing cryptographically hashed credentials.
      - `UserPublic`: API outbound data transfer object (DTO). Whitelist-only fields.
        Zero exposure of raw or hashed credentials.
  • ISO 8601 UTC Enforcement: All timestamps are strictly UTC and serialized to ISO 8601.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Set

from domain.value_objects import (
    EmailAddress,
    HashedPassword,
    Timestamp,
    UserId,
    Username,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    """Business roles for authorization within the system."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

    @classmethod
    def from_str(cls, val: str) -> UserRole:
        try:
            return cls(val.strip().lower())
        except ValueError:
            valid = ", ".join(r.value for r in cls)
            raise ValueError(f"Invalid UserRole '{val}'. Must be one of: {valid}")


# ---------------------------------------------------------------------------
# Outbound DTO: UserPublic (Safe API Projection)
# ---------------------------------------------------------------------------

# Explicit whitelist of permitted public fields
_PUBLIC_FIELDS_WHITELIST: Set[str] = {
    "id",
    "username",
    "email",
    "role",
    "is_active",
    "full_name",
    "created_at",
    "updated_at",
}

# Explicit blacklist of prohibited sensitive fields
_FORBIDDEN_PUBLIC_FIELDS: Set[str] = {
    "password",
    "plain_password",
    "hashed_password",
    "secret",
    "salt",
    "token",
}


@dataclass(frozen=True)
class UserPublic:
    """
    Publicly safe outbound User Data Transfer Object (DTO).

    Security Invariants:
      1. CANNOT hold password or hashed_password (enforced structurally and at runtime).
      2. Whitelisted fields only.
      3. Timestamps are timezone-aware UTC datetimes, serialized as ISO 8601 UTC.
    """

    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        # Runtime invariant check: verify no sensitive attributes leaked
        for forbidden in _FORBIDDEN_PUBLIC_FIELDS:
            if hasattr(self, forbidden):
                raise TypeError(f"Security violation: UserPublic cannot contain '{forbidden}'.")

        # Invariant: username non-empty
        if not self.username or not isinstance(self.username, str):
            raise ValueError("UserPublic.username must be a non-empty string.")

        # Invariant: email non-empty
        if not self.email or not isinstance(self.email, str):
            raise ValueError("UserPublic.email must be a non-empty string.")

        # Invariant: timestamps must be timezone-aware
        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=timezone.utc))
        if self.updated_at.tzinfo is None:
            object.__setattr__(self, "updated_at", self.updated_at.replace(tzinfo=timezone.utc))

        # Invariant: role must be UserRole
        if isinstance(self.role, str) and not isinstance(self.role, UserRole):
            object.__setattr__(self, "role", UserRole(self.role))

    def to_dict(self) -> dict[str, Any]:
        """
        Explicit whitelist projection dictionary for JSON API responses.
        ISO 8601 UTC timestamps are enforced with canonical 'Z' suffix.
        """
        created_iso = Timestamp.from_datetime(self.created_at).to_iso()
        updated_iso = Timestamp.from_datetime(self.updated_at).to_iso()

        projected: dict[str, Any] = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, UserRole) else str(self.role),
            "is_active": self.is_active,
            "full_name": self.full_name,
            "created_at": created_iso,
            "updated_at": updated_iso,
        }

        # Double check that no forbidden field ever exists in projected dict
        assert not any(k in projected for k in _FORBIDDEN_PUBLIC_FIELDS), "Credential leak detected!"
        return projected


# ---------------------------------------------------------------------------
# Persistence Model: UserInDB
# ---------------------------------------------------------------------------

@dataclass
class UserInDB:
    """
    Internal persistence model representing a user record stored in the database.

    Security & Invariant Rules:
      1. Plain-text password is NEVER stored.
      2. hashed_password MUST be a non-empty PBKDF2 or standard hash string.
      3. Timestamps are always UTC datetime instances.
      4. `to_public()` performs an explicit projection whitelist to prevent credential leakage.
    """

    username: str
    email: str
    hashed_password: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: UserRole = UserRole.USER
    is_active: bool = True
    full_name: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        # Invariant: plain passwords rejected
        if not self.hashed_password or not isinstance(self.hashed_password, str):
            raise ValueError("UserInDB.hashed_password must be a non-empty string.")

        # Invariant: reject obvious plain text in hashed_password field
        if not (self.hashed_password.startswith("pbkdf2_") or self.hashed_password.startswith("$")):
            raise ValueError(
                "Security violation: hashed_password does not appear to be a cryptographic hash."
            )

        # Invariant: normalize role to UserRole enum
        if isinstance(self.role, str) and not isinstance(self.role, UserRole):
            self.role = UserRole(self.role)

        # Invariant: ensure UTC timezone
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

        # Invariant: normalize email
        self.email = self.email.strip().lower()

    def verify_password(self, plain_password: str) -> bool:
        """Verify candidate plain password against this user's stored hash."""
        hp = HashedPassword(self.hashed_password)
        return hp.verify(plain_password)

    def to_public(self) -> UserPublic:
        """
        Explicit projection whitelist: construct a UserPublic DTO.
        Eliminates hashed_password and any credentials from outbound data.
        """
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

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize record for persistence layer (e.g. database row or document).
        Includes hashed_password and ISO 8601 UTC timestamps.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "role": self.role.value if isinstance(self.role, UserRole) else str(self.role),
            "is_active": self.is_active,
            "full_name": self.full_name,
            "created_at": Timestamp.from_datetime(self.created_at).to_iso(),
            "updated_at": Timestamp.from_datetime(self.updated_at).to_iso(),
        }


# ---------------------------------------------------------------------------
# Domain Aggregate Root: UserAggregate
# ---------------------------------------------------------------------------

class UserAggregate:
    """
    Domain Entity and Aggregate Root for User.

    Encapsulates core business rules, domain invariants, and identity lifecycle.
    """

    def __init__(
        self,
        id: UserId,
        username: Username,
        email: EmailAddress,
        hashed_password: HashedPassword,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
        full_name: Optional[str] = None,
        created_at: Optional[Timestamp] = None,
        updated_at: Optional[Timestamp] = None,
    ) -> None:
        if not isinstance(id, UserId):
            raise TypeError(f"id must be UserId, got {type(id).__name__}")
        if not isinstance(username, Username):
            raise TypeError(f"username must be Username, got {type(username).__name__}")
        if not isinstance(email, EmailAddress):
            raise TypeError(f"email must be EmailAddress, got {type(email).__name__}")
        if not isinstance(hashed_password, HashedPassword):
            raise TypeError(f"hashed_password must be HashedPassword, got {type(hashed_password).__name__}")
        if not isinstance(role, UserRole):
            raise TypeError(f"role must be UserRole, got {type(role).__name__}")

        now = Timestamp.now()
        self._id = id
        self._username = username
        self._email = email
        self._hashed_password = hashed_password
        self._role = role
        self._is_active = bool(is_active)
        self._full_name = full_name.strip() if full_name else None
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    # Identity
    @property
    def id(self) -> UserId:
        return self._id

    @property
    def username(self) -> Username:
        return self._username

    @property
    def email(self) -> EmailAddress:
        return self._email

    @property
    def hashed_password(self) -> HashedPassword:
        return self._hashed_password

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def full_name(self) -> Optional[str]:
        return self._full_name

    @property
    def created_at(self) -> Timestamp:
        return self._created_at

    @property
    def updated_at(self) -> Timestamp:
        return self._updated_at

    # Domain methods / state transitions
    def verify_password(self, plain_password: str) -> bool:
        return self._hashed_password.verify(plain_password)

    def change_password(self, new_plain_password: str) -> None:
        """Change password enforcing domain policy."""
        new_hp = HashedPassword.create(new_plain_password)
        self._hashed_password = new_hp
        self._updated_at = Timestamp.now()

    def update_profile(self, full_name: Optional[str] = None, email: Optional[EmailAddress] = None) -> None:
        """Update user profile metadata."""
        if email is not None:
            if not isinstance(email, EmailAddress):
                raise TypeError("email must be an EmailAddress value object")
            self._email = email
        if full_name is not None:
            self._full_name = full_name.strip() if full_name else None
        self._updated_at = Timestamp.now()

    def assign_role(self, new_role: UserRole) -> None:
        if not isinstance(new_role, UserRole):
            raise TypeError("role must be a valid UserRole")
        self._role = new_role
        self._updated_at = Timestamp.now()

    def deactivate(self) -> None:
        self._is_active = False
        self._updated_at = Timestamp.now()

    def activate(self) -> None:
        self._is_active = True
        self._updated_at = Timestamp.now()

    # Projection factories
    def to_user_in_db(self) -> UserInDB:
        """Project to persistence model."""
        return UserInDB(
            id=str(self._id),
            username=str(self._username),
            email=str(self._email),
            hashed_password=self._hashed_password.get_raw_hash(),
            role=self._role,
            is_active=self._is_active,
            full_name=self._full_name,
            created_at=self._created_at.dt,
            updated_at=self._updated_at.dt,
        )

    def to_public(self) -> UserPublic:
        """Project directly to safe public DTO."""
        return UserPublic(
            id=str(self._id),
            username=str(self._username),
            email=str(self._email),
            role=self._role,
            is_active=self._is_active,
            full_name=self._full_name,
            created_at=self._created_at.dt,
            updated_at=self._updated_at.dt,
        )

    @classmethod
    def register(
        cls,
        username: str,
        email: str,
        plain_password: str,
        role: UserRole = UserRole.USER,
        full_name: Optional[str] = None,
    ) -> UserAggregate:
        """
        Factory method to create a new User aggregate from registration data.
        Validates all invariants and hashes password securely.
        """
        vo_id = UserId.generate()
        vo_username = Username(username)
        vo_email = EmailAddress(email)
        vo_hashed = HashedPassword.create(plain_password)
        return cls(
            id=vo_id,
            username=vo_username,
            email=vo_email,
            hashed_password=vo_hashed,
            role=role,
            is_active=True,
            full_name=full_name,
        )

    @classmethod
    def from_db_model(cls, db_model: UserInDB) -> UserAggregate:
        """Reconstitute UserAggregate from a UserInDB persistence model."""
        return cls(
            id=UserId(db_model.id),
            username=Username(db_model.username),
            email=EmailAddress(db_model.email),
            hashed_password=HashedPassword(db_model.hashed_password),
            role=db_model.role,
            is_active=db_model.is_active,
            full_name=db_model.full_name,
            created_at=Timestamp.from_datetime(db_model.created_at),
            updated_at=Timestamp.from_datetime(db_model.updated_at),
        )
