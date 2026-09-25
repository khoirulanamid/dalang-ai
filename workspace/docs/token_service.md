# Token Service Reference (`token_service.py`)

![Status](https://img.shields.io/badge/Status-Sprint%201%20Ready-brightgreen)
![Module](https://img.shields.io/badge/Module-token__service-blue)
![Tests](https://img.shields.io/badge/Tests-33%20passed-brightgreen)
![JWT](https://img.shields.io/badge/JWT-HS256%20%7C%20RS256-orange)

The `token_service` module provides a production-ready JWT (JSON Web Token) engine for issuing, verifying, and rotating access and refresh tokens. It integrates directly with `auth_models.UserRole` and is configurable via constructor arguments or environment variables.

---

## Table of Contents

1. [Token Architecture](#token-architecture)
2. [JWT Claim Schemas](#jwt-claim-schemas)
3. [Enums](#enums)
   - [TokenType](#tokentype)
4. [Configuration](#configuration)
   - [TokenConfig](#tokenconfig)
5. [Decoded Payload](#decoded-payload)
   - [TokenPayload](#tokenpayload)
6. [Exceptions](#exceptions)
7. [TokenService](#tokenservice)
   - [Constructor](#constructor)
   - [generate_access_token](#generate_access_token)
   - [generate_refresh_token](#generate_refresh_token)
   - [verify_token](#verify_token)
   - [refresh_access_token](#refresh_access_token)
   - [decode_unverified](#decode_unverified)
8. [Factory Function](#factory-function)
   - [create_token_service](#create_token_service)
9. [Environment Variables Reference](#environment-variables-reference)
10. [Error Handling Reference](#error-handling-reference)
11. [Integration Examples](#integration-examples)
    - [FastAPI Bearer Token Middleware](#fastapi-bearer-token-middleware)
    - [Full Auth Lifecycle (Python)](#full-auth-lifecycle-python)
    - [cURL Examples](#curl-examples)

---

## Token Architecture

The service issues two distinct JWT types that work together in a standard OAuth2-style token pair:

```
┌─────────────────────────────────────────────────────────────────┐
│                        TOKEN LIFECYCLE                          │
│                                                                 │
│  Login ──► generate_access_token()  ──► short-lived (15 min)   │
│        └─► generate_refresh_token() ──► long-lived  (7 days)   │
│                                                                 │
│  API Request ──► verify_token(expected_type=ACCESS)             │
│                       │                                         │
│                  TokenPayload (sub, role, exp, jti, …)          │
│                                                                 │
│  Token Expired ──► refresh_access_token(refresh_token, role)    │
│                       │                                         │
│                  New access token (fresh exp, new jti)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## JWT Claim Schemas

### Access Token Claims

| Claim | Type | Description |
|---|---|---|
| `sub` | `str` | Subject — user ID or username |
| `role` | `str` | User role (`"admin"`, `"moderator"`, `"user"`, `"guest"`) |
| `type` | `str` | Always `"access"` |
| `iat` | `int` | Issued-at (UTC Unix epoch) |
| `exp` | `int` | Expiry (UTC Unix epoch) |
| `jti` | `str` | Unique token ID (UUID4) — enables revocation tracking |
| `iss` | `str` | Issuer (optional, from `TokenConfig.issuer`) |
| `aud` | `str` | Audience (optional, from `TokenConfig.audience`) |
| _custom_ | any | Additional claims via `extra_claims` (reserved claims protected) |

### Refresh Token Claims

| Claim | Type | Description |
|---|---|---|
| `sub` | `str` | Subject — user ID or username |
| `type` | `str` | Always `"refresh"` |
| `iat` | `int` | Issued-at (UTC Unix epoch) |
| `exp` | `int` | Expiry (UTC Unix epoch) |
| `jti` | `str` | Unique token ID (UUID4) |
| `iss` | `str` | Issuer (optional) |
| `aud` | `str` | Audience (optional) |

> **Note:** Refresh tokens intentionally omit the `role` claim. The role is re-supplied by the application when calling `refresh_access_token()`, allowing role changes to take effect on the next refresh.

---

## Enums

### `TokenType`

Extends `(str, Enum)`. Identifies the purpose of a JWT.

```python
from token_service import TokenType
```

| Member | Value | Description |
|---|---|---|
| `ACCESS` | `"access"` | Short-lived token for API authorization |
| `REFRESH` | `"refresh"` | Long-lived token for obtaining new access tokens |

---

## Configuration

### `TokenConfig`

Dataclass holding all JWT configuration parameters. Validated at construction time.

```python
from datetime import timedelta
from token_service import TokenConfig

config = TokenConfig(
    secret_key="your-256-bit-secret-key-here",
    algorithm="HS256",
    access_token_expire=timedelta(minutes=15),
    refresh_token_expire=timedelta(days=7),
    issuer="dalang-ai-api",
    audience="dalang-ai-web",
)
```

#### Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `secret_key` | `str` | _required_ | HMAC signing secret (HS256) or PEM key (RS256) |
| `algorithm` | `str` | `"HS256"` | JWT signing algorithm |
| `access_token_expire` | `timedelta` | `timedelta(minutes=15)` | Access token lifetime |
| `refresh_token_expire` | `timedelta` | `timedelta(days=7)` | Refresh token lifetime |
| `issuer` | `Optional[str]` | `None` | Value for the `iss` claim |
| `audience` | `Optional[str]` | `None` | Value for the `aud` claim |

#### Validation Errors

| Condition | Exception | Message |
|---|---|---|
| `secret_key` is empty or whitespace-only | `ValueError` | `"TokenConfig.secret_key must not be empty."` |
| `algorithm` not in PyJWT's supported list | `ValueError` | `"Unsupported algorithm: '<alg>'"` |
| `access_token_expire` ≤ 0 | `ValueError` | `"access_token_expire must be a positive duration."` |
| `refresh_token_expire` ≤ 0 | `ValueError` | `"refresh_token_expire must be a positive duration."` |

#### Supported Algorithms

| Algorithm | Type | Notes |
|---|---|---|
| `HS256` | Symmetric HMAC | Default; suitable for single-service deployments |
| `HS384` | Symmetric HMAC | Higher security margin |
| `HS512` | Symmetric HMAC | Maximum HMAC security |
| `RS256` | Asymmetric RSA | Recommended for multi-service / microservice architectures |
| `ES256` | Asymmetric ECDSA | Compact signatures; requires `cryptography` package |

---

## Decoded Payload

### `TokenPayload`

Dataclass returned by `verify_token()`. Represents a fully decoded and validated JWT.

```python
from token_service import TokenPayload
```

#### Fields

| Field | Type | Description |
|---|---|---|
| `sub` | `str` | Subject (user ID or username) |
| `token_type` | `TokenType` | `TokenType.ACCESS` or `TokenType.REFRESH` |
| `jti` | `str` | Unique token identifier (UUID4) |
| `iat` | `datetime` | Issued-at timestamp (UTC-aware) |
| `exp` | `datetime` | Expiry timestamp (UTC-aware) |
| `role` | `Optional[UserRole]` | User role (present on access tokens; `None` on refresh tokens) |
| `issuer` | `Optional[str]` | `iss` claim value |
| `audience` | `Optional[str]` | `aud` claim value |
| `raw` | `dict` | Original decoded claims dictionary (`repr=False`) |

#### Properties

| Property | Type | Description |
|---|---|---|
| `is_expired` | `bool` | `True` if `datetime.now(UTC) >= self.exp` |
| `is_access_token` | `bool` | `True` if `token_type == TokenType.ACCESS` |
| `is_refresh_token` | `bool` | `True` if `token_type == TokenType.REFRESH` |

```python
payload = svc.verify_token(access_token)

print(payload.sub)              # "user-uuid-1234"
print(payload.role)             # UserRole.ADMIN
print(payload.is_access_token)  # True
print(payload.is_expired)       # False
print(payload.exp)              # datetime(2024, 3, 1, 12, 15, 0, tzinfo=UTC)
print(payload.raw["jti"])       # "a1b2c3d4-..."
```

---

## Exceptions

All token exceptions inherit from `TokenError`, which itself inherits from `Exception`.

```
Exception
└── TokenError
    ├── TokenExpiredError
    ├── TokenInvalidError
    └── TokenTypeMismatchError
```

| Exception | Trigger Condition |
|---|---|
| `TokenError` | Base class; catch-all for any token error |
| `TokenExpiredError` | Token's `exp` claim is in the past |
| `TokenInvalidError` | Malformed JWT, bad signature, unknown `type` or `role` claim |
| `TokenTypeMismatchError` | `expected_type` argument does not match the token's `type` claim |

```python
from token_service import (
    TokenError,
    TokenExpiredError,
    TokenInvalidError,
    TokenTypeMismatchError,
)

try:
    payload = svc.verify_token(token, expected_type=TokenType.ACCESS)
except TokenExpiredError:
    # Prompt client to use refresh token
    ...
except TokenTypeMismatchError:
    # Client sent wrong token type
    ...
except TokenInvalidError:
    # Reject — token is tampered or malformed
    ...
except TokenError:
    # Catch-all for any other token issue
    ...
```

---

## TokenService

The core service class. Instantiate with a `TokenConfig` or use the `create_token_service()` factory.

### Constructor

```python
from token_service import TokenService, TokenConfig

svc = TokenService(config=TokenConfig(secret_key="my-secret"))
```

#### Parameters

| Parameter | Type | Description |
|---|---|---|
| `config` | `TokenConfig` | Validated configuration instance |

---

### `generate_access_token`

```python
def generate_access_token(
    self,
    sub: str,
    role: UserRole,
    extra_claims: Optional[dict] = None,
) -> str
```

Generates and signs a JWT access token.

#### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `sub` | `str` | ✅ | Subject identifier (user ID or username) |
| `role` | `UserRole` \| `str` | ✅ | User role; string values are coerced to `UserRole` |
| `extra_claims` | `dict` | ❌ | Additional custom claims to embed (reserved claims are protected) |

#### Returns

`str` — Compact, URL-safe JWT string (`header.payload.signature`).

#### Raises

| Exception | Condition |
|---|---|
| `ValueError` | `sub` is empty or whitespace-only |
| `ValueError` | `role` string is not a valid `UserRole` value |

#### Reserved Claims (cannot be overwritten via `extra_claims`)

`sub`, `role`, `type`, `iat`, `exp`, `jti`, `iss`, `aud`

#### Example

```python
token = svc.generate_access_token(
    sub="user-uuid-abc123",
    role=UserRole.ADMIN,
    extra_claims={"org_id": "org-42", "tenant": "acme-corp"},
)
```

---

### `generate_refresh_token`

```python
def generate_refresh_token(
    self,
    sub: str,
    extra_claims: Optional[dict] = None,
) -> str
```

Generates and signs a JWT refresh token. Refresh tokens do **not** carry a `role` claim.

#### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `sub` | `str` | ✅ | Subject identifier |
| `extra_claims` | `dict` | ❌ | Additional custom claims |

#### Returns

`str` — Compact JWT string.

#### Raises

| Exception | Condition |
|---|---|
| `ValueError` | `sub` is empty or whitespace-only |

#### Example

```python
refresh_token = svc.generate_refresh_token(sub="user-uuid-abc123")
```

---

### `verify_token`

```python
def verify_token(
    self,
    token: str,
    expected_type: Optional[TokenType] = None,
) -> TokenPayload
```

Decodes and fully validates a JWT token: signature, expiry, algorithm, issuer, audience, and optionally the token type.

#### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | `str` | ✅ | Encoded JWT string |
| `expected_type` | `TokenType` | ❌ | If provided, enforces the `type` claim must match |

#### Returns

`TokenPayload` — Decoded and validated payload.

#### Raises

| Exception | Condition |
|---|---|
| `TokenExpiredError` | Token's `exp` is in the past |
| `TokenInvalidError` | Malformed JWT, bad signature, unknown `type` or `role` |
| `TokenTypeMismatchError` | `expected_type` does not match the token's `type` claim |

#### Example

```python
# Strict type enforcement (recommended for route guards)
payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)

# Permissive — accepts any valid token type
payload = svc.verify_token(some_token)
print(payload.token_type)  # TokenType.ACCESS or TokenType.REFRESH
```

---

### `refresh_access_token`

```python
def refresh_access_token(
    self,
    refresh_token: str,
    role: UserRole,
    extra_claims: Optional[dict] = None,
) -> str
```

Validates a refresh token and issues a brand-new access token. The new access token has a fresh `exp` and a new `jti`.

#### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `refresh_token` | `str` | ✅ | Encoded refresh JWT |
| `role` | `UserRole` | ✅ | Role to embed in the new access token (re-fetched from DB) |
| `extra_claims` | `dict` | ❌ | Optional extra claims for the new access token |

#### Returns

`str` — New encoded access JWT string.

#### Raises

| Exception | Condition |
|---|---|
| `TokenExpiredError` | Refresh token has expired |
| `TokenInvalidError` | Refresh token is malformed or has bad signature |
| `TokenTypeMismatchError` | Provided token is not a refresh token |

#### Example

```python
try:
    new_access = svc.refresh_access_token(
        refresh_token=stored_refresh_token,
        role=UserRole.USER,
    )
except TokenExpiredError:
    # Refresh token expired — force re-login
    redirect_to_login()
```

---

### `decode_unverified`

```python
def decode_unverified(self, token: str) -> dict
```

Decodes a JWT **without verifying the signature**. Useful for inspecting headers or claims before performing full verification (e.g., to determine which key to use for RS256 multi-tenant scenarios).

> ⚠️ **Security Warning:** Never use the output of `decode_unverified()` for authorization decisions. Always follow up with `verify_token()`.

#### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | `str` | ✅ | Encoded JWT string |

#### Returns

`dict` — Raw decoded claims dictionary (unverified).

#### Raises

| Exception | Condition |
|---|---|
| `TokenInvalidError` | Token is structurally malformed (not a valid JWT format) |

#### Example

```python
# Inspect the token's issuer before selecting the right verification key
raw = svc.decode_unverified(incoming_token)
issuer = raw.get("iss")

# Now verify with the appropriate service
verified_payload = get_service_for_issuer(issuer).verify_token(incoming_token)
```

---

## Factory Function

### `create_token_service`

```python
def create_token_service(
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    access_expire_minutes: Optional[int] = None,
    refresh_expire_days: Optional[int] = None,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
) -> TokenService
```

Convenience factory that builds a `TokenService` from explicit arguments, falling back to environment variables, and then to built-in defaults.

#### Resolution Order (per parameter)

```
Explicit argument → Environment variable → Built-in default
```

#### Parameters

| Parameter | Env Variable | Default | Description |
|---|---|---|---|
| `secret_key` | `JWT_SECRET_KEY` | Built-in fallback ⚠️ | HMAC signing secret |
| `algorithm` | `JWT_ALGORITHM` | `"HS256"` | Signing algorithm |
| `access_expire_minutes` | `JWT_ACCESS_EXPIRE_MINUTES` | `15` | Access token TTL in minutes |
| `refresh_expire_days` | `JWT_REFRESH_EXPIRE_DAYS` | `7` | Refresh token TTL in days |
| `issuer` | `JWT_ISSUER` | `None` | `iss` claim value |
| `audience` | `JWT_AUDIENCE` | `None` | `aud` claim value |

#### Returns

`TokenService` — Fully configured service instance.

#### Example

```python
# From explicit arguments
svc = create_token_service(
    secret_key="my-production-secret-key-256-bits",
    access_expire_minutes=30,
    refresh_expire_days=14,
    issuer="dalang-ai-api",
    audience="dalang-ai-frontend",
)

# From environment variables (set before running)
# JWT_SECRET_KEY=... JWT_ACCESS_EXPIRE_MINUTES=30 python app.py
svc = create_token_service()
```

---

## Environment Variables Reference

| Variable | Type | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | `str` | Built-in fallback ⚠️ | **Must be overridden in production.** Use `openssl rand -hex 32` to generate. |
| `JWT_ALGORITHM` | `str` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `15` | Access token lifetime in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `int` | `7` | Refresh token lifetime in days |
| `JWT_ISSUER` | `str` | _(none)_ | Optional `iss` claim |
| `JWT_AUDIENCE` | `str` | _(none)_ | Optional `aud` claim |

```bash
# Recommended production setup
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
export JWT_ALGORITHM="HS256"
export JWT_ACCESS_EXPIRE_MINUTES="15"
export JWT_REFRESH_EXPIRE_DAYS="7"
export JWT_ISSUER="dalang-ai-api"
export JWT_AUDIENCE="dalang-ai-web"
```

---

## Error Handling Reference

| Scenario | Exception | HTTP Status (recommended) |
|---|---|---|
| Token has expired | `TokenExpiredError` | `401 Unauthorized` |
| Token is malformed or tampered | `TokenInvalidError` | `401 Unauthorized` |
| Wrong token type (e.g. refresh used as access) | `TokenTypeMismatchError` | `401 Unauthorized` |
| Empty `sub` passed to generator | `ValueError` | `400 Bad Request` |
| Invalid `role` string | `ValueError` | `400 Bad Request` |
| Empty `secret_key` in config | `ValueError` | Startup error — fix configuration |

---

## Integration Examples

### FastAPI Bearer Token Middleware

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from token_service import create_token_service, TokenType, TokenExpiredError, TokenInvalidError
from auth_models import UserRole

app = FastAPI(title="Dalang-AI API")
bearer_scheme = HTTPBearer()
svc = create_token_service()  # reads from environment variables


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """FastAPI dependency that validates the Bearer access token."""
    token = credentials.credentials
    try:
        payload = svc.verify_token(token, expected_type=TokenType.ACCESS)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


@app.get("/me")
def get_profile(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.sub,
        "role": current_user.role.value,
        "token_expires": current_user.exp.isoformat(),
    }


@app.post("/auth/refresh")
def refresh(body: dict):
    """Exchange a refresh token for a new access token."""
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required.")

    # In production: look up the user's current role from the database
    user_role = UserRole.USER

    try:
        new_access = svc.refresh_access_token(refresh_token, role=user_role)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Refresh token has expired. Please log in again.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    return {"access_token": new_access, "token_type": "bearer"}
```

---

### Full Auth Lifecycle (Python)

```python
from auth_models import parse_user_create, UserRole
from token_service import create_token_service, TokenType, TokenExpiredError

# ── Setup ──────────────────────────────────────────────────────────────────
svc = create_token_service(
    secret_key="dalang-ai-dev-secret-key-32-bytes!!",
    access_expire_minutes=15,
    refresh_expire_days=7,
)

# ── Registration ───────────────────────────────────────────────────────────
user_create = parse_user_create({
    "username": "eve_admin",
    "email": "eve@dalang-ai.io",
    "password": "Adm!nP@ssw0rd",
    "role": "admin",
})
user_in_db = user_create.to_user_in_db()
print(f"Registered: {user_in_db.username} [{user_in_db.id}]")

# ── Login & Token Issuance ─────────────────────────────────────────────────
if user_in_db.verify_password("Adm!nP@ssw0rd"):
    access_token  = svc.generate_access_token(sub=user_in_db.id, role=user_in_db.role)
    refresh_token = svc.generate_refresh_token(sub=user_in_db.id)
    print(f"Access token:  {access_token[:50]}...")
    print(f"Refresh token: {refresh_token[:50]}...")

# ── API Request Verification ───────────────────────────────────────────────
payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)
print(f"Authorized: sub={payload.sub}, role={payload.role}, expires={payload.exp}")

# ── Token Rotation ─────────────────────────────────────────────────────────
new_access = svc.refresh_access_token(refresh_token, role=UserRole.ADMIN)
new_payload = svc.verify_token(new_access, expected_type=TokenType.ACCESS)
print(f"New access token issued. New jti: {new_payload.jti}")

# ── Inspect Without Verifying ──────────────────────────────────────────────
raw_claims = svc.decode_unverified(access_token)
print(f"Unverified claims: sub={raw_claims['sub']}, type={raw_claims['type']}")
```

---

### cURL Examples

#### Login and obtain tokens

```bash
# POST /auth/login
curl -X POST https://api.dalang-ai.io/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "S3cur3P@ss!"}'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

#### Call a protected endpoint

```bash
# GET /me — pass access token as Bearer
curl -X GET https://api.dalang-ai.io/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Response:
# {
#   "user_id": "a1b2c3d4-...",
#   "role": "user",
#   "token_expires": "2024-03-01T12:15:00+00:00"
# }
```

#### Refresh an expired access token

```bash
# POST /auth/refresh
curl -X POST https://api.dalang-ai.io/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

#### Decode a token (inspect claims without verification)

```bash
# Decode the payload section (base64url) — for debugging only
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInJvbGUiOiJ1c2VyIiwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTcwOTI5MDAwMCwiZXhwIjoxNzA5MjkwOTAwLCJqdGkiOiJhMWIyYzNkNC0uLi4ifQ.SIGNATURE" \
  | cut -d'.' -f2 \
  | base64 -d 2>/dev/null | python3 -m json.tool

# Output:
# {
#   "sub": "user-123",
#   "role": "user",
#   "type": "access",
#   "iat": 1709290000,
#   "exp": 1709290900,
#   "jti": "a1b2c3d4-..."
# }
```
