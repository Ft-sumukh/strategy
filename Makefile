# ==============================================================================
# AEGIS INVEST — Development Makefile
# ==============================================================================

.PHONY: help setup dev backend frontend test test-backend test-frontend db-migrate db-upgrade db-downgrade clean

help:
	@echo "AEGIS INVEST Development Commands"
	@echo "=================================="
	@echo "make setup        - Install backend & frontend dependencies"
	@echo "make dev          - Start backend and frontend development servers"
	@echo "make backend      - Start FastAPI backend server on :8000"
	@echo "make frontend     - Start Next.js frontend on :3000"
	@echo "make test         - Run backend and frontend test suites"
	@echo "make db-migrate   - Generate a new Alembic migration"
	@echo "make db-upgrade   - Apply Alembic migrations to database"
	@echo "make db-downgrade - Revert last Alembic migration"

setup:
	pip install -r backend/requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd backend; uvicorn app.main:app --reload --port 8000'; cd frontend; npm run dev"

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	python -m pytest backend/tests -v

test-frontend:
	cd frontend && npm test && npm run typecheck

db-migrate:
	cd backend && alembic revision --autogenerate -m "auto_migration"

db-upgrade:
	cd backend && alembic upgrade head

db-downgrade:
	cd backend && alembic downgrade -1

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
