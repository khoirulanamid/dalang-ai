"""
token_service.py
================
Task T-102 — JWT token generator and verifier.

Provides:
  • TokenConfig      – Configuration dataclass for JWT settings.
  • TokenType        – Enum for access / refresh token types.
  • TokenPayload     – Dataclass representing a decoded JWT payload.
  • TokenService     – Core service: generate, verify, and refresh JWTs.
  • create_token_service – Factory that builds a TokenService from env vars or defaults.

Token format
------------
All tokens are signed JWTs (HS256 by default, RS256 supported).

Access token claims:
    sub   (str)      – subject (user ID or username)
    role  (str)      – user role
    type  (str)      – "access"
    iat   (int)      – issued-at (UTC epoch)
    exp   (int)      – expiry   (UTC epoch)
    jti   (str)      – unique token ID (UUID4)

Refresh token claims:
    sub   (str)      – subject
    type  (str)      – "refresh"
    iat   (int)      – issued-at
    exp   (int)      – expiry
    jti   (str)      – unique token ID
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidTokenError,
)

from auth_models import UserRole


# ---------------------------------------------------------------------------
# Enums & constants
# ---------------------------------------------------------------------------

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


# Default durations
_DEFAULT_ACCESS_MINUTES: int = 15
_DEFAULT_REFRESH_DAYS: int = 7
_DEFAULT_ALGORITHM: str = "HS256"
_DEFAULT_SECRET: str = "change-me-in-production-please-use-a-long-random-secret"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class TokenConfig:
    """
    JWT configuration.

    Attributes:
        secret_key          – HMAC secret (required for HS256).
        algorithm           – Signing algorithm (default: HS256).
        access_token_expire – Lifetime of access tokens.
        refresh_token_expire– Lifetime of refresh tokens.
        issuer              – Optional 'iss' claim value.
        audience            – Optional 'aud' claim value.
    """
    secret_key: str
    algorithm: str = _DEFAULT_ALGORITHM
    access_token_expire: timedelta = field(
        default_factory=lambda: timedelta(minutes=_DEFAULT_ACCESS_MINUTES)
    )
    refresh_token_expire: timedelta = field(
        default_factory=lambda: timedelta(days=_DEFAULT_REFRESH_DAYS)
    )
    issuer: Optional[str] = None
    audience: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.secret_key or not self.secret_key.strip():
            raise ValueError("TokenConfig.secret_key must not be empty.")
        if self.algorithm not in jwt.algorithms.get_default_algorithms():
            raise ValueError(f"Unsupported algorithm: {self.algorithm!r}")
        if self.access_token_expire.total_seconds() <= 0:
            raise ValueError("access_token_expire must be a positive duration.")
        if self.refresh_token_expire.total_seconds() <= 0:
            raise ValueError("refresh_token_expire must be a positive duration.")


# ---------------------------------------------------------------------------
# Payload
# ---------------------------------------------------------------------------

@dataclass
class TokenPayload:
    """
    Decoded, validated JWT payload.

    Attributes:
        sub       – Subject (user ID / username).
        token_type– TokenType.ACCESS or TokenType.REFRESH.
        jti       – Unique token identifier.
        iat       – Issued-at datetime (UTC).
        exp       – Expiry datetime (UTC).
        role      – User role (present on access tokens; None on refresh tokens).
        issuer    – 'iss' claim if present.
        audience  – 'aud' claim if present.
        raw       – The original decoded claims dict.
    """
    sub: str
    token_type: TokenType
    jti: str
    iat: datetime
    exp: datetime
    role: Optional[UserRole] = None
    issuer: Optional[str] = None
    audience: Optional[str] = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.exp

    @property
    def is_access_token(self) -> bool:
        return self.token_type == TokenType.ACCESS

    @property
    def is_refresh_token(self) -> bool:
        return self.token_type == TokenType.REFRESH


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TokenError(Exception):
    """Base class for token-related errors."""


class TokenExpiredError(TokenError):
    """Raised when a token has expired."""


class TokenInvalidError(TokenError):
    """Raised when a token is malformed or has an invalid signature."""


class TokenTypeMismatchError(TokenError):
    """Raised when the token type does not match the expected type."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TokenService:
    """
    JWT token generator and verifier.

    Usage::

        svc = TokenService(TokenConfig(secret_key="my-secret"))

        access  = svc.generate_access_token(sub="user-123", role=UserRole.USER)
        refresh = svc.generate_refresh_token(sub="user-123")

        payload = svc.verify_token(access, expected_type=TokenType.ACCESS)
        new_access = svc.refresh_access_token(refresh_token=refresh, role=UserRole.USER)
    """

    def __init__(self, config: TokenConfig) -> None:
        self._config = config

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_access_token(
        self,
        sub: str,
        role: UserRole,
        extra_claims: Optional[dict] = None,
    ) -> str:
        """
        Generate a signed JWT access token.

        Args:
            sub         – Subject identifier (user ID or username).
            role        – User role embedded in the token.
            extra_claims– Optional additional claims to include.

        Returns:
            Encoded JWT string.
        """
        if not sub or not sub.strip():
            raise ValueError("sub must not be empty.")
        if not isinstance(role, UserRole):
            role = UserRole(role)

        now = datetime.now(timezone.utc)
        exp = now + self._config.access_token_expire

        claims: dict = {
            "sub": sub,
            "role": role.value,
            "type": TokenType.ACCESS.value,
            "iat": now,
            "exp": exp,
            "jti": str(uuid.uuid4()),
        }
        if self._config.issuer:
            claims["iss"] = self._config.issuer
        if self._config.audience:
            claims["aud"] = self._config.audience
        if extra_claims:
            # Prevent overwriting reserved claims
            reserved = {"sub", "role", "type", "iat", "exp", "jti", "iss", "aud"}
            for k, v in extra_claims.items():
                if k not in reserved:
                    claims[k] = v

        return self._encode(claims)

    def generate_refresh_token(
        self,
        sub: str,
        extra_claims: Optional[dict] = None,
    ) -> str:
        """
        Generate a signed JWT refresh token.

        Args:
            sub         – Subject identifier.
            extra_claims– Optional additional claims.

        Returns:
            Encoded JWT string.
        """
        if not sub or not sub.strip():
            raise ValueError("sub must not be empty.")

        now = datetime.now(timezone.utc)
        exp = now + self._config.refresh_token_expire

        claims: dict = {
            "sub": sub,
            "type": TokenType.REFRESH.value,
            "iat": now,
            "exp": exp,
            "jti": str(uuid.uuid4()),
        }
        if self._config.issuer:
            claims["iss"] = self._config.issuer
        if self._config.audience:
            claims["aud"] = self._config.audience
        if extra_claims:
            reserved = {"sub", "type", "iat", "exp", "jti", "iss", "aud"}
            for k, v in extra_claims.items():
                if k not in reserved:
                    claims[k] = v

        return self._encode(claims)

    def verify_token(
        self,
        token: str,
        expected_type: Optional[TokenType] = None,
    ) -> TokenPayload:
        """
        Decode and validate a JWT token.

        Args:
            token         – Encoded JWT string.
            expected_type – If provided, raises TokenTypeMismatchError when the
                            token's 'type' claim does not match.

        Returns:
            TokenPayload with decoded claims.

        Raises:
            TokenExpiredError       – Token has expired.
            TokenInvalidError       – Token is malformed or signature is invalid.
            TokenTypeMismatchError  – Token type does not match expected_type.
        """
        raw = self._decode(token)
        payload = self._build_payload(raw)

        if expected_type is not None and payload.token_type != expected_type:
            raise TokenTypeMismatchError(
                f"Expected token type {expected_type.value!r}, "
                f"got {payload.token_type.value!r}."
            )

        return payload

    def refresh_access_token(
        self,
        refresh_token: str,
        role: UserRole,
        extra_claims: Optional[dict] = None,
    ) -> str:
        """
        Validate a refresh token and issue a new access token.

        Args:
            refresh_token – Encoded refresh JWT.
            role          – Role to embed in the new access token.
            extra_claims  – Optional extra claims for the new access token.

        Returns:
            New encoded access JWT string.

        Raises:
            TokenExpiredError      – Refresh token has expired.
            TokenInvalidError      – Refresh token is invalid.
            TokenTypeMismatchError – Token is not a refresh token.
        """
        payload = self.verify_token(refresh_token, expected_type=TokenType.REFRESH)
        return self.generate_access_token(
            sub=payload.sub,
            role=role,
            extra_claims=extra_claims,
        )

    def decode_unverified(self, token: str) -> dict:
        """
        Decode a JWT without verifying the signature.
        Useful for inspecting headers / claims before full verification.

        Returns:
            Raw claims dict (unverified).
        """
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=[self._config.algorithm],
            )
        except DecodeError as exc:
            raise TokenInvalidError(f"Malformed token: {exc}") from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _encode(self, claims: dict) -> str:
        """Encode claims into a signed JWT string."""
        return jwt.encode(
            claims,
            self._config.secret_key,
            algorithm=self._config.algorithm,
        )

    def _decode(self, token: str) -> dict:
        """Decode and verify a JWT string, returning raw claims."""
        decode_kwargs: dict = {
            "algorithms": [self._config.algorithm],
        }
        if self._config.issuer:
            decode_kwargs["issuer"] = self._config.issuer
        if self._config.audience:
            decode_kwargs["audience"] = self._config.audience

        try:
            return jwt.decode(token, self._config.secret_key, **decode_kwargs)
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired.") from exc
        except DecodeError as exc:
            raise TokenInvalidError(f"Malformed token: {exc}") from exc
        except InvalidTokenError as exc:
            raise TokenInvalidError(f"Invalid token: {exc}") from exc

    @staticmethod
    def _build_payload(raw: dict) -> TokenPayload:
        """Convert raw claims dict into a TokenPayload dataclass."""
        try:
            token_type = TokenType(raw.get("type", ""))
        except ValueError:
            raise TokenInvalidError(
                f"Unknown token type: {raw.get('type')!r}. "
                f"Expected 'access' or 'refresh'."
            )

        role_str = raw.get("role")
        role: Optional[UserRole] = None
        if role_str is not None:
            try:
                role = UserRole(role_str)
            except ValueError:
                raise TokenInvalidError(f"Unknown role: {role_str!r}.")

        def _epoch_to_dt(value) -> datetime:
            if isinstance(value, datetime):
                return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
            return datetime.fromtimestamp(int(value), tz=timezone.utc)

        return TokenPayload(
            sub=raw["sub"],
            token_type=token_type,
            jti=raw["jti"],
            iat=_epoch_to_dt(raw["iat"]),
            exp=_epoch_to_dt(raw["exp"]),
            role=role,
            issuer=raw.get("iss"),
            audience=raw.get("aud"),
            raw=raw,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_token_service(
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    access_expire_minutes: Optional[int] = None,
    refresh_expire_days: Optional[int] = None,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
) -> TokenService:
    """
    Build a TokenService from explicit arguments or environment variables.

    Environment variables (used as fallback):
        JWT_SECRET_KEY           – HMAC secret key.
        JWT_ALGORITHM            – Signing algorithm (default: HS256).
        JWT_ACCESS_EXPIRE_MINUTES– Access token lifetime in minutes (default: 15).
        JWT_REFRESH_EXPIRE_DAYS  – Refresh token lifetime in days (default: 7).
        JWT_ISSUER               – Optional issuer claim.
        JWT_AUDIENCE             – Optional audience claim.
    """
    resolved_secret = (
        secret_key
        or os.environ.get("JWT_SECRET_KEY")
    )
    if not resolved_secret:
        if os.environ.get("APP_ENV", "").lower() in ("production", "prod"):
            raise ValueError(
                "CRITICAL: JWT_SECRET_KEY environment variable MUST be set in production. "
                "Default secret keys are rejected by security policy."
            )
        resolved_secret = _DEFAULT_SECRET
    resolved_algorithm = (
        algorithm
        or os.environ.get("JWT_ALGORITHM")
        or _DEFAULT_ALGORITHM
    )
    resolved_access = int(
        access_expire_minutes
        if access_expire_minutes is not None
        else os.environ.get("JWT_ACCESS_EXPIRE_MINUTES", _DEFAULT_ACCESS_MINUTES)
    )
    resolved_refresh = int(
        refresh_expire_days
        if refresh_expire_days is not None
        else os.environ.get("JWT_REFRESH_EXPIRE_DAYS", _DEFAULT_REFRESH_DAYS)
    )
    resolved_issuer = issuer or os.environ.get("JWT_ISSUER") or None
    resolved_audience = audience or os.environ.get("JWT_AUDIENCE") or None

    config = TokenConfig(
        secret_key=resolved_secret,
        algorithm=resolved_algorithm,
        access_token_expire=timedelta(minutes=resolved_access),
        refresh_token_expire=timedelta(days=resolved_refresh),
        issuer=resolved_issuer,
        audience=resolved_audience,
    )
    return TokenService(config)
