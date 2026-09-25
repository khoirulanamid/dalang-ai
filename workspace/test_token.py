"""
test_token.py
=============
Tests for token_service.py (Task T-102).

Covers:
  1. TokenConfig validation
  2. Access token generation and verification
  3. Refresh token generation and verification
  4. Token expiry handling (TokenExpiredError)
  5. Signature tampering and invalid tokens (TokenInvalidError)
  6. TokenType mismatch enforcement (TokenTypeMismatchError)
  7. Token refresh flow (refresh_access_token)
  8. decode_unverified functionality
  9. Extra custom claims handling
 10. Factory function create_token_service and env var overrides
 11. Role compatibility with auth_models.UserRole
"""

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

from auth_models import UserRole
from token_service import (
    TokenConfig,
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenPayload,
    TokenService,
    TokenType,
    TokenTypeMismatchError,
    create_token_service,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def secret_key():
    return "super-secret-key-for-testing-purposes-12345678-32bytes"


@pytest.fixture
def default_config(secret_key):
    return TokenConfig(
        secret_key=secret_key,
        algorithm="HS256",
        access_token_expire=timedelta(minutes=15),
        refresh_token_expire=timedelta(days=7),
    )


@pytest.fixture
def token_service(default_config):
    return TokenService(default_config)


# ---------------------------------------------------------------------------
# 1. TokenConfig validation tests
# ---------------------------------------------------------------------------

class TestTokenConfig:
    def test_valid_config(self, secret_key):
        cfg = TokenConfig(
            secret_key=secret_key,
            algorithm="HS256",
            access_token_expire=timedelta(minutes=30),
            refresh_token_expire=timedelta(days=14),
            issuer="test-issuer",
            audience="test-aud",
        )
        assert cfg.secret_key == secret_key
        assert cfg.algorithm == "HS256"
        assert cfg.issuer == "test-issuer"
        assert cfg.audience == "test-aud"

    def test_empty_secret_raises(self):
        with pytest.raises(ValueError, match="secret_key must not be empty"):
            TokenConfig(secret_key="")

        with pytest.raises(ValueError, match="secret_key must not be empty"):
            TokenConfig(secret_key="   ")

    def test_unsupported_algorithm_raises(self, secret_key):
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            TokenConfig(secret_key=secret_key, algorithm="INVALID_ALG")

    def test_non_positive_expire_raises(self, secret_key):
        with pytest.raises(ValueError, match="access_token_expire must be a positive duration"):
            TokenConfig(secret_key=secret_key, access_token_expire=timedelta(seconds=0))

        with pytest.raises(ValueError, match="access_token_expire must be a positive duration"):
            TokenConfig(secret_key=secret_key, access_token_expire=timedelta(minutes=-5))

        with pytest.raises(ValueError, match="refresh_token_expire must be a positive duration"):
            TokenConfig(secret_key=secret_key, refresh_token_expire=timedelta(days=0))


# ---------------------------------------------------------------------------
# 2. Access Token Generation & Verification
# ---------------------------------------------------------------------------

class TestAccessToken:
    def test_generate_and_verify_access_token(self, token_service):
        sub = "user-uuid-1234"
        token = token_service.generate_access_token(sub=sub, role=UserRole.ADMIN)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # Valid JWT format: header.payload.signature

        payload = token_service.verify_token(token, expected_type=TokenType.ACCESS)
        assert isinstance(payload, TokenPayload)
        assert payload.sub == sub
        assert payload.role == UserRole.ADMIN
        assert payload.token_type == TokenType.ACCESS
        assert payload.is_access_token is True
        assert payload.is_refresh_token is False
        assert payload.is_expired is False
        assert payload.jti is not None
        assert isinstance(payload.iat, datetime)
        assert isinstance(payload.exp, datetime)
        assert payload.exp > payload.iat

    def test_generate_with_string_role(self, token_service):
        token = token_service.generate_access_token(sub="user-1", role="user")
        payload = token_service.verify_token(token)
        assert payload.role == UserRole.USER

    def test_empty_sub_raises(self, token_service):
        with pytest.raises(ValueError, match="sub must not be empty"):
            token_service.generate_access_token(sub="", role=UserRole.USER)
        with pytest.raises(ValueError, match="sub must not be empty"):
            token_service.generate_access_token(sub="   ", role=UserRole.USER)

    def test_invalid_role_raises(self, token_service):
        with pytest.raises(ValueError):
            token_service.generate_access_token(sub="user-1", role="superhero")

    def test_all_user_roles_supported(self, token_service):
        for role in UserRole:
            token = token_service.generate_access_token(sub=f"user-{role.value}", role=role)
            payload = token_service.verify_token(token)
            assert payload.role == role


# ---------------------------------------------------------------------------
# 3. Refresh Token Generation & Verification
# ---------------------------------------------------------------------------

class TestRefreshToken:
    def test_generate_and_verify_refresh_token(self, token_service):
        sub = "user-uuid-refresh-001"
        token = token_service.generate_refresh_token(sub=sub)

        assert isinstance(token, str)
        assert len(token.split(".")) == 3

        payload = token_service.verify_token(token, expected_type=TokenType.REFRESH)
        assert payload.sub == sub
        assert payload.role is None
        assert payload.token_type == TokenType.REFRESH
        assert payload.is_refresh_token is True
        assert payload.is_access_token is False
        assert payload.is_expired is False

    def test_empty_sub_raises_on_refresh(self, token_service):
        with pytest.raises(ValueError, match="sub must not be empty"):
            token_service.generate_refresh_token(sub="")


# ---------------------------------------------------------------------------
# 4. Token Expiry Handling
# ---------------------------------------------------------------------------

class TestTokenExpiry:
    def test_expired_access_token_raises_error(self, secret_key):
        short_config = TokenConfig(
            secret_key=secret_key,
            access_token_expire=timedelta(milliseconds=1),
        )
        svc = TokenService(short_config)

        now = datetime.now(timezone.utc) - timedelta(minutes=10)
        past_claims = {
            "sub": "user-expired",
            "role": "user",
            "type": "access",
            "iat": now - timedelta(minutes=5),
            "exp": now,
            "jti": "jti-past",
        }
        expired_token = jwt.encode(past_claims, secret_key, algorithm="HS256")

        with pytest.raises(TokenExpiredError, match="Token has expired"):
            svc.verify_token(expired_token)

    def test_expired_refresh_token_raises_error(self, secret_key):
        svc = TokenService(TokenConfig(secret_key=secret_key))
        past = datetime.now(timezone.utc) - timedelta(days=1)
        claims = {
            "sub": "user-expired",
            "type": "refresh",
            "iat": past - timedelta(days=7),
            "exp": past,
            "jti": "jti-past-refresh",
        }
        expired_token = jwt.encode(claims, secret_key, algorithm="HS256")

        with pytest.raises(TokenExpiredError):
            svc.verify_token(expired_token, expected_type=TokenType.REFRESH)


# ---------------------------------------------------------------------------
# 5. Signature Tampering and Invalid Tokens
# ---------------------------------------------------------------------------

class TestTokenInvalid:
    def test_tampered_signature_raises(self, token_service):
        token = token_service.generate_access_token("user-1", role=UserRole.USER)
        parts = token.split(".")
        tampered_token = f"{parts[0]}.eyJhZG1pbiI6dHJ1ZX0.{parts[2]}"

        with pytest.raises(TokenInvalidError):
            token_service.verify_token(tampered_token)

    def test_wrong_secret_raises(self, default_config):
        svc1 = TokenService(default_config)
        token = svc1.generate_access_token("user-1", role=UserRole.USER)

        svc2 = TokenService(TokenConfig(secret_key="different-secret-key-12345678-long-enough-32bytes"))
        with pytest.raises(TokenInvalidError):
            svc2.verify_token(token)

    def test_malformed_string_raises(self, token_service):
        for bad in ["not-a-token", "a.b", "...", "", "abc.def.ghi.extra"]:
            with pytest.raises(TokenInvalidError):
                token_service.verify_token(bad)

    def test_unknown_token_type_raises(self, secret_key):
        svc = TokenService(TokenConfig(secret_key=secret_key))
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-1",
            "type": "unrecognized_type",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "jti": "jti-1",
        }
        token = jwt.encode(claims, secret_key, algorithm="HS256")
        with pytest.raises(TokenInvalidError, match="Unknown token type"):
            svc.verify_token(token)

    def test_unknown_role_in_token_raises(self, secret_key):
        svc = TokenService(TokenConfig(secret_key=secret_key))
        now = datetime.now(timezone.utc)
        claims = {
            "sub": "user-1",
            "type": "access",
            "role": "non_existent_role",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "jti": "jti-1",
        }
        token = jwt.encode(claims, secret_key, algorithm="HS256")
        with pytest.raises(TokenInvalidError, match="Unknown role"):
            svc.verify_token(token)


