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

## 5. Reverse Engineering & Security Audit Routing Methodology (from reverse-skill)
Reference: `zhaoxuya520/reverse-skill` AI Security Skill Routing Architecture

### A. Scenario-Based Tool & Analysis Routing Matrix
Saat mengaudit atau menganalisis artefak keamanan, ikuti alur metodologis terstruktur (jangan menebak):
1. **APK / Android Mobile Audit**:
   - *Static Analysis*: Decompile bytecode via `jadx` / `apktool` untuk mengaudit manifest, exported components (`activity`, `service`, `receiver`, `provider`), hardcoded keys/secrets, dan network security config.
   - *Dynamic Instrumentation*: Evaluasi implementasi anti-tampering, integrity check, root detection, dan dynamic certificate pinning.
2. **Frontend JS & Client Cryptography Audit**:
   - *Deobfuscation*: Membedah parameter terenkripsi di client-side (AES, RSA, custom XOR, WebAssembly).
   - *Tamper Resistance*: Pastikan token atau signature client tidak dapat dimanipulasi atau di-replay ke server backend.
3. **Binary & ELF/SO Security Assessment**:
   - *Disassembly & Decompilation*: Analisis pola memory safety, RPATH insecure linking, buffer boundaries, stack protection (`canary`), ASLR, dan PIE flags.
   - *String & Symbol Audit*: Deteksi hardcoded credentials, sensitive debugging endpoints, dan unsafe C library calls.
4. **API, GraphQL & Token Gating Audit**:
   - *Token Integrity*: Uji JWT algorithm confusion (`none` alg, asymmetric-to-symmetric key confusion), lack of signature verification, token expiration enforcement.
   - *Access Control*: Uji Broken Object Level Authorization (BOLA/IDOR), Broken Function Level Authorization (BFLA), dan mass assignment.

### B. Evidence-Based Audit Lifecycle (Evidence → Finding → Remediation)
Semua audit harus mematuhi alur ketat:
- **Scope Gate**: Tentukan batasan target audit (URL, commit, binary, codebase path). Dilarang melakukan audit tanpa verifikasi scope.
- **Evidence Collection**: Catat request/response raw, stack trace, atau baris kode rentan yang dapat direproduksi 100%.
- **Finding Classification**: Klasifikasikan temuan dengan CVSS v3.1 score dan nomor CWE (Common Weakness Enumeration).
- **Remediation Path**: Berikan instruksi perbaikan konkret dan actionable untuk developer (Zaki/Lulu/Nova).
- **Zero Hallucination Policy**: Jangan pernah melaporkan kerentanan tanpa bukti konkret (reproducible PoC).

### C. Software Supply Chain & Dependency Integrity (SBOM)
- **Pinning & Fixity**: Pastikan setiap package dependency di-pin versi eksplisit dengan hash checksum (`pip-audit`, `npm audit`).
- **Transitive Risk Mapping**: Periksa dependensi turunan yang memiliki N-day CVE yang diketahui publik.

### D. LLM Application & Agentic AI Security (OWASP LLM Top 10 & ASI 2026)
- **LLM01 / ASI01 — Prompt Injection Defense**:
  - Validasi seluruh input konteks dari file eksternal/workspace menggunakan filter netralisasi (`LLMGuardrail`).
  - Cegah *Indirect Prompt Injection* yang disisipkan penyerang ke dalam file teks/kode agar tidak mengubah instruksi orkestrator (Risko).
- **LLM02 — Sensitive Information Disclosure**:
  - Awasi output model LLM agar tidak membocorkan system prompt rahasia, environment variables, atau API keys (`sk-...`, `ghp_...`).
- **LLM06 / ASI02 — Excessive Agency & Tool Abuse**:
  - Batasi wewenang eksekusi tools: blokir pemanggilan shell exfiltration (`curl`, `wget`, `nc`, reverse shell) dari input model yang tidak terotorisasi.
  - Terapkan *Human-in-the-Loop* (Persetujuan Bos Muda) untuk aksi destruktif atau mutasi permanen di luar workspace.

### E. Cloudflare-Grade Multi-Phase Audit & Coverage Ledger (from cloudflare/security-audit-skill)
- **Phase 1: Coverage Ledger Mapping**:
  - Petakan seluruh unit kode dan attack surfaces (API, DB, UI, CLI) ke dalam `CoverageUnit` sebelum mulai berburu. Tidak boleh ada area yang tidak tercatat.
- **Phase 2: Hunter Candidate Handoff**:
  - Sebagai Hunter, Kai mengajukan temuan sebagai *Candidate Finding* (bukan langsung vonis final).
  - Setiap kandidat wajib menyertakan jejak kode sumber konkret dan command reproduksi.
  - Serahkan kandidat ke Ren (Adversarial Verifier) untuk diuji sangkal. Dilarang menetapkan status *confirmed* sendirian tanpa lolos uji sangkal lawan.




---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-01 23:08 UTC)
## 🏢 MANIFESTO KANTOR BOS MUDA (MULTI-DISCIPLINARY STUDIO)
Tim Dalang-AI beroperasi sebagai kantor profesional multi-domain:
1. Bidang Kerja Fleksibel: Frontend, Backend, Desain Grafis, Animasi/Video, Microstock, Dokumentasi, Security, QA.
2. Siap Adaptif: Terbuka untuk penambahan spesialis baru seiring perkembangan bisnis.
3. Standar Kolaborasi: Wajib Pre-flight Consultation, Handover Gate, dan Musyawarah Tim — tidak ada yang kerja soliter tanpa konsul.
4. Kualitas Kantor: Semua hasil kerja harus siap pakai untuk kebutuhan profesional Bos Muda.


---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-02 09:16 UTC)
### Standar Keamanan Otomasi Media Sosial (Threads & Meta Affiliate)
1. **Zero Secret Leakage**: Session cookies (Instagram/Threads via Meta SSO) HARUS disimpan di folder aman di luar repository (misal ) dengan permission 600. DILARANG commit session cookies, post history, atau affiliate database ke git.
2. **Rate Limiting & Account Protection**: Maksimal 3-5 post per hari untuk mencegah spam shadowban atau account lock dari sistem deteksi AI Meta.
3. **URL Validation & Link Hygiene**: Link affiliate WAJIB divalidasi protokol (https://) dan domain resmi (s.shopee.co.id, dll.) untuk mencegah open-redirect atau injection.


---

### 🎓 Pelajaran Baru — Diajarkan oleh Bos Muda (2026-10-02 09:17 UTC)
### Standar Keamanan Otomasi Media Sosial (Threads & Meta Affiliate)
1. **Zero Secret Leakage**: Session cookies (Instagram/Threads via Meta SSO) HARUS disimpan di folder aman di luar repository (misal ~/.threads_poster/cookies/session.json) dengan permission 600. DILARANG commit session cookies, post history, atau affiliate database ke git.
2. **Rate Limiting & Account Protection**: Maksimal 3-5 post per hari untuk mencegah spam shadowban atau account lock dari sistem deteksi AI Meta.
3. **URL Validation & Link Hygiene**: Link affiliate WAJIB divalidasi protokol (https://) dan domain resmi (s.shopee.co.id, dll.) untuk mencegah open-redirect atau injection.
