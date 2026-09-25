"""
auth_api.py
===========
Task T-301 — FastAPI authentication server.

Endpoints:
  POST /register  – Register a new user account.
  POST /login     – Authenticate and receive access + refresh tokens.
  POST /refresh   – Exchange a refresh token for a new access token.
  GET  /me        – Return the currently authenticated user's profile.

Design notes:
  • In-memory user store (dict keyed by lowercase username).
  • Passwords hashed via PasswordHasher (PBKDF2-HMAC-SHA256, T-101).
  • JWTs issued / verified via TokenService (HS256, T-102).
  • Bearer token authentication via Authorization header.
  • All error responses follow standard HTTP status codes.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from auth_models import UserCreate, UserInDB, UserPublic, UserRole, parse_user_create
from token_service import (
    TokenExpiredError,
    TokenInvalidError,
    TokenService,
    TokenType,
    TokenTypeMismatchError,
    create_token_service,
)

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Dalang-AI Auth API",
    description="Authentication server: register, login, refresh, and profile.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory user store  (lowercase username → UserInDB)
# ---------------------------------------------------------------------------

_USER_STORE: dict[str, UserInDB] = {}


def _get_user_by_username(username: str) -> Optional[UserInDB]:
    return _USER_STORE.get(username.lower())


def _get_user_by_email(email: str) -> Optional[UserInDB]:
    email_lower = email.strip().lower()
    for user in _USER_STORE.values():
        if user.email.lower() == email_lower:
            return user
    return None


def _save_user(user: UserInDB) -> None:
    _USER_STORE[user.username.lower()] = user


# ---------------------------------------------------------------------------
# Token service (singleton, configured from env vars or defaults)
# ---------------------------------------------------------------------------

_token_service: Optional[TokenService] = None


def get_token_service() -> TokenService:
    """Return the application-level TokenService (lazy singleton)."""
    global _token_service
    if _token_service is None:
        _token_service = create_token_service()
    return _token_service


# ---------------------------------------------------------------------------
# Pydantic request / response schemas
# ---------------------------------------------------------------------------

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")


class RegisterRequest(BaseModel):
    username: str = Field(..., description="Unique username (3-64 alphanumeric chars)")
    email: str = Field(..., description="Valid e-mail address")
    password: str = Field(..., min_length=8, description="Plain-text password (min 8 chars)")
    full_name: Optional[str] = Field(None, description="Optional display name")
    role: Optional[str] = Field(None, description="User role (default: user)")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not _USERNAME_REGEX.match(v):
            raise ValueError(
                "Username must be 3–64 characters and contain only letters, "
                "digits, underscores, hyphens, or dots."
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip()
        if not _EMAIL_REGEX.match(v):
            raise ValueError(f"Invalid e-mail address: {v!r}")
        return v.lower()

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return UserRole.USER.value
        try:
            return UserRole(v).value
        except ValueError:
            valid = [r.value for r in UserRole]
            raise ValueError(f"Invalid role {v!r}. Must be one of: {valid}")


class RegisterResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    full_name: Optional[str]
    created_at: str
    message: str = "User registered successfully."


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or e-mail address")
    password: str = Field(..., description="Plain-text password")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="A valid refresh JWT")


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    full_name: Optional[str]
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Auth dependency — extract and verify Bearer token
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=False)


def _require_access_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    svc: TokenService = Depends(get_token_service),
) -> UserInDB:
    """
    FastAPI dependency that validates the Bearer access token and returns the
    corresponding UserInDB.  Raises HTTP 401 on any auth failure.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = svc.verify_token(token, expected_type=TokenType.ACCESS)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )
    except (TokenInvalidError, TokenTypeMismatchError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid access token: {exc}",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    user = _get_user_by_username(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )
    return user


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    tags=["auth"],
)
def register(body: RegisterRequest) -> RegisterResponse:
    """
    Create a new user account.

    - **username**: 3–64 alphanumeric characters, underscores, hyphens, or dots.
    - **email**: Must be a valid e-mail address.
    - **password**: Minimum 8 characters.
    - **role**: Optional; defaults to `user`.

    Returns the newly created user profile (no password fields).
    """
    # Conflict checks
    if _get_user_by_username(body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username {body.username!r} is already taken.",
        )
    if _get_user_by_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"E-mail {body.email!r} is already registered.",
        )

    # Build and persist the user
    try:
        user_create: UserCreate = parse_user_create(
            {
                "username": body.username,
                "email": body.email,
                "password": body.password,
                "role": body.role or UserRole.USER.value,
                "full_name": body.full_name,
            }
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    user_in_db: UserInDB = user_create.to_user_in_db()
    _save_user(user_in_db)

    pub: UserPublic = user_in_db.to_public()
    return RegisterResponse(
        id=pub.id,
        username=pub.username,
        email=pub.email,
        role=pub.role.value,
        is_active=pub.is_active,
        full_name=pub.full_name,
        created_at=pub.created_at.isoformat(),
    )


@app.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain tokens",
    tags=["auth"],
)
def login(
    body: LoginRequest,
    svc: TokenService = Depends(get_token_service),
) -> TokenResponse:
    """
    Authenticate with username (or e-mail) and password.

    Returns a short-lived **access token** and a long-lived **refresh token**.
    """
    # Support login by username or e-mail
    user = _get_user_by_username(body.username) or _get_user_by_email(body.username)

    if user is None or not user.verify_password(body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )

    access_token = svc.generate_access_token(sub=user.username, role=user.role)
    refresh_token = svc.generate_refresh_token(sub=user.username)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    tags=["auth"],
)
def refresh(
    body: RefreshRequest,
    svc: TokenService = Depends(get_token_service),
) -> AccessTokenResponse:
    """
    Exchange a valid **refresh token** for a new **access token**.

    The refresh token must not be expired and must be of type `refresh`.
    """
    try:
        payload = svc.verify_token(body.refresh_token, expected_type=TokenType.REFRESH)
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )
    except (TokenInvalidError, TokenTypeMismatchError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {exc}",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""},
        )

    # Look up the user to get current role (may have changed)
    user = _get_user_by_username(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )

    new_access_token = svc.generate_access_token(sub=user.username, role=user.role)
    return AccessTokenResponse(access_token=new_access_token)


@app.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    tags=["auth"],
)
def me(current_user: UserInDB = Depends(_require_access_token)) -> UserProfileResponse:
    """
    Return the profile of the currently authenticated user.

    Requires a valid Bearer access token in the `Authorization` header.
    """
    pub: UserPublic = current_user.to_public()
    return UserProfileResponse(
        id=pub.id,
        username=pub.username,
        email=pub.email,
        role=pub.role.value,
        is_active=pub.is_active,
        full_name=pub.full_name,
        created_at=pub.created_at.isoformat(),
        updated_at=pub.updated_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Health-check (convenience, not part of the auth spec)
# ---------------------------------------------------------------------------


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# Dev entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    bind_host = os.environ.get("HOST", "127.0.0.1")
    bind_port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("auth_api:app", host=bind_host, port=bind_port, reload=True)