# ---------------------------------------------------------------------------
# 6. TokenType Mismatch Enforcement
# ---------------------------------------------------------------------------

class TestTokenTypeMismatch:
    def test_verify_access_as_refresh_fails(self, token_service):
        access_token = token_service.generate_access_token("u1", role=UserRole.USER)
        with pytest.raises(TokenTypeMismatchError, match="Expected token type 'refresh', got 'access'"):
            token_service.verify_token(access_token, expected_type=TokenType.REFRESH)

    def test_verify_refresh_as_access_fails(self, token_service):
        refresh_token = token_service.generate_refresh_token("u1")
        with pytest.raises(TokenTypeMismatchError, match="Expected token type 'access', got 'refresh'"):
            token_service.verify_token(refresh_token, expected_type=TokenType.ACCESS)

    def test_verify_without_expected_type_accepts_both(self, token_service):
        access = token_service.generate_access_token("u1", role=UserRole.USER)
        refresh = token_service.generate_refresh_token("u1")

        p_acc = token_service.verify_token(access)
        p_ref = token_service.verify_token(refresh)

        assert p_acc.token_type == TokenType.ACCESS
        assert p_ref.token_type == TokenType.REFRESH


# ---------------------------------------------------------------------------
# 7. Token Refresh Flow
# ---------------------------------------------------------------------------

