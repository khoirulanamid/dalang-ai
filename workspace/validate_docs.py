"""
validate_docs.py
================
Validates that all runnable code snippets in docs/ARCHITECTURE.md and
docs/QUICKSTART.md execute without errors.
"""

import sys
import os

# Add workspace root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

errors = []

def check(label, condition):
    if condition:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ FAIL: {label}")
        errors.append(label)


# ─── QUICKSTART.md Snippet 1: parse_user_create + to_user_in_db ──────────────
print("\n=== QUICKSTART: User creation and password hashing ===")
from auth_models import parse_user_create, UserRole

user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "Password123!",
    "role": "user",
    "full_name": "Alice Smith",
}

user_create = parse_user_create(user_data)
check("parse_user_create returns UserCreate", user_create is not None)
check("username is alice", user_create.username == "alice")

user_in_db = user_create.to_user_in_db()
check("to_user_in_db produces UserInDB", user_in_db is not None)
check("hashed_password starts with pbkdf2_sha256", user_in_db.hashed_password.startswith("pbkdf2_sha256:"))
check("verify_password correct", user_in_db.verify_password("Password123!"))
check("verify_password wrong returns False", not user_in_db.verify_password("WrongPassword!"))

public_profile = user_in_db.to_public()
profile_dict = public_profile.to_dict()
check("to_public has no hashed_password", not hasattr(public_profile, "hashed_password"))
check("to_dict has username", profile_dict["username"] == "alice")
check("to_dict has role as string", profile_dict["role"] == "user")
check("to_dict has no password", "password" not in profile_dict)
check("to_dict has no hashed_password", "hashed_password" not in profile_dict)


# ─── QUICKSTART.md Snippet 2: Token issuance and verification ────────────────
print("\n=== QUICKSTART: Token issuance and verification ===")
from token_service import create_token_service, TokenType

svc = create_token_service(secret_key="your-256-bit-secret-at-least-32-chars!")

access_token = svc.generate_access_token(sub="alice", role=UserRole.USER)
check("generate_access_token returns string", isinstance(access_token, str))
check("access_token is a JWT (3 parts)", len(access_token.split(".")) == 3)

refresh_token = svc.generate_refresh_token(sub="alice")
check("generate_refresh_token returns string", isinstance(refresh_token, str))
check("refresh_token is a JWT (3 parts)", len(refresh_token.split(".")) == 3)

payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)
check("verify_token returns payload", payload is not None)
check("payload.sub == alice", payload.sub == "alice")
check("payload.role == user", payload.role == "user")
check("payload.jti is set", payload.jti is not None and len(payload.jti) > 0)
check("payload.exp is set", payload.exp is not None)


# ─── QUICKSTART.md Snippet 3: Token refresh ──────────────────────────────────
print("\n=== QUICKSTART: Token refresh ===")
new_access_token = svc.refresh_access_token(
    refresh_token=refresh_token,
    role=UserRole.USER,
)
check("refresh_access_token returns string", isinstance(new_access_token, str))
check("new access token is a JWT", len(new_access_token.split(".")) == 3)

new_payload = svc.verify_token(new_access_token, expected_type=TokenType.ACCESS)
check("new payload.sub == alice", new_payload.sub == "alice")
check("new token has different jti", new_payload.jti != payload.jti)


# ─── QUICKSTART.md: FastAPI endpoint integration ─────────────────────────────
print("\n=== QUICKSTART: FastAPI endpoint integration ===")
from fastapi.testclient import TestClient
from auth_api import app, _USER_STORE

# Clear store for clean test
_USER_STORE.clear()

client = TestClient(app)

# Register
res_reg = client.post("/register", json={
    "username": "alice",
    "email": "alice@example.com",
    "password": "Password123!",
    "role": "user",
    "full_name": "Alice Smith",
})
check("POST /register returns 201", res_reg.status_code == 201)
check("register response has id", "id" in res_reg.json())
check("register response has no password", "password" not in res_reg.json())
check("register response has no hashed_password", "hashed_password" not in res_reg.json())

# Login
res_login = client.post("/login", json={"username": "alice", "password": "Password123!"})
check("POST /login returns 200", res_login.status_code == 200)
check("login response has access_token", "access_token" in res_login.json())
check("login response has refresh_token", "refresh_token" in res_login.json())
check("login response has token_type bearer", res_login.json()["token_type"] == "bearer")

api_access = res_login.json()["access_token"]
api_refresh = res_login.json()["refresh_token"]

# GET /me with valid token
res_me = client.get("/me", headers={"Authorization": f"Bearer {api_access}"})
check("GET /me with valid token returns 200", res_me.status_code == 200)
check("/me response has username", res_me.json()["username"] == "alice")

# GET /me without token
res_me_unauth = client.get("/me")
check("GET /me without token returns 401", res_me_unauth.status_code == 401)

# POST /refresh
res_ref = client.post("/refresh", json={"refresh_token": api_refresh})
check("POST /refresh returns 200", res_ref.status_code == 200)
check("refresh response has access_token", "access_token" in res_ref.json())

new_api_access = res_ref.json()["access_token"]
res_me2 = client.get("/me", headers={"Authorization": f"Bearer {new_api_access}"})
check("GET /me with refreshed token returns 200", res_me2.status_code == 200)

# Wrong password
res_bad_login = client.post("/login", json={"username": "alice", "password": "WrongPass!"})
check("POST /login with wrong password returns 401", res_bad_login.status_code == 401)

# Duplicate registration
res_dup = client.post("/register", json={
    "username": "alice",
    "email": "alice2@example.com",
    "password": "Password123!",
    "role": "user",
})
check("Duplicate username returns 409", res_dup.status_code == 409)


# ─── ARCHITECTURE.md: Token type enforcement ─────────────────────────────────
print("\n=== ARCHITECTURE: Token type enforcement ===")
from token_service import TokenTypeMismatchError

try:
    # Passing a refresh token where an access token is expected must raise
    svc.verify_token(refresh_token, expected_type=TokenType.ACCESS)
    check("TokenTypeMismatchError raised for wrong type", False)
except TokenTypeMismatchError:
    check("TokenTypeMismatchError raised for wrong type", True)

try:
    # Passing an access token where a refresh token is expected must raise
    svc.verify_token(access_token, expected_type=TokenType.REFRESH)
    check("TokenTypeMismatchError raised for access-as-refresh", False)
except TokenTypeMismatchError:
    check("TokenTypeMismatchError raised for access-as-refresh", True)


# ─── ARCHITECTURE.md: needs_rehash detection ─────────────────────────────────
print("\n=== ARCHITECTURE: needs_rehash detection ===")
from auth_models import PasswordHasher

# A hash produced with the current parameters should NOT need rehash
current_hash = PasswordHasher.hash_password("Password123!")
check("Current hash does not need rehash", not PasswordHasher.needs_rehash(current_hash))

# A hash produced with fewer iterations SHOULD need rehash
weak_salt = os.urandom(32)
weak_dk = __import__("hashlib").pbkdf2_hmac("sha256", b"Password123!", weak_salt, 1000, 32)
weak_hash = f"pbkdf2_sha256:1000:{weak_salt.hex()}:{weak_dk.hex()}"
check("Weak hash needs rehash", PasswordHasher.needs_rehash(weak_hash))


# ─── Summary ─────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
if errors:
    print(f"FAILED — {len(errors)} check(s) failed:")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    total = sum(1 for line in open(__file__) if line.strip().startswith("check("))
    print(f"All {total} documentation snippet checks passed ✓")
    sys.exit(0)
