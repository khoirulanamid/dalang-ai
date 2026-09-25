# Application Security Standards
**Reference:** OWASP ASVS v4.0 · OWASP Top 10 (2021) · NIST SP 800-63B · CVSS v3.1 Scoring · CWE/SANS Top 25

## 1. OWASP Application Security Verification Standard (ASVS) v4.0
Target: **ASVS Level 2** (most applications should meet this baseline).

### Authentication (V2)
- **V2.1.1** — Minimum password length 12 characters (not 8). *(Current: 8 — needs uplift)*
- **V2.1.7** — Passwords must be checked against known-breached password lists (HaveIBeenPwned API).
- **V2.1.9** — No password composition rules (no "must have uppercase/number") — research shows it's ineffective.
- **V2.2.1** — Anti-automation controls (rate limiting) MUST exist on `/login`. Max 5 attempts / 15 min before lockout.

### Session Management (V3)
- **V3.2.1** — Session tokens minimum 64 bits of entropy.
- **V3.3.1** — Logout must invalidate the session server-side (not just delete cookie client-side).
- **V3.5.1** — JWT must include `iss`, `aud`, `iat`, `exp`, `jti` claims.

### Cryptography (V6)
- **V6.2.2** — Only approved algorithms: `PBKDF2-SHA512` (not SHA256) at ≥ 120,000 iterations (OWASP 2024) or `Argon2id`.
- **V6.2.5** — Insecure hash functions (MD5, SHA1) must never be used for passwords.
- **V6.4.1** — Key management: Secret keys must be rotatable without downtime.

### Input Validation & Encoding (V5)
- **V5.1.3** — Input validation must use a whitelist (allowlist), not a denylist (blocklist).
- **V5.3.4** — All output to SQL/NoSQL must be parameterized.

## 2. OWASP Top 10 (2021) Checklist
| # | Risk | Status Wajib |
|---|------|------|
| A01 | Broken Access Control | Role-check middleware di semua protected route |
| A02 | Cryptographic Failures | Hashing standar PBKDF2/Argon2, HTTPS mandatory |
| A03 | Injection | Parameterized queries, input validation |
| A07 | Identification & Auth Failures | Rate limiting `/login`, token expiry, jti unique |
| A09 | Security Logging & Monitoring | Log semua auth failures dengan user agent + IP |

## 3. CVSS v3.1 Scoring Guide (untuk laporan temuan)
```
Score Range    Severity    Action Required
9.0 – 10.0     CRITICAL    Fix sebelum deploy, mandatory
7.0 – 8.9      HIGH        Fix dalam 24 jam
4.0 – 6.9      MEDIUM      Fix dalam sprint ini
0.1 – 3.9      LOW         Fix dalam 90 hari
0.0            NONE        Informational
```

## Anti-AI-Slop Code Hygiene (from antislop-code)
- **No Decorative Banners**: DILARANG `# =====`, `# -----`, `/* **** */` sebagai section separator.
- **No Obvious Comments**: DILARANG komentar yang restates the code (`# set timeout to 30` di atas `timeout = 30`).
- **No Emoji**: DILARANG emoji di komentar/docstring (`# 🚀`, `# ✅`, `# 💥`). Profesional saja.
- **Why, Not What**: Komentar hanya untuk menjelaskan keputusan non-obvious, bukan apa yang kode lakukan.

## 4. Mandatory Security Test Categories
Setiap rilis harus memiliki regression tests untuk:
- SQL/NoSQL injection attempts
- Authentication bypass (null token, malformed JWT, expired JWT)
- Token type confusion (access token dipakai sebagai refresh, vice versa)
- Timing attacks (pastikan response time constant untuk invalid password)
- Mass assignment (kirim field yang tidak seharusnya: `is_admin=true`)