class TestTokenRefreshFlow:
    def test_refresh_access_token_success(self, token_service):
        refresh_token = token_service.generate_refresh_token(sub="user-999")
        new_access = token_service.refresh_access_token(
            refresh_token=refresh_token,
            role=UserRole.MODERATOR,
        )

        assert isinstance(new_access, str)
        payload = token_service.verify_token(new_access, expected_type=TokenType.ACCESS)
        assert payload.sub == "user-999"
        assert payload.role == UserRole.MODERATOR
        assert payload.token_type == TokenType.ACCESS

    def test_refresh_with_access_token_raises_type_mismatch(self, token_service):
        access_token = token_service.generate_access_token("u1", role=UserRole.USER)
        with pytest.raises(TokenTypeMismatchError):
            token_service.refresh_access_token(access_token, role=UserRole.USER)

    def test_refresh_with_expired_refresh_token_raises(self, secret_key):
        svc = TokenService(TokenConfig(secret_key=secret_key))
        past = datetime.now(timezone.utc) - timedelta(days=1)
        claims = {
            "sub": "user-expired",
            "type": "refresh",
            "iat": past - timedelta(days=7),
            "exp": past,
            "jti": "jti-expired",
        }
        expired_refresh = jwt.encode(claims, secret_key, algorithm="HS256")

        with pytest.raises(TokenExpiredError):
            svc.refresh_access_token(expired_refresh, role=UserRole.USER)


# ---------------------------------------------------------------------------
# 8. Unverified Decoding
# ---------------------------------------------------------------------------

