# Auth Models Reference (`auth_models.py`)

![Status](https://img.shields.io/badge/Status-Sprint%201%20Ready-brightgreen)
![Module](https://img.shields.io/badge/Module-auth__models-blue)
![Coverage](https://img.shields.io/badge/Coverage-100%25-green)

The `auth_models` module provides the data structures, validation rules, and password hashing primitives required to build secure user registration, authentication, and persistence workflows.

---

## Table of Contents

1. [Architecture & Schema Lifecycle](#architecture--schema-lifecycle)
2. [Enums](#enums)
   - [UserRole](#userrole)
3. [Password Hashing Utility](#password-hashing-utility)
   - [PasswordHasher](#passwordhasher)
   - [Hash Format](#hash-format)
   - [Parameters & Recommendations](#parameters--recommendations)
4. [Data Schemas](#data-schemas)
   - [UserBase](#userbase)
   - [UserCreate](#usercreate)
   - [UserInDB](#userindb)
   - [UserPublic](#userpublic)
5. [Validation Rules](#validation-rules)
6. [Parser Functions](#parser-functions)
   - [parse_user_create](#parse_user_create)
   - [parse_user_in_db](#parse_user_in_db)
7. [Error Handling & Edge Cases](#error-handling--edge-cases)
8. [Integration Examples](#integration-examples)
   - [Full Registration & Authentication Flow](#full-registration--authentication-flow)
   - [FastAPI Route Integration](#fastapi-route-integration)

---

## Architecture & Schema Lifecycle

The module enforces strict separation between input schemas, persisted representations, and outbound public models to prevent password leaks:

```
[ Incoming Request Body ]
           │
           ▼
     parse_user_create()
           │
           ▼
      UserCreate  (contains plain-text password)
           │
           │  .to_user_in_db()
           │  (PasswordHasher.hash_password)
           ▼
       UserInDB   (contains hashed password; plain password dropped)
           │
     ┌─────┴───────────────┐
     ▼                     ▼
[ Persist to DB ]      .to_public()
                           │
                           ▼
                      UserPublic  (no password fields at all)
                           │
                           ▼
                   [ API JSON Response ]
```

---

## Enums

### `UserRole`

Extends `(str, Enum)`. Defines the role-based access control (RBAC) tiers available in the system.

```python
from auth_models import UserRole
```

| Member | Value | Description |
|---|---|---|
| `ADMIN` | `"admin"` | Full administrative privileges |
| `MODERATOR` | `"moderator"` | Content and user moderation capabilities |
| `USER` | `"user"` | Standard registered user (default) |
| `GUEST` | `"guest"` | Unauthenticated or restricted read-only access |

#### Usage

```python
role = UserRole("admin")          # UserRole.ADMIN
role = UserRole.USER              # UserRole.USER
role_str = UserRole.ADMIN.value   # "admin"

assert isinstance(UserRole.USER, str)   # True (string enum)
```

---

## Password Hashing Utility

### `PasswordHasher`

A cryptographic helper class providing PBKDF2-HMAC-SHA256 password hashing, verification, and parameter staleness checks.

```python
from auth_models import PasswordHasher
```

#### Class Attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `ALGORITHM` | `str` | `"sha256"` | Hashing digest algorithm |
| `ITERATIONS` | `int` | `260_000` | PBKDF2 iteration count (OWASP 2023 guideline) |
| `SALT_BYTES` | `int` | `32` | 256-bit cryptographically secure random salt |
| `HASH_BYTES` | `int` | `32` | 256-bit derived key length |
| `MIN_PASSWORD_LENGTH` | `int` | `8` | Minimum allowed plain-text password length |

---

### Hash Format

Hashes are serialized as a four-part colon-delimited string:

```
pbkdf2_sha256:<iterations>:<hex-salt>:<hex-digest>
```

**Example:**

```
pbkdf2_sha256:260000:7e4a11b6...64hexchars...:3f8b01c9...64hexchars...
```

- **Algorithm prefix:** `pbkdf2_sha256` ensures future algorithm versioning.
- **Iterations:** Integer indicating work factor used when hashed.
- **Hex-salt:** 64 hexadecimal characters (32 raw bytes).
- **Hex-digest:** 64 hexadecimal characters (32 raw bytes).

---

### Methods

#### `hash_password(plain_password: str) -> str`

Hashes a plain-text password using a freshly generated random salt and PBKDF2-HMAC-SHA256.

- **Parameters:**
  - `plain_password` (`str`): Plain-text password to hash.
- **Returns:** `str` — Formatted hash string.
- **Raises:**
  - `TypeError`: If `plain_password` is not a string.
  - `ValueError`: If `plain_password` is shorter than `MIN_PASSWORD_LENGTH` (8 characters).

```python
hashed = PasswordHasher.hash_password("S3cur3P@ssword!")
print(hashed)
# "pbkdf2_sha256:260000:4b6f...:a81e..."
```

---

#### `verify_password(plain_password: str, hashed_password: str) -> bool`

Verifies whether a plain-text password matches a stored hash string using constant-time comparison (`hmac.compare_digest`) to prevent timing side-channel attacks.

- **Parameters:**
  - `plain_password` (`str`): Candidate plain-text password.
  - `hashed_password` (`str`): Stored hash string.
- **Returns:** `bool` — `True` if the password matches, `False` otherwise (including malformed hashes).

```python
is_valid = PasswordHasher.verify_password("S3cur3P@ssword!", hashed)
# True

is_valid = PasswordHasher.verify_password("WrongPassword!", hashed)
# False
```

---

#### `needs_rehash(hashed_password: str) -> bool`

Checks whether a stored hash was produced with parameters below current security recommendations (e.g. fewer than 260 000 iterations or a salt shorter than 32 bytes).

- **Parameters:**
  - `hashed_password` (`str`): Stored hash string.
- **Returns:** `bool` — `True` if the hash should be regenerated upon next successful login.

```python
if PasswordHasher.needs_rehash(user_in_db.hashed_password):
    # Re-hash with current parameters and update DB
    user_in_db.hashed_password = PasswordHasher.hash_password(plain_password)
    save_to_db(user_in_db)
```

---

## Data Schemas

All schemas are standard Python `@dataclass` structures.

### `UserBase`

Common base class providing shared user identity and status fields.

```python
@dataclass
class UserBase:
    username: str
    email: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    full_name: Optional[str] = None
```

| Field | Type | Default | Validation / Constraints |
|---|---|---|---|
| `username` | `str` | _required_ | 3–64 characters; alphanumeric, `_`, `-`, `.` |
| `email` | `str` | _required_ | Valid e-mail pattern; automatically lowercased and stripped |
| `role` | `UserRole` | `UserRole.USER` | Coerced to `UserRole` enum |
| `is_active` | `bool` | `True` | User account active flag |
| `full_name` | `Optional[str]` | `None` | Display name |

---

### `UserCreate`

Inherits from `UserBase`. Used exclusively during user registration. Holds the plain-text password in memory.

```python
@dataclass
class UserCreate(UserBase):
    password: str = field(default="", repr=False)
```

- `repr=False`: Plain-text password is **omitted from `repr()` output** to prevent accidental logging.
- `__post_init__`: Enforces `PasswordHasher._validate_plain(password)`.

#### Methods

##### `to_user_in_db() -> UserInDB`

Computes the PBKDF2 hash of `self.password`, generates a new UUID4 `id`, and returns a `UserInDB` instance.

```python
user_create = UserCreate(
    username="alice",
    email="alice@example.com",
    password="SuperPassword123",
    role=UserRole.ADMIN,
)
user_in_db = user_create.to_user_in_db()

assert user_in_db.hashed_password.startswith("pbkdf2_sha256:")
assert not hasattr(user_in_db, "password")
```

---

### `UserInDB`

Inherits from `UserBase`. Represents the persisted user record in the database.

```python
@dataclass
class UserInDB(UserBase):
    hashed_password: str = field(default="", repr=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

| Field | Type | Default | Description |
|---|---|---|---|
| `hashed_password` | `str` | _required_ (`repr=False`) | Stored PBKDF2 hash string |
| `id` | `str` | UUID4 string | Unique user identifier |
| `created_at` | `datetime` | UTC now | Record creation timestamp |
| `updated_at` | `datetime` | UTC now | Last record update timestamp |

#### Methods

##### `verify_password(plain_password: str) -> bool`

Convenience wrapper around `PasswordHasher.verify_password(plain_password, self.hashed_password)`.

```python
if user_in_db.verify_password("candidate_password"):
    print("Authentication successful")
```

##### `to_public() -> UserPublic`

Strips all password-related fields and returns a `UserPublic` instance safe for API responses.

```python
public_user = user_in_db.to_public()
```

---

### `UserPublic`

Safe outbound representation returned to API consumers or frontends.

```python
@dataclass
class UserPublic:
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### Methods

##### `to_dict() -> dict`

Serializes the public user into a JSON-compatible dictionary.

```python
data = public_user.to_dict()
# {
#     "id": "e3b0c442-98fc-1c14-9afb-4c72e04f9810",
#     "username": "alice",
#     "email": "alice@example.com",
#     "role": "user",
#     "is_active": True,
#     "full_name": None,
#     "created_at": "2024-03-01T12:00:00+00:00",
#     "updated_at": "2024-03-01T12:00:00+00:00"
# }
```

---

## Validation Rules

| Field | Regex / Constraint | Valid Examples | Invalid Examples |
|---|---|---|---|
| `username` | `^[a-zA-Z0-9_.-]{3,64}$` | `alice`, `john_doe`, `user-123`, `dev.pro` | `ab` (too short), `a@b` (illegal char), `a"*c` |
| `email` | `^[^@\s]+@[^@\s]+\.[^@\s]+$` | `user@example.com`, `admin@sub.domain.org` | `plainaddress`, `missing@domain`, `a@b.` |
| `password` | `len(password) >= 8` | `8chars!!`, `LongSecurePassword` | `short` (< 8 chars), non-string types |

---

## Parser Functions

### `parse_user_create(data: dict) -> UserCreate`

Parses and validates a raw input dictionary (e.g., from an HTTP POST request payload) into a `UserCreate` instance.

#### Parameters

- `data` (`dict`): Raw input dictionary.

| Key | Type | Requirement | Default |
|---|---|---|---|
| `username` | `str` | Required | — |
| `email` | `str` | Required | — |
| `password` | `str` | Required | — |
| `role` | `str` \| `UserRole` | Optional | `"user"` |
| `is_active` | `bool` | Optional | `True` |
| `full_name` | `str` \| `None` | Optional | `None` |

#### Exceptions

| Exception | Condition |
|---|---|
| `TypeError` | `data` is not a `dict` |
| `KeyError` | Missing any of `username`, `email`, or `password` |
| `ValueError` | Validation fails on username, email, or password length |

#### Example

```python
from auth_models import parse_user_create

try:
    user = parse_user_create({
        "username": "charlie_k",
        "email": "Charlie@Domain.ORG",
        "password": "CorrectHorseBatteryStaple",
        "role": "moderator",
    })
    print(user.email)  # "charlie@domain.org" (lowercased)
except (KeyError, ValueError) as err:
    print(f"Validation failed: {err}")
```

---

### `parse_user_in_db(data: dict) -> UserInDB`

Parses a dictionary representing a stored database row into a `UserInDB` instance.

#### Parameters

- `data` (`dict`): Database row dictionary.

| Key | Type | Requirement | Default |
|---|---|---|---|
| `username` | `str` | Required | — |
| `email` | `str` | Required | — |
| `hashed_password` | `str` | Required | — |
| `id` | `str` | Optional | Auto-generated UUID4 |
| `role` | `str` \| `UserRole` | Optional | `"user"` |
| `is_active` | `bool` | Optional | `True` |
| `full_name` | `str` \| `None` | Optional | `None` |
| `created_at` | `str` (ISO) \| `datetime` | Optional | UTC now |
| `updated_at` | `str` (ISO) \| `datetime` | Optional | UTC now |

#### Exceptions

| Exception | Condition |
|---|---|
| `TypeError` | `data` is not a `dict` |
| `KeyError` | Missing any of `username`, `email`, or `hashed_password` |
| `ValueError` | Validation fails or date parsing fails |

#### Example

```python
from auth_models import parse_user_in_db

db_record = {
    "id": "11111111-2222-3333-4444-555555555555",
    "username": "dave",
    "email": "dave@example.com",
    "hashed_password": "pbkdf2_sha256:260000:abcdef...:123456...",
    "role": "user",
    "created_at": "2024-01-01T00:00:00+00:00",
}
user_db = parse_user_in_db(db_record)
assert user_db.id == "11111111-2222-3333-4444-555555555555"
```

---

## Error Handling & Edge Cases

| Scenario | Input | Error Raised | Message / Behavior |
|---|---|---|---|
| Missing required key | `{"username": "a", "email": "a@b.com"}` | `KeyError` | `"Missing required field(s): ['password']"` |
| Non-dict input | `"not a dict"` | `TypeError` | `"Expected dict, got 'str'."` |
| Password < 8 characters | `password="short"` | `ValueError` | `"Password must be at least 8 characters long."` |
| Invalid username format | `username="a"` | `ValueError` | `"Username must be 3–64 characters..."` |
| Invalid e-mail | `email="not-an-email"` | `ValueError` | `"Invalid e-mail address: 'not-an-email'"` |
| Empty hashed password | `hashed_password=""` | `ValueError` | `"hashed_password must not be empty."` |
| Corrupt hash verification | `verify_password("pw", "garbage")` | Returns `False` | No exception raised; cleanly returns `False` |
| Outdated hash check | `needs_rehash("garbage")` | Returns `True` | Flags corrupted or unparseable hash for re-hash |

---

## Integration Examples

### Full Registration & Authentication Flow

```python
from auth_models import parse_user_create, PasswordHasher, UserRole

# 1. Simulate registration payload from HTTP client
raw_signup = {
    "username": "jane_developer",
    "email": "Jane@Example.COM",
    "password": "StrongPassword999!",
    "full_name": "Jane Developer",
}

# 2. Parse and validate input
user_create = parse_user_create(raw_signup)

# 3. Hash password and prepare for storage
user_in_db = user_create.to_user_in_db()

# 4. Save `user_in_db` to database (pseudo-code)
# db.users.insert(user_in_db)

# 5. Later: simulate user login attempt
login_username = "jane_developer"
login_password = "StrongPassword999!"

# Retrieve user from database (pseudo-code)
# loaded_user = db.users.find_one({"username": login_username})

if user_in_db.verify_password(login_password):
    print("Login successful!")
    
    # Check if hash needs upgrading
    if PasswordHasher.needs_rehash(user_in_db.hashed_password):
        user_in_db.hashed_password = PasswordHasher.hash_password(login_password)
        # db.users.update(user_in_db)

    # Return safe user profile
    client_response = user_in_db.to_public().to_dict()
    print("Client response payload:", client_response)
else:
    print("Invalid credentials.")
```

### FastAPI Route Integration

```python
from fastapi import FastAPI, HTTPException, status
from auth_models import parse_user_create, parse_user_in_db, UserPublic

app = FastAPI(title="Auth API")
db_store: dict = {}

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: dict):
    try:
        user_create = parse_user_create(payload)
    except (KeyError, ValueError, TypeError) as err:
        raise HTTPException(status_code=400, detail=str(err))

    if user_create.username in db_store:
        raise HTTPException(status_code=409, detail="Username already exists.")

    user_in_db = user_create.to_user_in_db()
    db_store[user_create.username] = user_in_db

    return user_in_db.to_public().to_dict()

@app.post("/auth/login")
def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")

    user_in_db = db_store.get(username)
    if not user_in_db or not user_in_db.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return {"message": "Authenticated", "user": user_in_db.to_public().to_dict()}
```
