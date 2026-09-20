# ==============================================================================
# AEGIS INVEST — Run Database Migrations (PowerShell)
# ==============================================================================

Write-Host ">>> Running Alembic database migrations..." -ForegroundColor Cyan

$env:PYTHONPATH = "d:\strategy\apps\api;$env:PYTHONPATH"
Set-Location "d:\strategy\apps\api"

try {
    python -m alembic upgrade head
    Write-Host "[OK] Database migrations completed successfully." -ForegroundColor Green
} catch {
    Write-Error "[FAIL] Migration failed: $_"
    exit 1
} finally {
    Set-Location "d:\strategy"
}
