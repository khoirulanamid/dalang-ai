# Dalang-AI — Sprint 1 Authentication Modules

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-33%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/Modules-auth__models%20%7C%20token__service-blueviolet)

A production-ready, dependency-light authentication foundation for the Dalang-AI platform.  
Sprint 1 delivers two tightly integrated Python modules:

| Module | File | Purpose |
|---|---|---|
| **Auth Models** | `auth_models.py` | User schemas, roles, and PBKDF2 password hashing |
| **Token Service** | `token_service.py` | JWT generation, verification, and refresh |

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Module Overview](#module-overview)
4. [Usage Examples](#usage-examples)
   - [User Registration Flow](#user-registration-flow)
   - [Token Issuance Flow](#token-issuance-flow)
   - [Token Verification Flow](#token-verification-flow)
   - [Token Refresh Flow](#token-refresh-flow)
5. [Configuration](#configuration)
6. [Security Notes](#security-notes)
7. [Running Tests](#running-tests)
8. [Detailed Documentation](#detailed-documentation)

---

## Quick Start

```python
from auth_models import parse_user_create, UserRole
from token_service import create_token_service, TokenType

# 1. Register a user
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "S3cur3P@ss!",
    "role": "user",
}
user_create = parse_user_create(user_data)
user_in_db  = user_create.to_user_in_db()   # hashes password, never stores plain text

# 2. Authenticate and issue tokens
if user_in_db.verify_password("S3cur3P@ss!"):
    svc = create_token_service(secret_key="your-256-bit-secret")

    access_token  = svc.generate_access_token(sub=user_in_db.id, role=user_in_db.role)
    refresh_token = svc.generate_refresh_token(sub=user_in_db.id)

# 3. Verify an incoming access token
payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)
print(payload.sub, payload.role)   # user UUID, UserRole.USER

# 4. Rotate access token using refresh token
new_access = svc.refresh_access_token(refresh_token, role=UserRole.USER)
```

---

## Installation

The modules have **no third-party dependencies** beyond `PyJWT` (for `token_service.py`).

```bash
# Using the project virtual environment
pip install PyJWT cryptography
```

> `cryptography` is required only when using RS256 / ES256 asymmetric algorithms.

---

## Module Overview

```
auth_models.py
├── UserRole          (Enum)       — admin | moderator | user | guest
├── PasswordHasher    (class)      — PBKDF2-HMAC-SHA256 hash & verify
├── UserBase          (dataclass)  — shared fields: username, email, role, …
├── UserCreate        (dataclass)  — registration input (plain-text password)
├── UserInDB          (dataclass)  — persisted record (hashed password)
├── UserPublic        (dataclass)  — API-safe outbound schema (no passwords)
├── parse_user_create (function)   — dict → UserCreate with validation
└── parse_user_in_db  (function)   — dict → UserInDB with validation

token_service.py
├── TokenType         (Enum)       — access | refresh
├── TokenConfig       (dataclass)  — JWT settings (secret, algorithm, TTLs, …)
├── TokenPayload      (dataclass)  — decoded & validated JWT claims
├── TokenService      (class)      — generate / verify / refresh JWTs
│   ├── generate_access_token()
│   ├── generate_refresh_token()
│   ├── verify_token()
│   ├── refresh_access_token()
│   └── decode_unverified()
├── TokenError        (exception)  — base exception
├── TokenExpiredError (exception)  — token past its expiry
├── TokenInvalidError (exception)  — malformed or bad signature
├── TokenTypeMismatchError         — wrong token type presented
└── create_token_service (factory) — build TokenService from args or env vars
```

---

## Usage Examples

### User Registration Flow

```python
from auth_models import parse_user_create, UserRole

# Parse and validate raw input (e.g. from an HTTP request body)
user_create = parse_user_create({
    "username": "bob_dev",
    "email": "Bob@Example.COM",   # normalised to lowercase automatically
    "password": "MyStr0ng!Pass",
    "role": "moderator",
    "full_name": "Bob Developer",
})

# Convert to a DB-ready record (password is hashed, plain text discarded)
user_in_db = user_create.to_user_in_db()

print(user_in_db.username)         # "bob_dev"
print(user_in_db.email)            # "bob@example.com"
print(user_in_db.role)             # UserRole.MODERATOR
print(user_in_db.hashed_password)  # "pbkdf2_sha256:260000:<salt>:<digest>"
print(user_in_db.id)               # UUID4 string, e.g. "a1b2c3d4-..."

# Expose safe public representation (no password fields)
public = user_in_db.to_public()
print(public.to_dict())
# {
#   "id": "a1b2c3d4-...",
#   "username": "bob_dev",
#   "email": "bob@example.com",
#   "role": "moderator",
#   "is_active": True,
#   "full_name": "Bob Developer",
#   "created_at": "2024-01-15T10:30:00+00:00",
#   "updated_at": "2024-01-15T10:30:00+00:00"
# }
```

### Token Issuance Flow

```python
from token_service import create_token_service
from auth_models import UserRole

svc = create_token_service(
    secret_key="your-super-secret-key-at-least-32-chars",
    access_expire_minutes=15,
    refresh_expire_days=7,
)

access_token  = svc.generate_access_token(sub="user-uuid-123", role=UserRole.ADMIN)
refresh_token = svc.generate_refresh_token(sub="user-uuid-123")

# Tokens are compact JWTs: header.payload.signature
print(access_token[:40], "...")
```

### Token Verification Flow

```python
from token_service import TokenType, TokenExpiredError, TokenInvalidError

try:
    payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)
    print(f"User: {payload.sub}, Role: {payload.role}, Expires: {payload.exp}")
except TokenExpiredError:
    print("Token has expired — ask the client to refresh.")
except TokenInvalidError:
    print("Token is invalid or tampered — reject the request.")
```

### Token Refresh Flow

```python
from token_service import TokenTypeMismatchError

try:
    new_access = svc.refresh_access_token(
        refresh_token=refresh_token,
        role=UserRole.ADMIN,
    )
    payload = svc.verify_token(new_access, expected_type=TokenType.ACCESS)
    print(f"New access token issued for: {payload.sub}")
except TokenTypeMismatchError:
    print("Wrong token type — a refresh token is required here.")
```

---

## Configuration

### Environment Variables (for `create_token_service`)

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | built-in fallback ⚠️ | HMAC signing secret — **always override in production** |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm (`HS256`, `HS384`, `HS512`, `RS256`, …) |
| `JWT_ACCESS_EXPIRE_MINUTES` | `15` | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `7` | Refresh token lifetime in days |
| `JWT_ISSUER` | _(none)_ | Optional `iss` claim value |
| `JWT_AUDIENCE` | _(none)_ | Optional `aud` claim value |

```bash
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export JWT_ACCESS_EXPIRE_MINUTES=30
export JWT_REFRESH_EXPIRE_DAYS=14
export JWT_ISSUER="dalang-ai-api"
export JWT_AUDIENCE="dalang-ai-web"
```

---

## Security Notes

| Concern | Implementation |
|---|---|
| Password hashing | PBKDF2-HMAC-SHA256, 260 000 iterations (OWASP 2023), 256-bit salt |
| Timing-safe comparison | `hmac.compare_digest` prevents timing attacks on password verification |
| Plain-text passwords | Never stored — `UserCreate` converts to `UserInDB` immediately |
| JWT signing | HS256 by default; RS256 supported for asymmetric key scenarios |
| Reserved claims | `sub`, `type`, `iat`, `exp`, `jti`, `iss`, `aud` cannot be overwritten via `extra_claims` |
| Token type enforcement | `verify_token(expected_type=…)` prevents access tokens being used as refresh tokens |
| Rehash detection | `PasswordHasher.needs_rehash()` flags hashes produced with weaker parameters |

---

## Running Tests

```bash
# Run all tests
/root/storage/projects/dalang-ai/.venv/bin/pytest test_token.py -v

# Run a specific test class
/root/storage/projects/dalang-ai/.venv/bin/pytest test_token.py::TestTokenRefreshFlow -v

# Run with coverage (if pytest-cov is installed)
/root/storage/projects/dalang-ai/.venv/bin/pytest --cov=auth_models --cov=token_service
```

Expected output: **33 tests passed**.

---

## Detailed Documentation

| Document | Description |
|---|---|
| [`docs/auth_models.md`](docs/auth_models.md) | Full API reference for `auth_models.py` |
| [`docs/token_service.md`](docs/token_service.md) | Full API reference for `token_service.py` |
