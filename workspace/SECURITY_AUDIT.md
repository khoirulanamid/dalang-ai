# Security Audit Report — Dalang-AI Auth Service
**Audit ID:** T-601  
**Auditor:** Kai (Application Security Specialist & Auditor — Dalang-AI Team)  
**Scope:** `auth_models.py`, `token_service.py`, `auth_api.py`  
**Scan Date:** 2025-07-14  
**Tools Used:** Bandit (SAST), pip-audit (CVE), Entropy / Secret Check (custom)

---

## 1. Executive Summary

The Dalang-AI authentication service implements a well-structured, layered security architecture. Password hashing uses PBKDF2-HMAC-SHA256 at 260,000 iterations (OWASP 2023 recommendation), JWT tokens are signed with HS256 and carry explicit `type` claims to prevent token-type confusion, and the API enforces Bearer-token authentication on all protected endpoints.

The scan uncovered **zero HIGH-severity issues**. Two categories of findings require attention before production deployment:

| Severity | Count | Summary |
|----------|-------|---------|
| MEDIUM   | 1     | Server binds to `0.0.0.0` — exposes all network interfaces |
| LOW      | 4     | Hardcoded password literals in test code (acceptable in test context) |
| WARN     | 1     | Default fallback JWT secret in `token_service.py` — must be overridden via env var |

No known CVEs were found in any installed dependency (pip-audit clean).

---

## 2. Overall Security Grade

> **B+ (Good — Minor Issues to Remediate Before Production)**

The codebase demonstrates strong security fundamentals. The two actionable items (bind-all-interfaces and default JWT secret fallback) are straightforward to fix and do not represent exploitable vulnerabilities in a properly configured deployment, but they create unnecessary risk if configuration steps are missed.

---

## 3. CVSS Scoring Table

| ID | File | Line | Severity | CVSS v3.1 Score | Vector |
|----|------|------|----------|-----------------|--------|
| F-001 | `auth_api.py` | 426 | MEDIUM | **5.3** | AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N |
| F-002 | `token_service.py` | (factory fn) | MEDIUM-WARN | **4.8** | AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N |
| F-003 | `auth_models.py` | 352, 382, 398, 406 | LOW | **0.0** | Test-only — no production exposure |

---

## 4. Per-Finding Analysis

---

### F-001 — Hardcoded Bind-All-Interfaces (`0.0.0.0`)

| Attribute | Detail |
|-----------|--------|
| **Tool** | Bandit B104 |
| **File** | `auth_api.py` |
| **Line** | 426 |
| **Severity** | MEDIUM |
| **CWE** | [CWE-605](https://cwe.mitre.org/data/definitions/605.html) — Multiple Binds to the Same Port |
| **CVSS v3.1** | 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N) |

**Description:**  
The dev entry-point at the bottom of `auth_api.py` calls:
```python
uvicorn.run("auth_api:app", host="0.0.0.0", port=8000, reload=True)
```
Binding to `0.0.0.0` causes the server to listen on **all** available network interfaces, including any public-facing ones. In a cloud or container environment where network segmentation is not enforced externally, this can expose the service to unintended network traffic. Additionally, `reload=True` is a development-only flag that enables hot-reloading and should never be used in production.

**Risk:**  
- Unintended exposure of the auth service on public/internal interfaces.
- `reload=True` in production enables file-system watching and can be a vector for denial-of-service or unexpected restarts.

**Remediation:**
1. Remove or guard the `__main__` block so it is never executed in production.
2. Bind to `127.0.0.1` (loopback) for local development, and let the production container orchestrator (e.g., Kubernetes, Docker) handle port exposure.
3. Set `reload=False` (or omit it) in any non-development invocation.

```python
# Recommended dev entry-point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("auth_api:app", host="127.0.0.1", port=8000, reload=False)
```

---

### F-002 — Default Fallback JWT Secret in `token_service.py`

| Attribute | Detail |
|-----------|--------|
| **Tool** | Entropy / Secret Check |
| **File** | `token_service.py` |
| **Location** | `_DEFAULT_SECRET` constant & `create_token_service()` factory |
| **Severity** | MEDIUM-WARN |
| **CWE** | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) — Use of Hard-coded Credentials |
| **CVSS v3.1** | 4.8 (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N) |

**Description:**  
`token_service.py` defines a module-level fallback secret:
```python
_DEFAULT_SECRET: str = "change-me-in-production-please-use-a-long-random-secret"
```
The `create_token_service()` factory uses this value when `JWT_SECRET_KEY` is not set in the environment:
```python
resolved_secret = (
    secret_key
    or os.environ.get("JWT_SECRET_KEY")
    or _DEFAULT_SECRET          # ← silent fallback
)
```
If a deployment omits the `JWT_SECRET_KEY` environment variable, the service silently starts with a **known, public secret**. Any attacker who reads the source code (e.g., via a public repository) can forge valid JWTs for any user.

**Risk:**  
- Complete authentication bypass if the env var is not set.
- No runtime warning or startup failure to alert operators.

