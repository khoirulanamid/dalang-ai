"""
test_e2e_flow.py
================
Task T-703 — End-to-end integration tests covering the full user lifecycle.

Author: Ren (QA & E2E Testing Specialist)

Lifecycle journeys covered:
  1.  Full happy-path lifecycle:
        register → duplicate rejection → login → GET /me → refresh → use new token
  2.  Concurrent registrations — two distinct users registered in the same session
  3.  Duplicate username rejection (case-insensitive)
  4.  Duplicate email rejection (case-insensitive)
  5.  Login with email address instead of username
  6.  Weak / invalid registration inputs rejected (422)
  7.  Login with wrong password → 401
  8.  Login with unknown user → 401
  9.  GET /me with no Authorization header → 401
 10.  GET /me with malformed / garbage token → 401
 11.  GET /me with expired access token → 401
 12.  GET /me with refresh token (wrong type) → 401
 13.  POST /refresh with access token (wrong type) → 401
 14.  POST /refresh with expired refresh token → 401
 15.  POST /refresh with malformed token → 401
 16.  Full role-preservation journey: admin role survives register → login → /me → refresh
 17.  Inactive user: login blocked (403), /me blocked (403), refresh blocked (403)
 18.  Token claims contract verification (sub, role, type, iat, exp, jti)
 19.  New access token from refresh is accepted by /me
 20.  Health endpoint sanity check
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
import pytest
from starlette.testclient import TestClient

# ── Application under test ──────────────────────────────────────────────────
import auth_api
from auth_api import _USER_STORE, app
from auth_models import UserRole
from token_service import (
    TokenConfig,
    TokenService,
    TokenType,
    _DEFAULT_SECRET,
    create_token_service,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clean_store():
    """Wipe the in-memory user store before and after every test."""
    _USER_STORE.clear()
    yield
    _USER_STORE.clear()


@pytest.fixture
def client() -> TestClient:
    """Starlette TestClient wrapping the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def token_svc() -> TokenService:
    """A TokenService instance that matches the app's default configuration."""
    return create_token_service()


# ── Reusable payloads ────────────────────────────────────────────────────────

ALICE = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "AlicePass1!",
}

BOB = {
    "username": "bob",
    "email": "bob@example.com",
    "password": "BobPass99@",
}

