# AEGIS INVEST — Backend Server Script
Write-Host "Starting AEGIS INVEST FastAPI backend on http://localhost:8000..." -ForegroundColor Cyan
Set-Location backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
