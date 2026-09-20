# AEGIS INVEST — Development Guide

## 1. Prerequisites

- Python 3.12+ (tested on Python 3.14)
- Node.js 18+ & npm
- PostgreSQL 16+ (or local SQLite fallback for testing)
- Docker & Docker Compose (optional for containerized setup)

## 2. Local Setup

### 2.1 Backend Setup
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Copy environment variables
cp .env.example .env

# 3. Apply database migrations
cd backend && alembic upgrade head

# 4. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### 2.2 Frontend Setup
```bash
# 1. Install npm dependencies
cd frontend && npm install

# 2. Start Next.js development server
npm run dev
```
Web application will be live at `http://localhost:3000`.

## 3. Development Commands

### PowerShell
```powershell
./scripts/setup.ps1      # Install dependencies
./scripts/dev.ps1        # Launch full-stack environment
./scripts/test.ps1       # Run all backend and frontend test suites
./scripts/db.ps1 upgrade # Run Alembic migrations
```

### Make (Linux / macOS)
```bash
make setup               # Install dependencies
make dev                 # Concurrently start backend & frontend
make test                # Run test suites
make db-upgrade          # Run database migrations
```

## 4. Code Quality & Standards

- **Backend**: Strict PEP 8, Pydantic v2 schemas for all inputs/outputs, type annotations on all function signatures.
- **Frontend**: TypeScript strict mode (`tsc --noEmit`), Tailwind CSS semantic design tokens, zero `any` types in production components.