ADMIN_USER = {
    "username": "adminuser",
    "email": "admin@example.com",
    "password": "AdminPass1!",
    "role": "admin",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _register(client: TestClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Register a user and assert 201; return response JSON."""
    resp = client.post("/register", json=payload)
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    return resp.json()


def _login(client: TestClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Login and assert 200; return response JSON."""
    resp = client.post("/login", json=payload)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


def _me(client: TestClient, access_token: str) -> Dict[str, Any]:
    """Call GET /me with a Bearer token and assert 200; return response JSON."""
    resp = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200, f"/me failed: {resp.text}"
    return resp.json()


def _refresh(client: TestClient, refresh_token: str) -> Dict[str, Any]:
    """Call POST /refresh and assert 200; return response JSON."""
    resp = client.post("/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200, f"/refresh failed: {resp.text}"
    return resp.json()


def _make_expired_token(token_type: str, secret: str = _DEFAULT_SECRET) -> str:
    """Craft a JWT that is already expired."""
    now = datetime.now(timezone.utc)
    claims = {
        "sub": "ghost",
        "type": token_type,
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if token_type == TokenType.ACCESS:
        claims["role"] = "user"
    return jwt.encode(claims, secret, algorithm="HS256")


# ============================================================================
# 1. Full Happy-Path Lifecycle
# ============================================================================

class TestFullLifecycle:
    """
    The canonical end-to-end journey:
      register → duplicate rejection → login → /me → refresh → use new token
    """

    def test_register_success(self, client):
        data = _register(client, ALICE)
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"          # default role
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        # No password fields must leak
        assert "password" not in data
        assert "hashed_password" not in data

    def test_duplicate_username_rejected(self, client):
        _register(client, ALICE)
        resp = client.post("/register", json=ALICE)
        assert resp.status_code == 409
        assert "username" in resp.json()["detail"].lower() or "already" in resp.json()["detail"].lower()

    def test_duplicate_email_rejected(self, client):
        _register(client, ALICE)
        different_username = {**ALICE, "username": "alice2"}
        resp = client.post("/register", json=different_username)
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower() or "already" in resp.json()["detail"].lower()

    def test_login_returns_tokens(self, client):
        _register(client, ALICE)
        data = _login(client, {"username": "alice", "password": ALICE["password"]})
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_access_me_with_access_token(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        profile = _me(client, tokens["access_token"])
        assert profile["username"] == "alice"
        assert profile["email"] == "alice@example.com"
        assert profile["role"] == "user"
        assert profile["is_active"] is True

    def test_refresh_returns_new_access_token(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        new_tokens = _refresh(client, tokens["refresh_token"])
        assert "access_token" in new_tokens
        # New access token must be a non-empty string
        assert isinstance(new_tokens["access_token"], str)
        assert len(new_tokens["access_token"]) > 10

    def test_new_access_token_grants_me_access(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        new_tokens = _refresh(client, tokens["refresh_token"])
        profile = _me(client, new_tokens["access_token"])
        assert profile["username"] == "alice"

    def test_full_lifecycle_in_sequence(self, client):
        """Single test that chains every step end-to-end."""
        # Step 1 — Register
        reg = _register(client, ALICE)
        user_id = reg["id"]

        # Step 2 — Duplicate rejected
        dup = client.post("/register", json=ALICE)
        assert dup.status_code == 409

        # Step 3 — Login
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Step 4 — Access /me
        profile = _me(client, access_token)
        assert profile["id"] == user_id
        assert profile["username"] == "alice"

        # Step 5 — Refresh
        new_tokens = _refresh(client, refresh_token)
        new_access = new_tokens["access_token"]

        # Step 6 — Use new access token
        profile2 = _me(client, new_access)
        assert profile2["username"] == "alice"
        assert profile2["id"] == user_id


# ============================================================================
# 2. Concurrent / Multi-User Flows
# ============================================================================

class TestConcurrentUsers:
    """Two independent users can register and operate without interference."""

    def test_two_users_register_independently(self, client):
        alice_data = _register(client, ALICE)
        bob_data = _register(client, BOB)
        assert alice_data["username"] == "alice"
        assert bob_data["username"] == "bob"
        assert alice_data["id"] != bob_data["id"]

    def test_two_users_login_independently(self, client):
        _register(client, ALICE)
        _register(client, BOB)
        alice_tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        bob_tokens = _login(client, {"username": "bob", "password": BOB["password"]})
        # Tokens must be distinct
        assert alice_tokens["access_token"] != bob_tokens["access_token"]
        assert alice_tokens["refresh_token"] != bob_tokens["refresh_token"]

    def test_two_users_access_own_profiles(self, client):
        _register(client, ALICE)
        _register(client, BOB)
        alice_tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        bob_tokens = _login(client, {"username": "bob", "password": BOB["password"]})

        alice_profile = _me(client, alice_tokens["access_token"])
        bob_profile = _me(client, bob_tokens["access_token"])

        assert alice_profile["username"] == "alice"
        assert bob_profile["username"] == "bob"
        assert alice_profile["id"] != bob_profile["id"]

    def test_alice_token_cannot_impersonate_bob(self, client):
        """Alice's token returns Alice's profile, not Bob's."""
        _register(client, ALICE)
        _register(client, BOB)
        alice_tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        profile = _me(client, alice_tokens["access_token"])
        assert profile["username"] == "alice"
        assert profile["email"] == "alice@example.com"


# ============================================================================
# 3. Duplicate Rejection (Case-Insensitive)
# ============================================================================

class TestDuplicateRejection:
    def test_duplicate_username_case_insensitive(self, client):
        _register(client, ALICE)
        upper = {**ALICE, "username": "ALICE", "email": "alice2@example.com"}
        resp = client.post("/register", json=upper)
        assert resp.status_code == 409

    def test_duplicate_email_case_insensitive(self, client):
        _register(client, ALICE)
        upper_email = {**ALICE, "username": "alice2", "email": "ALICE@EXAMPLE.COM"}
        resp = client.post("/register", json=upper_email)
        assert resp.status_code == 409


# ============================================================================
# 4. Login with Email Address
# ============================================================================

class TestLoginWithEmail:
    def test_login_with_email(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": ALICE["email"], "password": ALICE["password"]})
        assert "access_token" in tokens

    def test_login_with_email_grants_me_access(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": ALICE["email"], "password": ALICE["password"]})
        profile = _me(client, tokens["access_token"])
        assert profile["username"] == "alice"


# ============================================================================
# 5. Registration Validation
# ============================================================================

class TestRegistrationValidation:
    def test_short_password_rejected(self, client):
        payload = {**ALICE, "password": "short"}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_invalid_email_rejected(self, client):
        payload = {**ALICE, "email": "not-an-email"}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_missing_username_rejected(self, client):
        payload = {"email": ALICE["email"], "password": ALICE["password"]}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_missing_password_rejected(self, client):
        payload = {"username": ALICE["username"], "email": ALICE["email"]}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_missing_email_rejected(self, client):
        payload = {"username": ALICE["username"], "password": ALICE["password"]}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422

    def test_invalid_role_rejected(self, client):
        payload = {**ALICE, "role": "superuser"}
        resp = client.post("/register", json=payload)
        assert resp.status_code == 422


# ============================================================================
# 6. Login Failure Scenarios
# ============================================================================

class TestLoginFailures:
    def test_wrong_password_rejected(self, client):
        _register(client, ALICE)
        resp = client.post("/login", json={"username": "alice", "password": "WrongPass!"})
        assert resp.status_code == 401

    def test_unknown_user_rejected(self, client):
        resp = client.post("/login", json={"username": "nobody", "password": "AnyPass1!"})
        assert resp.status_code == 401

    def test_empty_password_rejected(self, client):
        _register(client, ALICE)
        resp = client.post("/login", json={"username": "alice", "password": ""})
        assert resp.status_code in (401, 422)


# ============================================================================
# 7. /me Failure Scenarios
# ============================================================================

class TestMeFailures:
    def test_no_auth_header_rejected(self, client):
        resp = client.get("/me")
        assert resp.status_code == 401

    def test_malformed_token_rejected(self, client):
        resp = client.get("/me", headers={"Authorization": "Bearer this.is.garbage"})
        assert resp.status_code == 401

    def test_empty_bearer_rejected(self, client):
        resp = client.get("/me", headers={"Authorization": "Bearer "})
        assert resp.status_code in (401, 403, 422)

    def test_expired_access_token_rejected(self, client):
        expired = _make_expired_token(TokenType.ACCESS)
        resp = client.get("/me", headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()

    def test_refresh_token_rejected_at_me(self, client):
        """Presenting a refresh token to /me must be rejected."""
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        resp = client.get("/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"})
        assert resp.status_code == 401

    def test_tampered_token_rejected(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        # Flip the last character of the signature
        tampered = tokens["access_token"][:-1] + ("X" if tokens["access_token"][-1] != "X" else "Y")
        resp = client.get("/me", headers={"Authorization": f"Bearer {tampered}"})
        assert resp.status_code == 401


# ============================================================================
# 8. /refresh Failure Scenarios
# ============================================================================

class TestRefreshFailures:
    def test_access_token_rejected_at_refresh(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        resp = client.post("/refresh", json={"refresh_token": tokens["access_token"]})
        assert resp.status_code == 401

    def test_expired_refresh_token_rejected(self, client):
        expired = _make_expired_token(TokenType.REFRESH)
        resp = client.post("/refresh", json={"refresh_token": expired})
        assert resp.status_code == 401

    def test_malformed_refresh_token_rejected(self, client):
        resp = client.post("/refresh", json={"refresh_token": "not.a.real.token"})
        assert resp.status_code == 401

    def test_missing_refresh_token_field_rejected(self, client):
        resp = client.post("/refresh", json={})
        assert resp.status_code == 422

    def test_refresh_unknown_user(self, client, token_svc):
        """A refresh token for a user that no longer exists must be rejected."""
        ghost_token = token_svc.generate_refresh_token(sub="ghost_user")
        resp = client.post("/refresh", json={"refresh_token": ghost_token})
        assert resp.status_code == 401


# ============================================================================
# 9. Role Preservation Journey
# ============================================================================

class TestRolePreservation:
    def test_admin_role_preserved_through_lifecycle(self, client):
        # Register as admin
        reg = _register(client, ADMIN_USER)
        assert reg["role"] == "admin"

        # Login
        tokens = _login(client, {"username": "adminuser", "password": ADMIN_USER["password"]})

        # /me shows admin role
        profile = _me(client, tokens["access_token"])
        assert profile["role"] == "admin"

        # Refresh
        new_tokens = _refresh(client, tokens["refresh_token"])

        # /me with new token still shows admin role
        profile2 = _me(client, new_tokens["access_token"])
        assert profile2["role"] == "admin"

    def test_access_token_claims_carry_role(self, client, token_svc):
        _register(client, ADMIN_USER)
        tokens = _login(client, {"username": "adminuser", "password": ADMIN_USER["password"]})
        payload = token_svc.verify_token(tokens["access_token"], expected_type=None)
        assert payload.role == UserRole.ADMIN

    def test_moderator_role_preserved(self, client):
        mod_user = {
            "username": "moduser",
            "email": "mod@example.com",
            "password": "ModPass99!",
            "role": "moderator",
        }
        reg = _register(client, mod_user)
        assert reg["role"] == "moderator"
        tokens = _login(client, {"username": "moduser", "password": mod_user["password"]})
        profile = _me(client, tokens["access_token"])
        assert profile["role"] == "moderator"


# ============================================================================
# 10. Inactive User Flows
# ============================================================================

class TestInactiveUser:
    def _register_and_disable(self, client):
        _register(client, ALICE)
        _USER_STORE["alice"].is_active = False

    def test_inactive_user_login_blocked(self, client):
        self._register_and_disable(client)
        resp = client.post("/login", json={"username": "alice", "password": ALICE["password"]})
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"].lower()

    def test_inactive_user_me_blocked(self, client, token_svc):
        _register(client, ALICE)
        access_token = token_svc.generate_access_token(sub="alice", role=UserRole.USER)
        _USER_STORE["alice"].is_active = False
        resp = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 403

    def test_inactive_user_refresh_blocked(self, client, token_svc):
        _register(client, ALICE)
        refresh_token = token_svc.generate_refresh_token(sub="alice")
        _USER_STORE["alice"].is_active = False
        resp = client.post("/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code in (401, 403)


# ============================================================================
# 11. Token Claims Contract Verification
# ============================================================================

class TestTokenClaimsContract:
    """Verify that issued tokens carry the correct, complete claim set."""

    def test_access_token_claims(self, client, token_svc):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        payload = token_svc.verify_token(tokens["access_token"], expected_type=None)

        assert payload.sub == "alice"
        assert payload.token_type == TokenType.ACCESS
        assert payload.role == UserRole.USER
        assert payload.jti is not None and len(payload.jti) > 0
        assert payload.iat is not None
        assert payload.exp is not None
        assert payload.exp > payload.iat

    def test_refresh_token_claims(self, client, token_svc):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        payload = token_svc.verify_token(tokens["refresh_token"], expected_type=None)

        assert payload.sub == "alice"
        assert payload.token_type == TokenType.REFRESH
        assert payload.jti is not None and len(payload.jti) > 0
        assert payload.iat is not None
        assert payload.exp is not None
        assert payload.exp > payload.iat

    def test_access_token_has_longer_exp_than_iat(self, client, token_svc):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        payload = token_svc.verify_token(tokens["access_token"], expected_type=None)
        # Access token should expire in the future (at least a few seconds from now)
        now_dt = datetime.now(timezone.utc)
        assert payload.exp > now_dt

    def test_refresh_token_expires_after_access_token(self, client, token_svc):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        access_payload = token_svc.verify_token(tokens["access_token"], expected_type=None)
        refresh_payload = token_svc.verify_token(tokens["refresh_token"], expected_type=None)
        # Refresh token should live longer than access token
        assert refresh_payload.exp > access_payload.exp

    def test_each_login_produces_unique_jti(self, client, token_svc):
        _register(client, ALICE)
        tokens1 = _login(client, {"username": "alice", "password": ALICE["password"]})
        tokens2 = _login(client, {"username": "alice", "password": ALICE["password"]})
        p1 = token_svc.verify_token(tokens1["access_token"], expected_type=None)
        p2 = token_svc.verify_token(tokens2["access_token"], expected_type=None)
        assert p1.jti != p2.jti

    def test_new_access_token_from_refresh_has_correct_claims(self, client, token_svc):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        new_tokens = _refresh(client, tokens["refresh_token"])
        payload = token_svc.verify_token(new_tokens["access_token"], expected_type=None)
        assert payload.sub == "alice"
        assert payload.token_type == TokenType.ACCESS
        assert payload.role == UserRole.USER


# ============================================================================
# 12. Profile Data Integrity
# ============================================================================

class TestProfileDataIntegrity:
    def test_me_response_matches_registration(self, client):
        reg = _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        profile = _me(client, tokens["access_token"])

        assert profile["id"] == reg["id"]
        assert profile["username"] == reg["username"]
        assert profile["email"] == reg["email"]
        assert profile["role"] == reg["role"]
        assert profile["is_active"] == reg["is_active"]

    def test_me_response_has_no_password_fields(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        profile = _me(client, tokens["access_token"])
        assert "password" not in profile
        assert "hashed_password" not in profile

    def test_me_response_has_timestamps(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        profile = _me(client, tokens["access_token"])
        assert "created_at" in profile
        assert "updated_at" in profile
        # Should be parseable ISO strings
        datetime.fromisoformat(profile["created_at"])
        datetime.fromisoformat(profile["updated_at"])

    def test_register_response_has_no_password_fields(self, client):
        reg = _register(client, ALICE)
        assert "password" not in reg
        assert "hashed_password" not in reg

    def test_login_response_has_no_password_fields(self, client):
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})
        assert "password" not in tokens
        assert "hashed_password" not in tokens


# ============================================================================
# 13. Health Endpoint
# ============================================================================

class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_health_timestamp_is_iso(self, client):
        resp = client.get("/health")
        ts = resp.json()["timestamp"]
        datetime.fromisoformat(ts)  # must not raise


# ============================================================================
# 14. Edge Cases & Boundary Conditions
# ============================================================================

class TestEdgeCases:
    def test_register_guest_role(self, client):
        payload = {**ALICE, "role": "guest"}
        reg = _register(client, payload)
        assert reg["role"] == "guest"

    def test_register_moderator_role(self, client):
        payload = {**ALICE, "role": "moderator"}
        reg = _register(client, payload)
        assert reg["role"] == "moderator"

    def test_login_is_case_sensitive_for_password(self, client):
        _register(client, ALICE)
        resp = client.post("/login", json={"username": "alice", "password": ALICE["password"].upper()})
        assert resp.status_code == 401

    def test_register_id_is_uuid_format(self, client):
        reg = _register(client, ALICE)
        # Should parse as a valid UUID without raising
        uuid.UUID(reg["id"])

    def test_multiple_refreshes_in_sequence(self, client):
        """Chaining multiple refresh cycles must keep working."""
        _register(client, ALICE)
        tokens = _login(client, {"username": "alice", "password": ALICE["password"]})

        for _ in range(3):
            new_tokens = _refresh(client, tokens["refresh_token"])
            profile = _me(client, new_tokens["access_token"])
            assert profile["username"] == "alice"
            # Keep the original refresh token (stateless server reuses it)

    def test_wrong_http_method_on_register(self, client):
        resp = client.get("/register")
        assert resp.status_code == 405

    def test_wrong_http_method_on_login(self, client):
        resp = client.get("/login")
        assert resp.status_code == 405

    def test_wrong_http_method_on_refresh(self, client):
        resp = client.get("/refresh")
        assert resp.status_code == 405

    def test_wrong_http_method_on_me(self, client):
        resp = client.post("/me")
        assert resp.status_code == 405
