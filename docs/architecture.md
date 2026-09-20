# AEGIS INVEST — System Architecture

## 1. Modular Monolith Topology

Aegis Invest employs a domain-partitioned modular monolith architecture. This balances rapid development velocity with clean decoupling, ensuring modules can evolve independently or transition into distributed services if throughput demands require it in the future.

```text
                             AEGIS INVEST
                                  │
                  ┌───────────────┴───────────────┐
                  ↓                               ↓
              FRONTEND                         BACKEND
                  │                               │
            Next.js (App)                   FastAPI (Async)
                  │                               │
                  │            ┌──────────────────┼──────────────────┐
                  │            ↓                  ↓                  ↓
                  │        DATA LAYER        QUANT ENGINE        AI ENGINE
                  │            │                  │                  │
                  │            └──────────────────┼──────────────────┘
                  │                               ↓
                  │                          RISK ENGINE
                  │                               ↓
                  │                         DECISION LAYER
                  │                               │
                  └──────────── REST API ─────────┘
                                  │
                                  ↓
                        PostgreSQL (Relational)
```

## 2. Layer Responsibilities

### 2.1 Backend (`backend/app/`)
- **API Aggregator (`api/v1/`)**: Versioned routing, parameter validation, rate limiting, and standardized envelope serialization.
- **Core Infrastructure (`core/`)**: Structured JSON logging, secret scrubbing, domain exception hierarchy, and CORS controls.
- **Database Engine (`database/`)**: Async SQLAlchemy 2.0 sessions, connection pool configuration, UTC timestamp mixins, and Alembic migrations.
- **Data Layer (`data/`)**: Multi-vendor provider abstraction, OHLCV normalization, corporate action split/dividend adjustments, and data quality verification.
- **Analytics Engine (`analytics/`)**: Mathematical factor libraries, technical indicators, and econometric models.
- **Risk Engine (`risk/`)**: Historical, parametric, and Monte Carlo Value-at-Risk (VaR), Conditional VaR, and scenario shock generators.
- **Portfolio Layer (`portfolio/`)**: Position tracking, mean-variance and Black-Litterman optimization, and risk budgeting.
- **Strategies & Backtesting (`strategies/`, `backtesting/`)**: Rule definitions, signal generators, event-driven backtesting, slippage, and transaction cost modeling.
- **AI & Research (`ai/`, `research/`)**: Context retrieval, multi-source evidence synthesis, and analyst research note management.

### 2.2 Frontend (`frontend/`)
- **App Router (`app/`)**: File-system based routing for all 18 analytical views.
- **Component System (`components/`)**: Dark-first financial theme, Inter typography, monospace metrics, accessible status badges, and structured empty states.
- **API Client Layer (`lib/api/`)**: Strongly typed HTTP wrapper with abort controllers, retry mechanisms, and error envelope unpacking.
