# AEGIS INVEST

> **An AI-assisted, risk-aware investment decision-intelligence platform that combines financial data, fundamental analysis, technical analysis, quantitative strategies, market regimes, news/current affairs, risk analysis, portfolio optimization, backtesting, and explainable decision support.**

```text
DATA → ANALYSIS → RISK → EVIDENCE → DECISION INTELLIGENCE
```

---

## 1. Product Context & Phase Status

**Current Stage: Part 1 — Foundation, Architecture & Application Shell**

AEGIS INVEST is **not** a simplistic "AI stock predictor" and is **never** designed around guaranteed profits, guaranteed minimum losses, or deterministic price predictions. It is an institutional-grade, risk-aware financial decision-intelligence platform engineered for research, quantitative modeling, portfolio risk oversight, and systematic decision support.

### Part 1 Accomplishments:
* **Canonical Repository Structure:** Strict modular monolith layout (`backend/`, `frontend/`, `data/`, `scripts/`, `docs/`).
* **FastAPI Backend Core:** Layered architecture (`api/v1` $\rightarrow$ `core` $\rightarrow$ `services` $\rightarrow$ `database` $\rightarrow$ `models`).
* **API Versioning & Standard Error Envelope:** All endpoints structured under `/api/v1/` with consistent JSON error envelopes and request ID tracing.
* **Health & Readiness Probes:**
  * `GET /api/v1/health` (Liveness: `{"status": "healthy", "service": "aegis-invest", "version": "0.1.0"}`)
  * `GET /api/v1/health/readiness` (Readiness: evaluating PostgreSQL and downstream dependencies)
  * `GET /api/v1/system/info` (Runtime telemetry & operational metadata)
* **Architectural Module Boundaries:** Cleanly scaffolded packages for all planned future domains (`data`, `analytics`, `risk`, `portfolio`, `strategies`, `backtesting`, `ai`, `research`, `utils`).
* **Database & Migrations Foundation:** SQLAlchemy 2.0 async engine with Alembic migrations, UTC timestamp mixins, UUID primary keys, and financial decimal precision constants.
* **Next.js 14 App Router Shell:**
  * Dark-first institutional financial theme (Inter typography, monospace numbers/tickers).
  * Collapsible `Sidebar` with all 18 planned route items.
  * `Topbar` with global search modal, market status indicator, notification popover, and researcher persona profile.
  * Flagship `/dashboard` implementing the 4-row layout with high-quality, structured empty states and zero fake numbers.
  * Route shells for all 18 planned views (`/dashboard`, `/markets`, `/screener`, `/stocks`, `/research`, `/news`, `/macro`, `/strategies`, `/backtesting`, `/risk`, `/stress-test`, `/portfolio`, `/watchlist`, `/alerts`, `/ai-research`, `/experiments`, `/models`, `/settings`).
* **Reusable Component System:** `AppShell`, `Sidebar`, `Topbar`, `PageHeader`, `Card`, `MetricCard`, `StatusBadge`, `EmptyState`, `LoadingState`, `ErrorState`, `DataTable`, `SearchInput`, `FilterBar`, `Tabs`, `Tooltip`, `Modal`, `GlobalSearchModal`.
* **Typed API Client:** `ApiClient` supporting `GET`, `POST`, `PUT`, `PATCH`, `DELETE` with abort timeouts and typed error unpacking.
* **Financial Safety Guarantees:** Global regulatory disclaimer component and zero hallucinated metrics policy.
* **Automated Verification:** 18 backend unit & integration tests and frontend Vitest & TypeScript verification passing with 100% success rate.

---

## 2. Repository Structure

```text
aegis-invest/
├── backend/                  # FastAPI Application (Python 3.12 / 3.14)
│   ├── app/
│   │   ├── main.py           # Application entry point & middleware registration
│   │   ├── config.py         # Strongly typed settings (Pydantic v2)
│   │   ├── api/v1/           # Router aggregator & health endpoints
│   │   ├── core/             # Structured logging, exceptions & security
│   │   ├── database/         # SQLAlchemy session, base mixins & migrations
│   │   ├── models/           # Persistent domain entities (SystemAudit)
│   │   ├── schemas/          # Pydantic validation contracts
│   │   ├── services/         # Health & market provider abstraction
│   │   ├── data/             # Architectural boundary: Market & company data
│   │   ├── analytics/        # Architectural boundary: Technical & factor models
│   │   ├── risk/             # Architectural boundary: VaR & stress testing
│   │   ├── portfolio/        # Architectural boundary: Construction & optimization
│   │   ├── strategies/       # Architectural boundary: Systematic alphas
│   │   ├── backtesting/      # Architectural boundary: Event simulation
│   │   ├── ai/               # Architectural boundary: LLM reasoning
│   │   ├── research/         # Architectural boundary: Investment research
│   │   └── utils/            # Common mathematical & format utilities
│   └── tests/
│       ├── unit/             # Unit tests (config, errors, providers)
│       └── integration/      # Integration tests (health, readiness, DB)
├── frontend/                 # Next.js 14 Application (TypeScript / React 18 / Tailwind)
│   ├── app/                  # App Router views (all 18 planned routes)
│   ├── components/
│   │   ├── layout/           # AppShell
│   │   ├── navigation/       # Sidebar & Topbar
│   │   ├── ui/               # Reusable UI component library
│   │   ├── common/           # GlobalSearchModal
│   │   └── disclaimer/       # Institutional compliance disclaimers
│   ├── lib/
│   │   ├── api/              # Typed ApiClient & error envelopes
│   │   ├── types/            # Financial domain type contracts
│   │   └── utils/            # Styling & formatting utilities
│   └── tests/                # Vitest test suites
├── data/                     # Data Storage Layers
│   ├── raw/                  # Immutable provider feeds
│   ├── processed/            # Cleaned, split-adjusted data
│   ├── historical/           # Point-in-time backtesting archives
│   └── demo/                 # Deterministic offline demonstration data
├── scripts/                  # Development automation scripts (PowerShell & Make)
├── docs/                     # Institutional documentation suite
│   ├── product.md            # Product specification & philosophy
│   ├── architecture.md       # Modular monolith architecture
│   ├── development.md        # Local setup & developer workflow
│   ├── security.md           # Zero-trust security & RBAC
│   ├── data.md               # Financial data strategy & integrity
│   └── roadmap.md            # 12-phase engineering roadmap
├── docker-compose.yml        # Multi-container orchestration (API, Web, Postgres, Redis)
├── Makefile                  # Unix make targets
├── .env.example              # Environment variables template
└── LICENSE                   # Apache 2.0 License
```

