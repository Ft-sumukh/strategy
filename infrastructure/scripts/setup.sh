#!/usr/bin/env bash
# ==============================================================================
# AEGIS INVEST — Local Environment Setup Script (Bash / POSIX)
# ==============================================================================
set -euo pipefail

echo ">>> AEGIS INVEST: Bootstrapping Local Development Environment..."

command -v python3 >/dev/null 2>&1 || { echo "[FAIL] python3 required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "[FAIL] node required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "[FAIL] npm required"; exit 1; }

echo "[OK] Python: $(python3 --version)"
echo "[OK] Node.js: $(node --version)"
echo "[OK] npm: $(npm --version)"

if [ ! -f ".env" ]; then
    echo ">>> Creating .env from .env.example..."
    cp .env.example .env
    echo "[OK] Created .env"
fi

echo ">>> Installing Python dependencies..."
pip install -r apps/api/requirements.txt

echo ">>> Installing Frontend dependencies..."
npm install --workspace=apps/web

echo "============================================================"
echo "AEGIS INVEST environment setup complete."
echo "To start the backend:"
echo "  cd apps/api && python3 -m uvicorn app.main:app --reload --port 8000"
echo "To start the frontend:"
echo "  npm run dev:web"
echo "============================================================"
