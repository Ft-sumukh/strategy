# AEGIS INVEST — Test Runner Script
Write-Host "Running Backend Pytest Suite..." -ForegroundColor Cyan
python -m pytest backend/tests -v
$backendStatus = $LASTEXITCODE

Write-Host "`nRunning Frontend Vitest & Typecheck..." -ForegroundColor Cyan
Set-Location frontend
npm test
$frontendTestStatus = $LASTEXITCODE
npm run typecheck
$frontendTypeStatus = $LASTEXITCODE
Set-Location ..

if ($backendStatus -eq 0 -and $frontendTestStatus -eq 0 -and $frontendTypeStatus -eq 0) {
    Write-Host "`n[SUCCESS] All AEGIS INVEST test suites passed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[FAILURE] One or more test suites failed." -ForegroundColor Red
    exit 1
}
