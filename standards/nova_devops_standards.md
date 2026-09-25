# DevOps & Infrastructure Standards
**Reference:** CIS Docker Benchmark v1.6 · Google SRE Handbook · 12-Factor App · DORA Metrics · OpenSSF Best Practices

## 1. Container Security (CIS Docker Benchmark)
- **Non-Root Execution**: Container process **wajib** jalan sebagai unprivileged user (e.g. `USER appuser:1001`). Jangan pernah run sebagai `root`.
- **Multi-Stage Builds**: Pisahkan build stage (yang butuh compiler/uv) dengan runtime stage (hanya runtime dependencies dan binary). Image size harus minimal (< 150MB untuk Python).
- **Read-Only Root Filesystem**: Gunakan `read_only: true` di Docker Compose dengan `tmpfs` mounts untuk `/tmp`.
- **Drop Capabilities**: Di docker-compose / Kubernetes, drop all capabilities kecuali yang strictly dibutuhkan: `cap_drop: [ALL]`.
- **Explicit Base Image Tags**: Jangan pernah gunakan `:latest`. Selalu pin versi spesifik: `python:3.11-slim-bookworm` atau sha256 hash.

## 2. Health Checks & Observability (SRE Standard)
- **HEALTHCHECK Directive**: Setiap Dockerfile wajib memiliki:
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
  ```
- **Liveness vs Readiness**: `/health` menguji bahwa process hidup; `/ready` menguji bahwa koneksi ke dependency (database, cache) siap menerima request.
- **Graceful Shutdown**: Container harus merespons sinyal `SIGTERM` dan menyelesaikan inflight requests dalam timeout (default 30s) sebelum `SIGKILL`.

## 3. CI/CD Standards (DORA High-Performer)
- **Fast Feedback Loop**: Pipeline lint + test harus selesai dalam < 3 menit.
- **Fail-Fast Gates**:
  1. Gate 1: Static Analysis & Lint (Ruff, Flake8)
  2. Gate 2: Security SAST (Bandit)
  3. Gate 3: Unit & Integration Tests (pytest)
  4. Gate 4: Container Build & Vulnerability Scan (Trivy)
- **Secrets Management**: Jangan pernah commit secrets. Semua secrets diinjeksi via CI/CD Secret Store (GitHub Secrets).

## Anti-AI-Slop Code Hygiene (from antislop-code)
- **No Decorative Banners**: DILARANG `# =====`, `# -----`, `/* **** */` sebagai section separator.
- **No Obvious Comments**: DILARANG komentar yang restates the code (`# set timeout to 30` di atas `timeout = 30`).
- **No Emoji**: DILARANG emoji di komentar/docstring (`# 🚀`, `# ✅`, `# 💥`). Profesional saja.
- **Why, Not What**: Komentar hanya untuk menjelaskan keputusan non-obvious, bukan apa yang kode lakukan.

## 4. 12-Factor Configuration
- Storing config in the environment: Tidak boleh ada `.env` file di repository git. Gunakan `.env.example` sebagai kontrak terdokumentasi.
- Port Binding: Aplikasi harus completely self-contained dan bind langsung ke port yang disediakan environment variable `$PORT`.