class TestDecodeUnverified:
    def test_decode_unverified_returns_dict(self, token_service):
        token = token_service.generate_access_token("user-42", role=UserRole.ADMIN)
        raw = token_service.decode_unverified(token)
        assert isinstance(raw, dict)
        assert raw["sub"] == "user-42"
        assert raw["role"] == "admin"
        assert raw["type"] == "access"

    def test_decode_unverified_malformed_raises(self, token_service):
        with pytest.raises(TokenInvalidError):
            token_service.decode_unverified("bad.token")


# ---------------------------------------------------------------------------
# 9. Extra Claims & Reserved Claims
# ---------------------------------------------------------------------------

class TestExtraClaims:
    def test_extra_claims_included_in_token(self, token_service):
        extra = {"org_id": "org-55", "email": "test@example.com"}
        token = token_service.generate_access_token(
            sub="user-55",
            role=UserRole.USER,
            extra_claims=extra,
        )
        payload = token_service.verify_token(token)
        assert payload.raw.get("org_id") == "org-55"
        assert payload.raw.get("email") == "test@example.com"

    def test_reserved_claims_not_overwritten(self, token_service):
        token = token_service.generate_access_token(
            sub="real-sub",
            role=UserRole.USER,
            extra_claims={"sub": "fake-sub", "type": "refresh"},
        )
        payload = token_service.verify_token(token)
        assert payload.sub == "real-sub"
        assert payload.token_type == TokenType.ACCESS

    def test_issuer_and_audience_claims(self, secret_key):
        cfg = TokenConfig(
            secret_key=secret_key,
            issuer="my-app",
            audience="my-frontend",
        )
        svc = TokenService(cfg)
        token = svc.generate_access_token("user-iss", role=UserRole.USER)
        payload = svc.verify_token(token)
        assert payload.issuer == "my-app"
        assert payload.audience == "my-frontend"


# ---------------------------------------------------------------------------
# 10. Factory Function & Environment Variables
# ---------------------------------------------------------------------------

class TestCreateTokenService:
    def test_factory_with_explicit_args(self):
        svc = create_token_service(
            secret_key="custom-secret-key-12345-long-enough-32bytes",
            algorithm="HS256",
            access_expire_minutes=60,
            refresh_expire_days=30,
            issuer="test-factory",
            audience="aud-factory",
        )
        assert svc._config.secret_key == "custom-secret-key-12345-long-enough-32bytes"
        assert svc._config.access_token_expire == timedelta(minutes=60)
        assert svc._config.refresh_token_expire == timedelta(days=30)
        assert svc._config.issuer == "test-factory"
        assert svc._config.audience == "aud-factory"

    def test_factory_with_env_vars(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET_KEY", "env-secret-key-12345-long-enough-32bytes")
        monkeypatch.setenv("JWT_ACCESS_EXPIRE_MINUTES", "45")
        monkeypatch.setenv("JWT_REFRESH_EXPIRE_DAYS", "10")
        monkeypatch.setenv("JWT_ISSUER", "env-issuer")
        monkeypatch.setenv("JWT_AUDIENCE", "env-aud")

        svc = create_token_service()
        assert svc._config.secret_key == "env-secret-key-12345-long-enough-32bytes"
        assert svc._config.access_token_expire == timedelta(minutes=45)
        assert svc._config.refresh_token_expire == timedelta(days=10)
        assert svc._config.issuer == "env-issuer"
        assert svc._config.audience == "env-aud"

    def test_factory_defaults(self, monkeypatch):
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("JWT_ACCESS_EXPIRE_MINUTES", raising=False)
        monkeypatch.delenv("JWT_REFRESH_EXPIRE_DAYS", raising=False)

        svc = create_token_service()
        assert svc._config.access_token_expire == timedelta(minutes=15)
        assert svc._config.refresh_token_expire == timedelta(days=7)


# ---------------------------------------------------------------------------
# 11. Hierarchy of Token Exceptions
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    def test_token_exceptions_inherit_from_token_error(self):
        assert issubclass(TokenExpiredError, TokenError)
        assert issubclass(TokenInvalidError, TokenError)
        assert issubclass(TokenTypeMismatchError, TokenError)
        assert issubclass(TokenError, Exception)
