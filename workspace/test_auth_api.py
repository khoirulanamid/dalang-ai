"""
test_auth_api.py
================
Task T-301 — Comprehensive tests for FastAPI auth server (auth_api.py).

Covers:
  1. POST /register
     - Successful registration with default role (201)
     - Successful registration with explicit roles (admin, moderator, guest)
     - Response schema: safe fields only, no password fields
     - Duplicate username conflict (409)
     - Duplicate email conflict (409)
     - Case-insensitive email duplicate check
     - Validation: password too short (< 8 chars) (422)
     - Validation: invalid email format (422)
     - Validation: invalid username characters / length (422)
     - Validation: invalid role (422)
     - Missing required fields (422)

  2. POST /login
     - Successful login with username (200)
     - Successful login with email address (200)
     - Correct token structure (access_token, refresh_token, token_type="bearer")
     - Access token contains correct claims (sub, role, type=access)
     - Refresh token contains correct claims (sub, type=refresh, no role)
     - Wrong password (401)
     - Non-existent user (401)
     - Inactive user cannot log in (403)

  3. POST /refresh
     - Successful refresh with valid refresh token (200)
     - New access token allows calling /me
     - Refresh with an access token fails (401)
     - Refresh with expired refresh token (401)
     - Refresh with malformed token (401)
     - Refresh with unknown user (401)
     - Refresh with disabled/inactive user (403)

  4. GET /me
     - Successful retrieval with valid access token (200)
     - Response matches registered user data (id, username, email, role, is_active)
     - Missing Authorization header (401)
     - Invalid Bearer token (401)
     - Expired access token (401)
     - Refresh token presented instead of access token (401)
     - Inactive user (403)
     - Non-existent user (401)

  5. Health endpoint (GET /health)
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

import auth_api
from auth_api import _USER_STORE, app, get_token_service
from auth_models import UserInDB, UserRole
from token_service import TokenConfig, TokenService, TokenType


# ---------------------------------------------------------------------------
# Test setup & fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_user_store():
    """Ensure an empty user store before each test."""
    _USER_STORE.clear()
    yield
    _USER_STORE.clear()


@pytest.fixture
def secret_key():
    return "test-secret-key-32-chars-long-12345678"


@pytest.fixture(autouse=True)
def token_service(secret_key):
    """Provide a consistent TokenService and wire it into FastAPI dependencies."""
    config = TokenConfig(
        secret_key=secret_key,
        algorithm="HS256",
        access_token_expire=timedelta(minutes=15),
        refresh_token_expire=timedelta(days=7),
    )
    svc = TokenService(config)
    app.dependency_overrides[get_token_service] = lambda: svc
    yield svc
    app.dependency_overrides.pop(get_token_service, None)


@pytest.fixture
def client():
    """FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Registers a standard user and returns the registration dict."""
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password123!",
        "full_name": "Alice Wonderland",
    }
    resp = client.post("/register", json=user_data)
    assert resp.status_code == 201
    return {**user_data, "id": resp.json()["id"]}


# ---------------------------------------------------------------------------
# 1. POST /register tests
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success_default_role(self, client):
        payload = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePassword123!",
            "full_name": "John Doe",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()

        assert data["username"] == "johndoe"
        assert data["email"] == "john@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert data["full_name"] == "John Doe"
        assert "id" in data
        assert "created_at" in data
        # Ensure password is NEVER returned
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.parametrize("role", ["admin", "moderator", "guest", "user"])
    def test_register_explicit_roles(self, client, role):
        payload = {
            "username": f"user_{role}",
            "email": f"{role}@example.com",
            "password": "ValidPassword999",
            "role": role,
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 201
        assert resp.json()["role"] == role

    def test_register_duplicate_username_conflict(self, client, registered_user):
        payload = {
            "username": registered_user["username"],  # "alice"
            "email": "different@example.com",
            "password": "AnotherPassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 409
        assert "already taken" in resp.json()["detail"]

    def test_register_duplicate_email_conflict(self, client, registered_user):
        payload = {
            "username": "different_alice",
            "email": registered_user["email"],  # "alice@example.com"
            "password": "AnotherPassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"]

    def test_register_duplicate_email_case_insensitive(self, client, registered_user):
        payload = {
            "username": "new_alice",
            "email": "ALICE@EXAMPLE.COM",
            "password": "AnotherPassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"]

    def test_register_password_too_short(self, client):
        payload = {
            "username": "bobsmith",
            "email": "bob@example.com",
            "password": "short",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        payload = {
            "username": "bobsmith",
            "email": "not-an-email",
            "password": "SecurePassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_register_invalid_username_too_short(self, client):
        payload = {
            "username": "ab",
            "email": "ab@example.com",
            "password": "SecurePassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_register_invalid_username_characters(self, client):
        payload = {
            "username": "bad user name!",
            "email": "bad@example.com",
            "password": "SecurePassword123!",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_register_invalid_role(self, client):
        payload = {
            "username": "superhero",
            "email": "superhero@example.com",
            "password": "SecurePassword123!",
            "role": "superadmin",
        }
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_register_missing_fields(self, client):
        # Missing password
        resp = client.post("/register", json={"username": "user1", "email": "u1@example.com"})
        assert resp.status_code == 422

        # Missing email
        resp = client.post("/register", json={"username": "user1", "password": "Password123!"})
        assert resp.status_code == 422

        # Missing username
        resp = client.post("/register", json={"email": "u1@example.com", "password": "Password123!"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 2. POST /login tests
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success_with_username(self, client, registered_user, token_service):
        payload = {
            "username": registered_user["username"],
            "password": registered_user["password"],
        }
        resp = client.post("/login", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify access token claims
        access_payload = token_service.verify_token(data["access_token"], expected_type=TokenType.ACCESS)
        assert access_payload.sub == registered_user["username"]
        assert access_payload.role == UserRole.USER

        # Verify refresh token claims
        refresh_payload = token_service.verify_token(data["refresh_token"], expected_type=TokenType.REFRESH)
        assert refresh_payload.sub == registered_user["username"]
        assert refresh_payload.role is None

    def test_login_success_with_email(self, client, registered_user):
        payload = {
            "username": registered_user["email"],
            "password": registered_user["password"],
        }
        resp = client.post("/login", json=payload)
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert "refresh_token" in resp.json()

    def test_login_wrong_password(self, client, registered_user):
        payload = {
            "username": registered_user["username"],
            "password": "WrongPassword999!",
        }
        resp = client.post("/login", json=payload)
        assert resp.status_code == 401
        assert "Invalid username or password" in resp.json()["detail"]

    def test_login_nonexistent_user(self, client):
        payload = {
            "username": "ghost_user",
            "password": "AnyPassword123!",
        }
        resp = client.post("/login", json=payload)
        assert resp.status_code == 401
        assert "Invalid username or password" in resp.json()["detail"]

    def test_login_inactive_user_forbidden(self, client, registered_user):
        # Disable the user
        user = _USER_STORE[registered_user["username"]]
        user.is_active = False

        payload = {
            "username": registered_user["username"],
            "password": registered_user["password"],
        }
        resp = client.post("/login", json=payload)
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 3. POST /refresh tests
# ---------------------------------------------------------------------------

class TestRefresh:
    def test_refresh_success(self, client, registered_user):
        login_resp = client.post("/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        refresh_token = login_resp.json()["refresh_token"]

        refresh_resp = client.post("/refresh", json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 200
        data = refresh_resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # The new access token must be valid and grant access to /me
        new_token = data["access_token"]
        me_resp = client.get("/me", headers={"Authorization": f"Bearer {new_token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == registered_user["username"]

    def test_refresh_with_access_token_fails(self, client, registered_user):
        login_resp = client.post("/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        access_token = login_resp.json()["access_token"]

        refresh_resp = client.post("/refresh", json={"refresh_token": access_token})
        assert refresh_resp.status_code == 401
        assert "Invalid refresh token" in refresh_resp.json()["detail"]

    def test_refresh_with_expired_token(self, client, secret_key, registered_user):
        now = datetime.now(timezone.utc) - timedelta(days=2)
        expired_claims = {
            "sub": registered_user["username"],
            "type": "refresh",
            "iat": now - timedelta(days=7),
            "exp": now,
            "jti": "expired-jti-123",
        }
        expired_token = jwt.encode(expired_claims, secret_key, algorithm="HS256")

        resp = client.post("/refresh", json={"refresh_token": expired_token})
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"]

    def test_refresh_with_malformed_token(self, client):
        resp = client.post("/refresh", json={"refresh_token": "not.a.valid.jwt"})
        assert resp.status_code == 401

    def test_refresh_with_unknown_user(self, client, token_service):
        token = token_service.generate_refresh_token(sub="ghost_user")
        resp = client.post("/refresh", json={"refresh_token": token})
        assert resp.status_code == 401
        assert "User not found" in resp.json()["detail"]

    def test_refresh_with_disabled_user(self, client, registered_user, token_service):
        refresh_token = token_service.generate_refresh_token(sub=registered_user["username"])
        # Disable the user
        _USER_STORE[registered_user["username"]].is_active = False

        resp = client.post("/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 4. GET /me tests
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_success(self, client, registered_user):
        login_resp = client.post("/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        access_token = login_resp.json()["access_token"]

        resp = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        data = resp.json()

        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert data["full_name"] == registered_user["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_me_missing_auth_header(self, client):
        resp = client.get("/me")
        assert resp.status_code == 401
        assert "Missing Authorization header" in resp.json()["detail"]

    def test_me_invalid_token(self, client):
        resp = client.get("/me", headers={"Authorization": "Bearer invalid.token.value"})
        assert resp.status_code == 401
        assert "Invalid access token" in resp.json()["detail"]

    def test_me_expired_token(self, client, secret_key, registered_user):
        now = datetime.now(timezone.utc) - timedelta(minutes=20)
        expired_claims = {
            "sub": registered_user["username"],
            "role": "user",
            "type": "access",
            "iat": now - timedelta(minutes=15),
            "exp": now,
            "jti": "expired-access-jti",
        }
        expired_token = jwt.encode(expired_claims, secret_key, algorithm="HS256")

        resp = client.get("/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"]

    def test_me_refresh_token_rejected(self, client, registered_user, token_service):
        refresh_token = token_service.generate_refresh_token(sub=registered_user["username"])
        resp = client.get("/me", headers={"Authorization": f"Bearer {refresh_token}"})
        assert resp.status_code == 401
        assert "Invalid access token" in resp.json()["detail"]

    def test_me_inactive_user_forbidden(self, client, registered_user, token_service):
        access_token = token_service.generate_access_token(
            sub=registered_user["username"],
            role=UserRole.USER,
        )
        # Disable the user
        _USER_STORE[registered_user["username"]].is_active = False

        resp = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"]

    def test_me_deleted_user(self, client, registered_user, token_service):
        access_token = token_service.generate_access_token(
            sub=registered_user["username"],
            role=UserRole.USER,
        )
        # Remove user from store
        del _USER_STORE[registered_user["username"]]

        resp = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 401
        assert "User not found" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 5. Health endpoint test
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
