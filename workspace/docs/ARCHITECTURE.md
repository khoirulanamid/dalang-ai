# Dalang-AI Authentication Platform — Architecture

> **Diátaxis type:** Explanation — *Understanding-oriented*
> This document explains *why* the system is designed the way it is, the trade-offs made, and how the components relate to each other. For step-by-step setup instructions, see [QUICKSTART.md](QUICKSTART.md). For API reference, see [auth_models.md](auth_models.md) and [token_service.md](token_service.md).

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Map](#2-component-map)
3. [Authentication Flow](#3-authentication-flow)
   - [Registration](#31-registration-flow)
   - [Login and Token Issuance](#32-login-and-token-issuance-flow)
   - [Authenticated Request](#33-authenticated-request-flow)
   - [Token Refresh](#34-token-refresh-flow)
4. [Security Design Decisions](#4-security-design-decisions)
   - [Password Hashing Strategy](#41-password-hashing-strategy)
   - [JWT Token Pair Design](#42-jwt-token-pair-design)
   - [Token Type Enforcement](#43-token-type-enforcement)
   - [Schema Separation and Password Lifecycle](#44-schema-separation-and-password-lifecycle)
5. [Module Responsibilities](#5-module-responsibilities)
   - [auth_models.py](#51-auth_modelspy)
   - [token_service.py](#52-token_servicepy)
   - [auth_api.py](#53-auth_apipy)
   - [frontend_auth/](#54-frontend_auth)
6. [Role-Based Access Control](#6-role-based-access-control)
7. [Configuration Architecture](#7-configuration-architecture)
8. [Deployment Topology](#8-deployment-topology)
9. [Design Trade-offs and Constraints](#9-design-trade-offs-and-constraints)

---

## 1. System Overview

Dalang-AI is a production-ready authentication platform built on three tightly integrated layers:

| Layer | Technology | Responsibility |
|---|---|---|
| **Data & Hashing** | `auth_models.py` (pure Python) | User schemas, role enforcement, PBKDF2 password hashing |
| **Token Engine** | `token_service.py` (PyJWT) | JWT generation, verification, and rotation |
| **HTTP API** | `auth_api.py` (FastAPI) | REST endpoints, request validation, dependency injection |
| **Frontend** | `frontend_auth/` (Vanilla JS + Nginx) | Browser-based auth portal, token storage, auto-refresh |

The platform deliberately avoids heavy ORM or framework dependencies in its core modules (`auth_models`, `token_service`). This keeps the security-critical code auditable, portable, and independently testable.

---

## 2. Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DALANG-AI PLATFORM                            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND (Nginx + JS)                      │  │
│  │  frontend_auth/index.html  ·  app.js  ·  style.css           │  │
│  │  • Login / Register forms                                     │  │
│  │  • Token storage (localStorage / sessionStorage)             │  │
│  │  • Auto-refresh on 401                                        │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
│                         │  HTTP (REST/JSON)                         │
│  ┌──────────────────────▼───────────────────────────────────────┐  │
│  │                  AUTH API  (FastAPI + Uvicorn)                │  │
│  │  auth_api.py                                                  │  │
│  │  POST /register  POST /login  POST /refresh  GET /me          │  │
│  │                                                               │  │
│  │  ┌─────────────────────┐   ┌──────────────────────────────┐  │  │
│  │  │   auth_models.py    │   │      token_service.py        │  │  │
│  │  │                     │   │                              │  │  │
│  │  │  UserRole (Enum)    │   │  TokenConfig (dataclass)     │  │  │
│  │  │  UserBase           │   │  TokenType (Enum)            │  │  │
│  │  │  UserCreate         │   │  TokenPayload (dataclass)    │  │  │
│  │  │  UserInDB           │   │  TokenService                │  │  │
│  │  │  UserPublic         │   │  create_token_service()      │  │  │
│  │  │  PasswordHasher     │   │                              │  │  │
│  │  │  parse_user_create()│   │  Exceptions:                 │  │  │
│  │  │  parse_user_in_db() │   │  TokenExpiredError           │  │  │
│  │  └─────────────────────┘   │  TokenInvalidError           │  │  │
│  │                            │  TokenTypeMismatchError      │  │  │
│  │                            └──────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  ENVIRONMENT CONFIGURATION                    │  │
│  │  .env  (from .env.example)                                    │  │
│  │  JWT_SECRET_KEY · JWT_ALGORITHM · JWT_ACCESS_EXPIRE_MINUTES  │  │
│  │  JWT_REFRESH_EXPIRE_DAYS · JWT_ISSUER · JWT_AUDIENCE         │  │
│  │  APP_ENV · APP_HOST · APP_PORT · CORS_ALLOWED_ORIGINS        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Authentication Flow

### 3.1 Registration Flow

```
Client                    auth_api.py              auth_models.py
  │                           │                          │
  │── POST /register ────────►│                          │
  │   {username, email,       │                          │
  │    password, role}        │                          │
  │                           │── parse_user_create() ──►│
  │                           │                          │ Validate fields
  │                           │                          │ Enforce password policy
  │                           │◄─ UserCreate ────────────│
  │                           │                          │
  │                           │── .to_user_in_db() ─────►│
  │                           │                          │ PBKDF2-HMAC-SHA256
  │                           │                          │ 260,000 iterations
  │                           │                          │ 256-bit random salt
  │                           │◄─ UserInDB ──────────────│
  │                           │   (hashed_password,      │
  │                           │    plain password gone)  │
  │                           │                          │
  │                           │ Store in _USER_STORE     │
  │                           │                          │
  │◄─ 201 Created ────────────│                          │
  │   UserPublic (no password)│                          │
```

**Key design point:** The plain-text password exists only inside `UserCreate` and only for the duration of the `.to_user_in_db()` call. It is never written to any store, log, or response body.

---

### 3.2 Login and Token Issuance Flow

```
Client                    auth_api.py              token_service.py
  │                           │                          │
  │── POST /login ───────────►│                          │
  │   {username, password}    │                          │
  │                           │ Lookup user by username  │
  │                           │ user.verify_password()   │
  │                           │ (hmac.compare_digest)    │
  │                           │                          │
  │                           │── generate_access_token()►│
  │                           │                          │ Sign JWT (HS256)
  │                           │                          │ sub, role, type,
  │                           │                          │ iat, exp, jti
  │                           │◄─ access_token ──────────│
  │                           │                          │
  │                           │── generate_refresh_token()►│
  │                           │                          │ Sign JWT (HS256)
  │                           │                          │ sub, type, iat,
  │                           │                          │ exp, jti
  │                           │◄─ refresh_token ─────────│
  │                           │                          │
  │◄─ 200 OK ─────────────────│                          │
  │   {access_token,          │                          │
  │    refresh_token,         │                          │
  │    token_type: "bearer"}  │                          │
```

---

### 3.3 Authenticated Request Flow

```
Client                    auth_api.py              token_service.py
  │                           │                          │
  │── GET /me ───────────────►│                          │
  │   Authorization:          │                          │
  │   Bearer <access_token>   │                          │
  │                           │── verify_token() ───────►│
  │                           │   expected_type=ACCESS   │ Decode JWT
  │                           │                          │ Verify signature
  │                           │                          │ Check expiry
  │                           │                          │ Enforce type claim
  │                           │◄─ TokenPayload ──────────│
  │                           │   {sub, role, jti, exp}  │
  │                           │                          │
  │                           │ Lookup user by sub       │
  │                           │ Check is_active flag     │
  │                           │                          │
  │◄─ 200 OK ─────────────────│                          │
  │   UserProfileResponse     │                          │
```

---

### 3.4 Token Refresh Flow

```
Client                    auth_api.py              token_service.py
  │                           │                          │
  │── POST /refresh ─────────►│                          │
  │   {refresh_token}         │                          │
  │                           │── refresh_access_token()►│
  │                           │                          │ Verify refresh JWT
  │                           │                          │ Enforce type=REFRESH
  │                           │                          │ Extract sub
  │                           │◄─ new access_token ──────│
  │                           │                          │
  │                           │ Lookup user by sub       │
  │                           │ Check is_active flag     │
  │                           │                          │
  │◄─ 200 OK ─────────────────│                          │
  │   {access_token,          │                          │
  │    token_type: "bearer"}  │                          │
```

**Key design point:** The refresh endpoint issues a new access token but does *not* rotate the refresh token. This is a deliberate simplicity trade-off — see [Section 9](#9-design-trade-offs-and-constraints).

---

## 4. Security Design Decisions

### 4.1 Password Hashing Strategy

The platform uses **PBKDF2-HMAC-SHA256** with the following parameters:

| Parameter | Value | Rationale |
|---|---|---|
| Algorithm | SHA-256 | FIPS 140-2 compliant, universally available |
| Iterations | 260,000 | OWASP 2023 minimum recommendation |
| Salt length | 32 bytes (256 bits) | Prevents rainbow table attacks |
| Digest length | 32 bytes (256 bits) | Sufficient collision resistance |
| Comparison | `hmac.compare_digest` | Constant-time; prevents timing attacks |

The hash format is a colon-delimited string stored as a single field:

```
pbkdf2_sha256:<iterations>:<hex-salt>:<hex-digest>
```

This format is self-describing: the iteration count is embedded in the hash, which allows `PasswordHasher.needs_rehash()` to detect hashes produced with weaker parameters and flag them for upgrade on next successful login — without requiring a forced password reset.

**Why not bcrypt or Argon2?** PBKDF2-HMAC-SHA256 is the only algorithm in Python's standard library (`hashlib`) that meets OWASP 2023 requirements. This eliminates the `bcrypt` or `argon2-cffi` dependency, keeping the security-critical module dependency-free and auditable.

---

### 4.2 JWT Token Pair Design

The platform issues two distinct token types that serve different purposes:

| Token | Lifetime | Claims | Purpose |
|---|---|---|---|
| **Access token** | 15 minutes (default) | `sub`, `role`, `type=access`, `iat`, `exp`, `jti` | Authorize individual API requests |
| **Refresh token** | 7 days (default) | `sub`, `type=refresh`, `iat`, `exp`, `jti` | Obtain new access tokens without re-login |

**Why short-lived access tokens?** Access tokens are stateless — the server cannot revoke them once issued. A 15-minute window limits the blast radius if a token is intercepted. The refresh token's longer lifetime provides user convenience without requiring the user to re-enter credentials frequently.

**Why does the refresh token omit the `role` claim?** The refresh token's sole purpose is to prove that the user previously authenticated. The role is re-read from the user store at refresh time, which means role changes (e.g., a user being demoted) take effect within one access token lifetime without requiring a full logout.

---

### 4.3 Token Type Enforcement

Every `verify_token()` call requires an `expected_type` argument:

```python
# This raises TokenTypeMismatchError if a refresh token is passed
payload = svc.verify_token(token, expected_type=TokenType.ACCESS)
```

This prevents **token substitution attacks**, where an attacker uses a refresh token (which may have been obtained through a less-secure channel) in place of an access token to call protected endpoints.

---

### 4.4 Schema Separation and Password Lifecycle

The module defines four distinct user schemas, each with a specific scope:

```
UserCreate          UserInDB            UserPublic
(input only)   →   (storage only)  →   (output only)
plain password      hashed password     no password field
```

This separation is enforced structurally, not by convention. `UserPublic` has no `hashed_password` attribute — it is impossible to accidentally serialize a password hash into an API response.

---

## 5. Module Responsibilities

### 5.1 `auth_models.py`

**Responsibility:** Define the data contract for users and enforce password security at the data layer.

This module has **zero external dependencies** beyond the Python standard library. It is intentionally isolated so that it can be audited, tested, and reused independently of any web framework.

Key design choices:
- Uses `dataclass` instead of Pydantic to avoid the Pydantic dependency in the core security module.
- Validation is explicit and raises typed exceptions (`ValueError`, `TypeError`, `KeyError`) rather than framework-specific errors.
- `parse_user_create()` and `parse_user_in_db()` are the only sanctioned entry points for constructing user objects from raw data.

### 5.2 `token_service.py`

**Responsibility:** Issue, verify, and rotate JWTs with configurable parameters.

This module depends only on `PyJWT` and `auth_models`. It exposes a clean service interface (`TokenService`) that is instantiated once and reused across requests.

Key design choices:
- `TokenConfig` is a dataclass, not a global singleton. This makes the service fully testable with different configurations in the same process.
- `create_token_service()` is a factory function that reads environment variables as fallback, enabling both programmatic and environment-driven configuration.
- The `jti` (JWT ID) claim is a UUID4 generated per token. This provides a unique identifier for each token, enabling future revocation list implementations without changing the token format.

### 5.3 `auth_api.py`

**Responsibility:** Expose the authentication operations as HTTP endpoints and wire together `auth_models` and `token_service`.

Key design choices:
- Uses FastAPI's `Depends()` system for the `_require_access_token` dependency, which keeps route handlers clean and makes the auth guard reusable.
- The in-memory `_USER_STORE` is intentional for Sprint 1. It is keyed by lowercase username to prevent case-sensitivity collisions. Replacing it with a database-backed store requires changing only the `_get_user_by_username` and `_get_user_by_email` functions.
- Pydantic `BaseModel` is used for request/response schemas at the API boundary, while the core modules use plain dataclasses. This keeps the framework dependency contained to the API layer.

### 5.4 `frontend_auth/`

**Responsibility:** Provide a browser-based interface for the authentication API.

Key design choices:
- Vanilla JavaScript with no build step. This eliminates Node.js toolchain complexity for a security-focused demo frontend.
- Tokens are stored in `localStorage` (with `sessionStorage` fallback when "Remember Me" is disabled). This is a pragmatic choice for a demo; production deployments should evaluate `HttpOnly` cookie storage to mitigate XSS risk.
- The frontend implements automatic token refresh: when an API call returns `401 Unauthorized`, the app transparently calls `POST /refresh` and retries the original request.

---

## 6. Role-Based Access Control

The platform defines four roles in a fixed hierarchy:

| Role | Value | Intended Use |
|---|---|---|
| `ADMIN` | `"admin"` | Full platform access, user management |
| `MODERATOR` | `"moderator"` | Content moderation, elevated read access |
| `USER` | `"user"` | Standard authenticated user |
| `GUEST` | `"guest"` | Limited, unauthenticated-equivalent access |

Roles are embedded in the access token's `role` claim at login time. The API reads the role from the verified token payload — it does not re-query the database on every request. This is a deliberate performance trade-off: role changes propagate within one access token lifetime (default: 15 minutes).

The `UserRole` enum inherits from both `str` and `Enum`, which means role values serialize naturally to JSON strings and can be compared directly to string literals.

---

## 7. Configuration Architecture

All runtime configuration flows through environment variables, which are resolved in a consistent priority order:

```
Explicit constructor argument  (highest priority)
        │
        ▼
Environment variable (JWT_SECRET_KEY, JWT_ALGORITHM, etc.)
        │
        ▼
Compiled-in default            (lowest priority)
```

The `create_token_service()` factory implements this resolution. In production (`APP_ENV=production`), the factory **rejects** the compiled-in default secret and raises a `ValueError` if `JWT_SECRET_KEY` is not set. This prevents accidental deployment with a known-weak secret.

Environment variables are documented exhaustively in `.env.example`. Copy that file to `.env` before running the platform:

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET_KEY to a strong random value
```

---

## 8. Deployment Topology

The platform ships with a Docker Compose configuration that runs two containers:

```
┌─────────────────────────────────────────────────────┐
│                   Host Machine                      │
│                                                     │
│  Port 80 ──────────────────────────────────────┐   │
│                                                │   │
│  ┌─────────────────────────────────────────┐   │   │
│  │         Nginx Container                 │   │   │
│  │  Serves frontend_auth/ static files     │◄──┘   │
│  │  Proxies /api/* → backend:8000          │       │
│  └──────────────────────┬──────────────────┘       │
│                         │ Internal Docker network   │
│  ┌──────────────────────▼──────────────────┐       │
│  │         Backend Container               │       │
│  │  Uvicorn + FastAPI (auth_api.py)        │       │
│  │  Port 8000 (internal only)              │       │
│  └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

The backend port is not exposed to the host in production — all traffic enters through Nginx. This means:
- Nginx handles TLS termination.
- The backend never receives raw HTTPS traffic.
- CORS is configured on the backend for the Nginx origin.

---

## 9. Design Trade-offs and Constraints

| Decision | Trade-off | Rationale |
|---|---|---|
| **In-memory user store** | Data lost on restart; not horizontally scalable | Keeps Sprint 1 dependency-free; designed for easy swap to a database |
| **No refresh token rotation** | A stolen refresh token remains valid until expiry | Simplifies the stateless design; rotation requires a token store (e.g., Redis) |
| **No token revocation list** | Issued tokens cannot be invalidated before expiry | Stateless JWTs by design; the `jti` claim is present to enable future revocation |
| **PBKDF2 over Argon2** | Slightly less memory-hard than Argon2id | Zero external dependencies; meets OWASP 2023 requirements |
| **HS256 default** | Shared secret; key compromise affects all tokens | Simpler to operate than RS256; RS256 is supported for asymmetric deployments |
| **Role in access token** | Role changes take up to 15 minutes to propagate | Avoids a database lookup on every authenticated request |
| **Vanilla JS frontend** | No component framework, no build toolchain | Reduces attack surface and operational complexity for a security demo |

---

*This document is classified as **Explanation** under the [Diátaxis Framework](https://diataxis.fr/). It describes the reasoning behind design decisions. For operational instructions, see [QUICKSTART.md](QUICKSTART.md).*
