# AEGIS INVEST — Database Migration Script
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("upgrade", "downgrade", "status", "revision")]
    [string]$Action,
    [string]$Message = "migration"
)

Set-Location backend
switch ($Action) {
    "upgrade" {
        Write-Host "Applying database migrations..." -ForegroundColor Cyan
        alembic upgrade head
    }
    "downgrade" {
        Write-Host "Reverting last migration..." -ForegroundColor Yellow
        alembic downgrade -1
    }
    "status" {
        Write-Host "Checking current migration state..." -ForegroundColor Cyan
        alembic current
    }
    "revision" {
        Write-Host "Creating new migration: $Message..." -ForegroundColor Cyan
        alembic revision --autogenerate -m "$Message"
    }
}
Set-Location ..
