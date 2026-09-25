# =============================================================================
# Ripple10 Auth API — CIS Docker Benchmark v1.6 Hardened Dockerfile
# =============================================================================
# CIS Controls Applied:
#   4.1  — Explicit base image digest (no :latest, pinned sha256)
#   4.2  — Non-root user (UID 1001 / GID 1001) — USER directive before ENTRYPOINT
#   4.3  — Minimal attack surface (multi-stage, no build tools in runtime)
#   4.6  — HEALTHCHECK directive present
#   4.7  — Update instructions not alone (combined with install)
#   4.9  — COPY preferred over ADD
#   4.10 — Secrets not baked in (all config via ENV / runtime injection)
#   5.1  — No privileged mode (enforced in compose)
#   5.4  — Filesystem permissions locked down (--chown on COPY)
#
# Stage 1 : builder  — install Python deps into an isolated venv
# Stage 2 : runtime  — lean image, non-root, minimal layers
# =============================================================================

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
# CIS 4.1: Pin exact version + sha256 digest to prevent image substitution attacks
FROM python:3.11-slim-bookworm@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b AS builder

LABEL stage="builder"

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# CIS 4.7: Combine apt-get update + install in one RUN layer; pin package versions
# CIS 4.3: Install only strictly required build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc=4:12.2.0-3 \
        libffi-dev=3.4.4-1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# CIS 4.9: Use COPY (not ADD) — no URL fetching, no tar auto-extraction
COPY requirements.txt .

# Create an isolated venv and install all dependencies into it
# --no-cache-dir prevents pip from writing cache to the image layer
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip --no-cache-dir && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
# CIS 4.1: Pin exact version + sha256 digest
FROM python:3.11-slim-bookworm@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b AS runtime

# OCI Image Spec labels for supply-chain traceability (OpenSSF Best Practices)
LABEL org.opencontainers.image.title="Ripple10 Auth API" \
      org.opencontainers.image.description="JWT-based authentication service for Ripple10 platform" \
      org.opencontainers.image.vendor="Ripple10" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/ripple10/auth-api" \
      security.cis-benchmark="v1.6" \
      security.non-root="true"

# 12-Factor: All config via environment variables — no hardcoded values
# CIS 4.10: No secrets baked into image layers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # Make the venv the default Python environment
    PATH="/opt/venv/bin:$PATH" \
    # Application defaults (overridable via docker-compose / CI env injection)
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    APP_WORKERS=1 \
    APP_LOG_LEVEL=info

# CIS 4.3: No build tools in runtime image — copy only the pre-built venv
COPY --from=builder /opt/venv /opt/venv

# CIS 4.2: Create a dedicated non-root user and group with explicit numeric IDs
# --no-create-home: no home directory (reduces attack surface)
# --shell /sbin/nologin: prevents interactive login
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid 1001 --no-create-home --shell /sbin/nologin appuser

WORKDIR /app

# CIS 4.9 + 5.4: COPY with explicit ownership — files owned by appuser, not root
COPY --chown=1001:1001 auth_api.py      ./
COPY --chown=1001:1001 auth_models.py   ./
COPY --chown=1001:1001 token_service.py ./

# Copy the entrypoint script with restricted permissions (read+execute only)
COPY --chown=1001:1001 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod 0550 /usr/local/bin/docker-entrypoint.sh

# CIS 4.2: Drop privileges — switch to non-root user BEFORE EXPOSE and CMD
# Numeric UID:GID ensures portability across host systems (CIS DL3066 compliant)
USER 1001:1001

# 12-Factor Port Binding: document the port the app binds to
EXPOSE 8000

# CIS 4.6 / SRE Standard: Robust HEALTHCHECK using JSON exec form (no shell)
# --interval=30s   : check every 30 seconds
# --timeout=5s     : fail if no response within 5 seconds
# --start-period=10s: grace period for app startup before counting failures
# --retries=3      : mark unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", \
         "import urllib.request, sys; r = urllib.request.urlopen('http://localhost:8000/health', timeout=4); sys.exit(0 if r.status == 200 else 1)"]

# CIS DL3025: JSON exec form for ENTRYPOINT and CMD
# Exec form ensures SIGTERM is delivered directly to the process (graceful shutdown)
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["uvicorn", "auth_api:app", "--host", "0.0.0.0", "--port", "8000"]
