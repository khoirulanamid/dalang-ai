#!/usr/bin/env sh
# =============================================================================
# docker-entrypoint.sh — Ripple10 Auth API container entrypoint
# =============================================================================
set -e

# Default port and host if not provided
HOST="${APP_HOST:-0.0.0.0}"
PORT="${APP_PORT:-8000}"
WORKERS="${APP_WORKERS:-1}"
LOG_LEVEL="${APP_LOG_LEVEL:-info}"

# If CMD starts with "uvicorn" and no extra args or default uvicorn cmd
if [ "$1" = "uvicorn" ] && [ "$#" -eq 1 ]; then
    exec uvicorn auth_api:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS" \
        --log-level "$LOG_LEVEL"
fi

# If the first argument looks like a flag or options to uvicorn
if [ "${1#-}" != "$1" ]; then
    exec uvicorn auth_api:app "$@"
fi

# Otherwise execute the passed command directly (e.g. bash, pytest, etc.)
exec "$@"
