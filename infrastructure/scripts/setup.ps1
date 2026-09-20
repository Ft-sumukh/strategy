# ==============================================================================
# AEGIS INVEST — Local Environment Setup Script (PowerShell)
# ==============================================================================

Write-Host ">>> AEGIS INVEST: Bootstrapping Local Development Environment..." -ForegroundColor Cyan

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVersion = python --version
    Write-Host "[OK] Python: $pyVersion" -ForegroundColor Green
} else {
    Write-Error "[FAIL] Python is not installed or not on PATH."
    exit 1
}

# Check Node.js
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Error "[FAIL] Node.js is not installed or not on PATH."
    exit 1
}

# Check npm
if (Get-Command npm -ErrorAction SilentlyContinue) {
    $npmVersion = npm --version
    Write-Host "[OK] npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Error "[FAIL] npm is not installed or not on PATH."
    exit 1
}

# Copy .env.example to .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host ">>> Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Created .env" -ForegroundColor Green
} else {
    Write-Host "[OK] .env already exists" -ForegroundColor Green
}

# Install Backend Python dependencies
Write-Host ">>> Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install -r apps/api/requirements.txt

# Install Frontend Node dependencies
Write-Host ">>> Installing Frontend dependencies..." -ForegroundColor Cyan
npm install --workspace=apps/web

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AEGIS INVEST environment setup complete." -ForegroundColor Green
Write-Host "To start the backend:" -ForegroundColor Yellow
Write-Host "  cd apps/api; python -m uvicorn app.main:app --reload --port 8000"
Write-Host "To start the frontend:" -ForegroundColor Yellow
Write-Host "  npm run dev:web"
Write-Host "============================================================" -ForegroundColor Cyan
