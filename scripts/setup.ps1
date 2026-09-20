# AEGIS INVEST — Setup Script
Write-Host "Setting up AEGIS INVEST development environment..." -ForegroundColor Cyan
pip install -r backend/requirements.txt
Set-Location frontend
npm install
Set-Location ..
Write-Host "Setup complete!" -ForegroundColor Green
