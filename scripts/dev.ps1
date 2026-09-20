# AEGIS INVEST — Development Runner Script
Write-Host "Launching AEGIS INVEST full-stack development environment..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location backend; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev"
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Docs:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
