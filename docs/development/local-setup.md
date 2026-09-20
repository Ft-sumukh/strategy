# AEGIS INVEST — Local Developer Setup Guide

This guide walks through setting up AEGIS INVEST locally for development, testing, and contributions.

---

## 1. Prerequisites

Ensure you have the following installed on your host machine:
* **Python:** 3.11, 3.12, 3.13, or 3.14
* **Node.js:** 20+ or 22 LTS
* **npm:** 10+ or 11+
* **Git:** 2.40+
* **Docker & Docker Compose:** Optional for native dev, required for containerized multi-service dev.

---

## 2. Quickstart (Native Local Development)

### Step 1: Clone and Configure Environment
```bash
# Clone the repository
git clone https://github.com/aegis-invest/aegis-invest.git
cd aegis-invest

# Copy environment configuration template
cp .env.example .env
```

### Step 2: Install Dependencies

**Backend:**
```bash
# Install Python dependencies
python -m pip install -r apps/api/requirements.txt
```

**Frontend:**
```bash
# Install Node workspace dependencies
npm install
```

### Step 3: Run Database Migrations
By default, the local `.env` uses SQLite (`sqlite+aiosqlite:///./aegis_local.db`) for zero-dependency local development:
```bash
cd apps/api
python -m alembic upgrade head
cd ../..
```

### Step 4: Start Development Servers

**Terminal 1 (Backend API):**
```bash
cd apps/api
python -m uvicorn app.main:app --reload --port 8000
```
API will be live at: `http://localhost:8000`  
Swagger UI Docs: `http://localhost:8000/docs`

**Terminal 2 (Frontend Web):**
```bash
npm run dev:web
```
Web application will be live at: `http://localhost:3000`

---

## 3. Containerized Development (Docker Compose)

To run the complete stack including PostgreSQL 16 and Redis 7 in Docker:

```bash
# Start all containers in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api

# Stop all containers
docker compose down
```

---

## 4. Running Verification & Tests

### Backend & Integration Tests
```bash
# Run all tests (18 tests)
python -m pytest

# Run with verbose output
python -m pytest -v
```

### Frontend Type Checking & Tests
```bash
# Run TypeScript type check
npm run typecheck:web

# Run Vitest unit tests
npm run test:web

# Run production build
npm run build:web
```

---

## 5. Database Migration Commands

Alembic manages database revisions in `apps/api/alembic/versions/`:

```bash
cd apps/api

# Apply all pending migrations
python -m alembic upgrade head

# Rollback one migration
python -m alembic downgrade -1

# Create a new migration revision
python -m alembic revision -m "add_new_table"
```
