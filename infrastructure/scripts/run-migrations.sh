#!/usr/bin/env bash
# ==============================================================================
# AEGIS INVEST — Run Database Migrations (Bash / POSIX)
# ==============================================================================
set -euo pipefail

echo ">>> Running Alembic database migrations..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

export PYTHONPATH="${ROOT_DIR}/apps/api:${PYTHONPATH:-}"

cd "${ROOT_DIR}/apps/api"
python3 -m alembic upgrade head

echo "[OK] Database migrations completed successfully."
