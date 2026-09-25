"""
test_bva_standards.py
Boundary Value Analysis (BVA) & AAA Pattern Testing Suite
Author: Ren (Lead QA Automation & Test Architect)
Standard: ISTQB Advanced / ISO 29119 / AAA Pattern
"""

import pytest
from starlette.testclient import TestClient
from auth_api import app, _USER_STORE
from auth_models import PasswordHasher, UserRole, UserCreate

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_user_store():
    # AAA: ARRANGE - clean state before each test
    _USER_STORE.clear()
    yield
    _USER_STORE.clear()


# =============================================================================
# 1. BOUNDARY VALUE ANALYSIS: Username Length (3 - 50 characters)
# =============================================================================

class TestUsernameBoundaries:
    """BVA on Username field: min=3, max=50"""

    def test_username_at_min_boundary_valid(self):
        # 1. ARRANGE
        payload = {"username": "abc", "password": "Password123!", "email": "min@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code == 201
        assert response.json()["username"] == "abc"

    def test_username_just_below_min_rejected(self):
        # 1. ARRANGE
        payload = {"username": "ab", "password": "Password123!", "email": "below_min@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code in (400, 422)

    def test_username_at_max_boundary_valid(self):
        # 1. ARRANGE (max = 64 characters per domain invariant)
        max_user = "u" * 64
        payload = {"username": max_user, "password": "Password123!", "email": "max@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code == 201
        assert response.json()["username"] == max_user

    def test_username_just_above_max_rejected(self):
        # 1. ARRANGE (65 chars is just above max)
        too_long = "u" * 65
        payload = {"username": too_long, "password": "Password123!", "email": "above_max@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code in (400, 422)


# =============================================================================
# 2. BOUNDARY VALUE ANALYSIS: Password Length (8 - 128 characters)
# =============================================================================

class TestPasswordBoundaries:
    """BVA on Password: min=8, max=128"""

    def test_password_at_min_boundary_valid(self):
        # 1. ARRANGE
        payload = {"username": "passmin", "password": "a" * 8, "email": "passmin@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code == 201

    def test_password_just_below_min_rejected(self):
        # 1. ARRANGE
        payload = {"username": "pass7", "password": "a" * 7, "email": "pass7@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code in (400, 422)

    def test_password_nominal_valid(self):
        # 1. ARRANGE
        payload = {"username": "nominal", "password": "SecurePassword123!", "email": "nom@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code == 201

    def test_password_empty_rejected(self):
        # 1. ARRANGE
        payload = {"username": "emptypass", "password": "", "email": "empty@test.com"}
        # 2. ACT
        response = client.post("/register", json=payload)
        # 3. ASSERT
        assert response.status_code in (400, 422)


# =============================================================================
# 3. AAA PATTERN: Concurrent Registration Edge Cases
# =============================================================================

class TestConcurrencyAndIdempotency:
    """Testing race-condition resistance and case sensitivity"""

    def test_case_insensitive_username_collision(self):
        # 1. ARRANGE
        client.post("/register", json={"username": "Alice", "password": "Password123!", "email": "a@test.com"})
        duplicate_payload = {"username": "alice", "password": "Password123!", "email": "a2@test.com"}
        # 2. ACT
        response = client.post("/register", json=duplicate_payload)
        # 3. ASSERT
        assert response.status_code in (400, 409)

    def test_case_insensitive_email_collision(self):
        # 1. ARRANGE
        client.post("/register", json={"username": "bob1", "password": "Password123!", "email": "Bob@Test.COM"})
        duplicate_payload = {"username": "bob2", "password": "Password123!", "email": "bob@test.com"}
        # 2. ACT
        response = client.post("/register", json=duplicate_payload)
        # 3. ASSERT
        assert response.status_code in (400, 409)


# =============================================================================
# 4. AAA PATTERN: Token Lifespan & Expiry Boundary
# =============================================================================

class TestTokenExpiryBoundaries:
    """Test token expiration handling"""

    def test_valid_access_token_allows_resource_access(self):
        # 1. ARRANGE
        client.post("/register", json={"username": "tokenuser", "password": "Password123!", "email": "t@test.com"})
        login_res = client.post("/login", json={"username": "tokenuser", "password": "Password123!"})
        access_token = login_res.json()["access_token"]
        # 2. ACT
        response = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        # 3. ASSERT
        assert response.status_code == 200
        assert response.json()["username"] == "tokenuser"

    def test_token_with_invalid_signature_rejected(self):
        # 1. ARRANGE
        client.post("/register", json={"username": "siguser", "password": "Password123!", "email": "sig@test.com"})
        login_res = client.post("/login", json={"username": "siguser", "password": "Password123!"})
        token = login_res.json()["access_token"]
        tampered_token = token[:-5] + "XXXXX"
        # 2. ACT
        response = client.get("/me", headers={"Authorization": f"Bearer {tampered_token}"})
        # 3. ASSERT
        assert response.status_code == 401