**Remediation:**
1. **Raise a hard error** at startup if `JWT_SECRET_KEY` is absent or equals the default value.
2. Enforce a minimum secret length (≥ 32 bytes of entropy).

```python
import secrets as _secrets

def create_token_service(...) -> TokenService:
    resolved_secret = secret_key or os.environ.get("JWT_SECRET_KEY")
    if not resolved_secret:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if resolved_secret == _DEFAULT_SECRET:
        raise RuntimeError("JWT_SECRET_KEY must not be the default placeholder value.")
    if len(resolved_secret) < 32:
        raise ValueError("JWT_SECRET_KEY must be at least 32 characters long.")
    ...
```

---

### F-003 — Hardcoded Password Literals in Test Code

| Attribute | Detail |
|-----------|--------|
| **Tool** | Bandit B105 |
| **File** | `auth_models.py` |
| **Lines** | 352, 382, 398, 406 |
| **Severity** | LOW |
| **CWE** | [CWE-259](https://cwe.mitre.org/data/definitions/259.html) — Use of Hard-coded Password |
| **CVSS v3.1** | 0.0 — Test-only, no production exposure |

**Description:**  
Bandit flagged four occurrences of string literals that look like passwords (e.g., `"MyP@ssw0rd"`) inside the `if __name__ == "__main__"` self-test block of `auth_models.py`. These are test fixtures, not production credentials.

**Risk:**  
Negligible. These strings are used only to exercise the `PasswordHasher` and `UserInDB` APIs in a local smoke-test context. They are never stored, transmitted, or used as actual credentials.

**Remediation (Optional / Best Practice):**  
- Add a `# nosec B105` inline comment to suppress the Bandit warning and document the intent.
- Alternatively, move test data to a dedicated `test_auth_models.py` file where test-credential patterns are expected.

```python
test_password = "MyP@ssw0rd"  # nosec B105 — test fixture only
```

---

## 5. Positive Findings

The following security controls were verified and found to be **correctly implemented**:

| Control | Implementation | Assessment |
|---------|---------------|------------|
| **Password Hashing** | PBKDF2-HMAC-SHA256, 260,000 iterations, 256-bit random salt | ✅ Excellent — meets OWASP 2023 |
| **Constant-Time Comparison** | `hmac.compare_digest()` used in `PasswordHasher.verify()` | ✅ Timing-attack resistant |
| **Token Type Enforcement** | `type` claim (`access`/`refresh`) validated on every decode; `TokenTypeMismatchError` raised on mismatch | ✅ Prevents token-type confusion attacks |
| **JWT Expiry** | `exp` claim enforced; `ExpiredSignatureError` caught and re-raised as `TokenExpiredError` | ✅ Correct |
| **JWT Unique ID** | `jti` (UUID4) included in every token | ✅ Enables future revocation list support |
| **Password Policy** | Minimum 8 chars, requires uppercase, lowercase, digit, special char | ✅ Enforced at registration |
| **No Plain-text Password Storage** | `UserInDB` stores only `hashed_password`; `UserCreate.password` is never persisted | ✅ Correct separation |
| **UserPublic Schema** | `hashed_password` field absent from outbound schema | ✅ No credential leakage in API responses |
| **HTTP 401 / 403 Separation** | Unauthenticated → 401; authenticated but forbidden → 403 | ✅ Correct semantics |
| **Dependency CVEs** | pip-audit scan: 0 known CVEs | ✅ Clean |
| **Email Normalisation** | Emails lowercased and stripped before storage/lookup | ✅ Prevents duplicate-account attacks |
| **Username Case-Insensitive Lookup** | Usernames lowercased on store and lookup | ✅ Prevents enumeration via case variants |

---

## 6. Recommendations (Priority Order)

| Priority | Action |
|----------|--------|
| 🔴 **P1** | Enforce `JWT_SECRET_KEY` at startup — raise `RuntimeError` if missing or default |
| 🔴 **P1** | Change dev `__main__` bind from `0.0.0.0` → `127.0.0.1`; remove `reload=True` |
| 🟡 **P2** | Add minimum secret-length validation (≥ 32 chars) in `create_token_service()` |
| 🟡 **P2** | Implement a token revocation / blocklist mechanism (JTI-based) for logout and refresh invalidation |
| 🟢 **P3** | Add `# nosec B105` annotations to test password literals to suppress false-positive Bandit noise |
| 🟢 **P3** | Add rate-limiting middleware to `/login` and `/register` endpoints to mitigate brute-force attacks |
| 🟢 **P3** | Log authentication failures (failed login, invalid token) to a structured audit log |
| 🟢 **P3** | Consider adding `iss` (issuer) and `aud` (audience) claims to JWTs for multi-service deployments |

---

## 7. Conclusion

The Dalang-AI auth service is built on a solid security foundation. The cryptographic choices (PBKDF2-SHA256, HS256 JWT, constant-time comparison) are appropriate and correctly implemented. The two actionable findings (bind-all-interfaces and default JWT secret fallback) are configuration-level risks that are straightforward to remediate. Addressing the P1 items before production deployment will bring the overall grade to **A**.

---

*Report generated by Kai — Dalang-AI Application Security Specialist & Auditor*