---

## 3. Local Development Quickstart

### Prerequisites
* Python 3.12+ (Python 3.14 verified)
* Node.js 18+ & npm 10+
* Git

### Step 1: Clone and Configure Environment
```bash
cp .env.example .env
```

### Step 2: Run Setup & Migrations
```powershell
# Using PowerShell
./scripts/setup.ps1
./scripts/db.ps1 upgrade

# Or using Make
make setup
make db-upgrade
```

### Step 3: Run Development Servers
```powershell
# Launch backend (:8000) and frontend (:3000) concurrently
./scripts/dev.ps1

# Or run individually:
./scripts/backend.ps1   # FastAPI backend
./scripts/frontend.ps1  # Next.js frontend
```

Endpoints:
* Web Application: `http://localhost:3000`
* API Server: `http://localhost:8000`
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`
* ReDoc UI: `http://localhost:8000/redoc`

---

## 4. Running Verification Tests

```powershell
# Run all test suites
./scripts/test.ps1

# Backend unit & integration tests (18 tests)
python -m pytest backend/tests -v

# Frontend Vitest suite & TypeScript validation
cd frontend
npm test
npm run typecheck
```

---

---

## 5. LLM AI Reasoning Layer & Qwen Integration

AEGIS INVEST features a modular, provider-agnostic AI reasoning architecture where external LLMs sit **strictly on top of deterministic financial and risk engines**.

```text
                    AEGIS AI LAYER
                          │
                          ▼
                 LLM Provider Router
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
      INTERNAL          QWEN            Future
    DETERMINISTIC       PROVIDER       PROVIDERS
          │               │
          │               ▼
          │          Qwen API
          │
          ▼
    Financial/Risk Results
                          │
                          ▼
                 AEGIS Intelligence
```

### Provider Options

#### 1. Internal Deterministic Engine (Default)
Zero external API key or token cost required. Uses deterministic financial synthesis and structured evidence citations.
```env
LLM_PROVIDER=AEGIS_INTERNAL_DETERMINISTIC
LLM_MODEL=aegis-institutional-v1
```

#### 2. Qwen LLM Provider
Integrates Alibaba Cloud DashScope / OpenAI-compatible Qwen endpoints (e.g. `qwen3-32b`, `qwen3-8b`, `qwen3-14b`, `qwen-plus`, `qwen-max`):
```env
LLM_PROVIDER=QWEN
LLM_MODEL=qwen3-32b
QWEN_API_KEY=your_dashscope_or_qwen_api_key
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

### Changing Models Dynamically
You can change the active model in `.env` (e.g., `LLM_MODEL=qwen3-8b` or `LLM_MODEL=qwen-plus`) without modifying any application code.

### Safe Status Endpoint
Check active provider status without leaking credentials:
```bash
GET http://localhost:8000/api/v1/ai/status
# Returns: {"llm_provider": "QWEN", "llm_model": "qwen3-32b", "status": "configured"}
```

### Financial Safety & Epistemic Boundaries
* **Deterministic Calculations**: Ratios, Sharpe, VaR, CVaR, DCF intrinsic value, factor metrics, and technical indicators are computed exclusively in deterministic Python engines.
* **Structured Context**: Qwen receives structured JSON context from the quantitative engines and produces natural-language syntheses, risk factor explanations, and thesis summaries.
* **Anti-Hallucination & Epistemic Bounds**: Guardrails sanitize prompt injections and eliminate speculative certainty claims.

---

## 6. Financial-System Safety Principle

> **AEGIS must never fabricate market data, financial metrics, historical returns, backtest results, model performance, news, or sources.**

* If data is unavailable or not yet implemented, it remains explicitly `unknown`.
* The frontend contains zero fake dashboard metrics ("Portfolio Risk: 72" or "AI Confidence: 94%").
* Clear architectural separation exists between **Historical Observation**, **Model Output**, **Backtest Result**, **Hypothetical Scenario**, and **User Assumption**.

---

## 7. License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
