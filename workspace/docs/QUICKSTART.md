# Quickstart: Run Dalang-AI Authentication in 5 Minutes

> **Diátaxis type:** Tutorial — *Learning-oriented*
> This tutorial walks you through setting up the Dalang-AI authentication platform from scratch, registering a user, logging in, calling a protected endpoint, and refreshing a token. You learn by doing — every step produces a visible result.
>
> **Prerequisites:** Python 3.11+, `git`, and optionally Docker + Docker Compose.
> **Time to complete:** ~5 minutes.

---

## Table of Contents

1. [What You Build](#1-what-you-build)
2. [Option A — Run with Python directly](#2-option-a--run-with-python-directly)
   - [Step 1: Clone and install dependencies](#step-1-clone-and-install-dependencies)
   - [Step 2: Configure environment variables](#step-2-configure-environment-variables)
   - [Step 3: Start the API server](#step-3-start-the-api-server)
   - [Step 4: Register a user](#step-4-register-a-user)
   - [Step 5: Log in and receive tokens](#step-5-log-in-and-receive-tokens)
   - [Step 6: Call a protected endpoint](#step-6-call-a-protected-endpoint)
   - [Step 7: Refresh the access token](#step-7-refresh-the-access-token)
3. [Option B — Run with Docker Compose](#3-option-b--run-with-docker-compose)
4. [Use the Python modules directly](#4-use-the-python-modules-directly)
   - [Step 1: Hash a password and create a user](#step-1-hash-a-password-and-create-a-user)
   - [Step 2: Issue and verify tokens](#step-2-issue-and-verify-tokens)
   - [Step 3: Refresh an access token](#step-3-refresh-an-access-token)
5. [Run the test suite](#5-run-the-test-suite)
6. [What to do next](#6-what-to-do-next)

---

## 1. What You Build

By the end of this tutorial, you have a running authentication API that:

- Accepts user registration with password hashing (PBKDF2-HMAC-SHA256, 260,000 iterations).
- Issues signed JWT access tokens (15-minute lifetime) and refresh tokens (7-day lifetime).
- Protects endpoints with Bearer token authentication.
- Rotates access tokens via a refresh endpoint.

The full flow looks like this:

```
Register ──► Login ──► GET /me (protected) ──► POST /refresh ──► GET /me (new token)
```

---

## 2. Option A — Run with Python directly

### Step 1: Clone and install dependencies

```bash
git clone https://github.com/your-org/dalang-ai.git
cd dalang-ai

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn PyJWT cryptography bcrypt passlib httpx
```

**Expected output:** pip prints a list of installed packages with no errors.

---

### Step 2: Configure environment variables

```bash
# Copy the template
cp .env.example .env

# Generate a strong secret key and write it to .env
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(64))" >> .env
```

Open `.env` and verify that `JWT_SECRET_KEY` is set to a long random string. The file looks like this:

```bash
# .env (excerpt)
JWT_SECRET_KEY=a1b2c3d4e5f6...   # 128 hex characters
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
APP_ENV=development
```

> **Security note:** Never commit `.env` to version control. The `.gitignore` already excludes it.

---

### Step 3: Start the API server

```bash
# Load environment variables and start Uvicorn
export $(grep -v '^#' .env | xargs)
uvicorn auth_api:app --host 127.0.0.1 --port 8000 --reload
```

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Leave this terminal open. Open a new terminal for the next steps.

---

### Step 4: Register a user

```bash
curl -s -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "Password123!",
    "role": "user",
    "full_name": "Alice Smith"
  }' | python3 -m json.tool
```

**Expected response (HTTP 201):**

```json
{
    "id": "72d12a8c-ea2c-4d0a-9621-3941488bf001",
    "username": "alice",
    "email": "alice@example.com",
    "role": "user",
    "is_active": true,
    "full_name": "Alice Smith",
    "created_at": "2024-03-01T12:00:00.000000+00:00",
    "message": "User registered successfully."
}
```

Notice that the response contains no password field — not even a hash. The `UserPublic` schema structurally prevents password data from appearing in API responses.

---

### Step 5: Log in and receive tokens

```bash
curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "Password123!"
  }' | python3 -m json.tool
```

**Expected response (HTTP 200):**

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

Save the tokens to shell variables for the next steps:

```bash
# Run login and capture tokens
TOKENS=$(curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "Password123!"}')

ACCESS_TOKEN=$(echo "$TOKENS" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
REFRESH_TOKEN=$(echo "$TOKENS" | python3 -c "import sys,json; print(json.load(sys.stdin)['refresh_token'])")

echo "Access token captured: ${ACCESS_TOKEN:0:40}..."
echo "Refresh token captured: ${REFRESH_TOKEN:0:40}..."
```

---

### Step 6: Call a protected endpoint

```bash
curl -s -X GET http://127.0.0.1:8000/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | python3 -m json.tool
```

**Expected response (HTTP 200):**

```json
{
    "id": "72d12a8c-ea2c-4d0a-9621-3941488bf001",
    "username": "alice",
    "email": "alice@example.com",
    "role": "user",
    "is_active": true,
    "full_name": "Alice Smith",
    "created_at": "2024-03-01T12:00:00.000000+00:00",
    "updated_at": "2024-03-01T12:00:00.000000+00:00"
}
```

Try calling the endpoint without a token to see the error response:

```bash
curl -s -X GET http://127.0.0.1:8000/me | python3 -m json.tool
```

**Expected response (HTTP 401):**

```json
{
    "detail": "Missing Authorization header."
}
```

---

### Step 7: Refresh the access token

```bash
curl -s -X POST http://127.0.0.1:8000/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" \
  | python3 -m json.tool
```

**Expected response (HTTP 200):**

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

The new access token has a fresh 15-minute expiry. Use it exactly as you used the original access token in Step 6.

---

## 3. Option B — Run with Docker Compose

Docker Compose starts both the backend API and the Nginx frontend in one command.

```bash
# Copy and configure environment
cp .env.example .env
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(64))" >> .env

# Build and start all services
docker compose up --build
```

**Expected output:**

```
[+] Building ...
[+] Running 2/2
 ✔ Container dalang-ai-backend-1   Started
 ✔ Container dalang-ai-frontend-1  Started
```

The services are now available at:

| Service | URL |
|---|---|
| Frontend (Auth Portal) | http://localhost:80 |
| Backend API | http://localhost:8000 |
| API Interactive Docs | http://localhost:8000/docs |

Open http://localhost:80 in your browser to use the visual login and registration interface.

To stop all services:

```bash
docker compose down
```

---

## 4. Use the Python modules directly

You can use `auth_models` and `token_service` as standalone libraries without the FastAPI server.

### Step 1: Hash a password and create a user

```python
from auth_models import parse_user_create, UserRole

# Build a validated user from raw input data
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "Password123!",
    "role": "user",
    "full_name": "Alice Smith",
}

user_create = parse_user_create(user_data)
# user_create.password == "Password123!"  (plain text, in memory only)

# Hash the password and produce a storage-safe object
user_in_db = user_create.to_user_in_db()
# user_in_db.hashed_password == "pbkdf2_sha256:260000:<hex-salt>:<hex-digest>"
# user_create.password is no longer referenced

# Verify a login attempt
is_valid = user_in_db.verify_password("Password123!")
print(f"Password valid: {is_valid}")   # Password valid: True

is_valid = user_in_db.verify_password("WrongPassword!")
print(f"Wrong password: {is_valid}")   # Wrong password: False

# Produce a safe public representation (no password fields)
public_profile = user_in_db.to_public()
print(public_profile.to_dict())
# {
#   "id": "...",
#   "username": "alice",
#   "email": "alice@example.com",
#   "role": "user",
#   "is_active": True,
#   "full_name": "Alice Smith",
#   "created_at": "2024-03-01T12:00:00+00:00",
#   "updated_at": "2024-03-01T12:00:00+00:00"
# }
```

---

### Step 2: Issue and verify tokens

```python
from token_service import create_token_service, TokenType
from auth_models import UserRole

# Create the token service (reads JWT_SECRET_KEY from env, or use explicit key)
svc = create_token_service(secret_key="your-256-bit-secret-at-least-32-chars!")

# Issue an access token for the user
access_token = svc.generate_access_token(
    sub="alice",
    role=UserRole.USER,
)
print(f"Access token: {access_token[:40]}...")

# Issue a refresh token
refresh_token = svc.generate_refresh_token(sub="alice")
print(f"Refresh token: {refresh_token[:40]}...")

# Verify the access token — raises an exception if invalid or expired
payload = svc.verify_token(access_token, expected_type=TokenType.ACCESS)
print(f"Subject: {payload.sub}")    # Subject: alice
print(f"Role: {payload.role}")      # Role: user
print(f"Token ID: {payload.jti}")   # Token ID: <uuid4>
print(f"Expires: {payload.exp}")    # Expires: <UTC datetime>
```

---

### Step 3: Refresh an access token

```python
from token_service import create_token_service, TokenType
from auth_models import UserRole

svc = create_token_service(secret_key="your-256-bit-secret-at-least-32-chars!")

# Assume refresh_token was obtained from generate_refresh_token()
# refresh_token = svc.generate_refresh_token(sub="alice")

new_access_token = svc.refresh_access_token(
    refresh_token=refresh_token,
    role=UserRole.USER,   # Re-read from your user store for up-to-date role
)

# Verify the new token
new_payload = svc.verify_token(new_access_token, expected_type=TokenType.ACCESS)
print(f"New token subject: {new_payload.sub}")   # New token subject: alice
print(f"New token JTI: {new_payload.jti}")       # New token JTI: <new uuid4>
```

> **Note:** Pass the user's current role from your user store when calling `refresh_access_token()`. This ensures that role changes (for example, a user being promoted to `moderator`) take effect on the next token refresh.

---

## 5. Run the test suite

The test suite covers 290 test cases across all modules.

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Run all tests
pytest -v

# Run a specific test file
pytest test_token.py -v

# Run a specific test class
pytest test_auth_api.py::TestRegisterEndpoint -v

# Run tests matching a keyword
pytest -k "refresh" -v
```

**Expected output:**

```
============================= test session starts ==============================
collected 290 items

test_auth_api.py .................................                       [ 11%]
test_e2e_flow.py ......................................................  [ 30%]
test_frontend_auth.py ..............................................     [ 75%]
test_security.py .............                                          [ 88%]
test_token.py .................................                         [100%]

============================= 290 passed in 47.01s =============================
```

---

## 6. What to do next

You have a working authentication platform. Here are the natural next steps:

| Goal | Where to look |
|---|---|
| Understand the security architecture and design decisions | [docs/ARCHITECTURE.md](ARCHITECTURE.md) |
| Look up every parameter and error code for `auth_models` | [docs/auth_models.md](auth_models.md) |
| Look up every parameter and error code for `token_service` | [docs/token_service.md](token_service.md) |
| Explore the interactive API documentation | http://localhost:8000/docs (when server is running) |
| Replace the in-memory user store with a database | Edit `_get_user_by_username()` and `_get_user_by_email()` in `auth_api.py` |
| Switch from HS256 to RS256 (asymmetric keys) | Set `JWT_ALGORITHM=RS256` and provide RSA key material to `create_token_service()` |
| Add token revocation | Implement a blocklist store keyed by `jti` and check it in `verify_token()` |

---

*This document is classified as **Tutorial** under the [Diátaxis Framework](https://diataxis.fr/). It teaches by doing. For conceptual explanations of why the system works this way, see [ARCHITECTURE.md](ARCHITECTURE.md).*
