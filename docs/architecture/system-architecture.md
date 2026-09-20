# AEGIS INVEST — System Architecture & Engineering Blueprint

## 1. Architectural Vision & Mission
**AEGIS INVEST** is a production-oriented, AI-assisted, risk-aware financial investment decision-intelligence platform. It provides transparent, reproducible, and mathematically rigorous analytics across fundamentals, technical indicators, quantitative factor strategies, market regimes, macro indicators, tail-risk modeling, and portfolio optimization.

AEGIS strictly repudiates simplistic "AI stock predictor" designs that make claims of guaranteed profits or minimum losses. Instead, AEGIS is designed as an institutional-grade decision-support platform emphasizing research integrity, evidence-based reasoning, and full auditability.

---

## 2. System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT / PRESENTATION                         │
│                                                                         │
│   Next.js 14 Frontend Application (App Router, Strict TypeScript)       │
│   ├── Centralized API Client (lib/api/client.ts)                        │
│   ├── UI Components (Card, Badge, Button, Alert, Skeleton, ErrorState)  │
│   ├── System Health & Architecture Maps                                 │
│   └── Regulatory Disclaimer Architecture & Banners                      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │  HTTPS / JSON
                                     │  X-Request-ID Header
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                               API LAYER                                 │
│                                                                         │
│   FastAPI Application (/api/v1/)                                        │
│   ├── RequestIDMiddleware (Extracts/Generates UUIDv4 Tracing Header)    │
│   ├── SecurityHeadersMiddleware (nosniff, DENY, strict referrer, CSP)   │
│   ├── CORSMiddleware (Configurable origins)                             │
│   ├── LoggingMiddleware (Latency timing, structured access logs)        │
│   ├── MetricsMiddleware (Request volume, status code instrumentation)   │
│   └── Global Exception Handlers (Standardized JSON Error Envelope)      │
│                                                                         │
│   Versioned Endpoints:                                                  │
│   ├── GET /api/v1/health       (Process Liveness Probe)                 │
│   ├── GET /api/v1/readiness    (PostgreSQL & Redis Readiness Probe)     │
│   └── GET /api/v1/system/info  (Operational Telemetry & Versioning)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION & SERVICE LAYER                      │
│                                                                         │
│   Domain Services & Abstractions                                        │
│   ├── HealthService (Orchestrates dependency health assessments)       │
│   ├── MarketDataProvider (Abstract Interface for multi-vendor adapters) │
│   └── Future Service Slots (Strategies, Risk, Backtesting, ML)          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             REPOSITORY LAYER                            │
│                                                                         │
│   Data Access Abstractions                                              │
│   ├── BaseRepository[ModelType] (Generic async CRUD operations)         │
│   └── SystemAuditRepository (System events, readiness audit logs)       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PERSISTENCE & INFRASTRUCTURE                     │
│                                                                         │
│   Database Engine & Migrations                                          │
│   ├── SQLAlchemy 2.0 Declarative Models (AsyncEngine, AsyncSessionLocal)│
│   ├── Alembic Migration System (Controlled schema versioning)          │
│   ├── PostgreSQL 16 (Primary relational datastore)                      │
│   └── Redis 7 (Caching & asynchronous job broker)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layered Separation of Concerns

The architecture strictly enforces five non-overlapping layers:

1. **Presentation Layer (`apps/web`):**
   * Built with Next.js 14, React 18, and Tailwind CSS.
   * Interacts with the backend exclusively via the centralized `ApiClient` (`apps/web/lib/api/client.ts`).
   * No hardcoded raw `fetch` calls, no direct database knowledge.
   * Strictly renders actual data or honest "Not implemented in Group 1: reserved for future research module" placeholders. No fake metrics!

2. **HTTP / API Layer (`apps/api/app/api` & `app/middleware`):**
   * Routing, HTTP protocol handling, parameter validation via Pydantic schemas.
   * Middleware intercepts every request to assign/propagate `X-Request-ID`, calculate response latency (`X-Response-Time-MS`), inject enterprise security headers, and record structured access logs.
   * Error responses uniformly adhere to the standard error envelope.

3. **Application & Service Layer (`apps/api/app/services`):**
   * Encapsulates all domain workflows and business rules.
   * Contains zero HTTP concerns (no `Request`, `Response`, or HTTP status code dependencies).
   * Defines provider abstraction interfaces (`MarketDataProvider`).

4. **Repository Layer (`apps/api/app/repositories`):**
   * Encapsulates all database querying and persistence logic using SQLAlchemy 2.0 async sessions.
   * Isolates the service layer from raw SQL or ORM intricacies.

5. **Persistence Layer (`apps/api/app/db` & `alembic`):**
   * PostgreSQL 16 relational database with UTC timestamps, UUID primary keys, and strict foreign keys.
   * Schema changes are strictly versioned through Alembic migrations (`alembic upgrade head`).

---

## 4. Provider Abstraction Architecture

To avoid vendor lock-in to any single market data or financial vendor (Bloomberg, Refinitiv, Polygon.io, Interactive Brokers, SEC EDGAR), the system establishes an abstract contract:

```text
                  ┌──────────────────────┐
                  │  MarketDataProvider  │ (Abstract Base Class)
                  └──────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
     │ Polygon.io  │  │ YFinance    │  │ MockProvider │ (Testing & Architecture)
     │ (Future)    │  │ (Future)    │  │ (Group 1)    │
     └─────────────┘  └─────────────┘  └──────────────┘
```

In accordance with the **Financial-System Safety Principle**, the `MockMarketDataProvider` in Group 1 does **not** generate fabricated prices or synthetic historical performance. Any call to un-implemented market data endpoints raises `NotImplementedError` with an informative message explaining that live data ingestion belongs to future modules.

---

## 5. Domain-Driven Future Module Boundaries

Future research engines will be integrated as isolated modules plugging into the existing FastAPI router and service layers:

| Module | Scope & Responsibility | Phase |
| :--- | :--- | :--- |
| `market_data` | Normalized real-time and historical price ingestion, corporate actions, dividends | Group 2 |
| `fundamentals` | SEC financial statements, balance sheet ratios, earnings quality, cash-flow analysis | Group 2 |
| `technical` | Mathematical indicators (EMA, RSI, MACD, Bollinger Bands, ATR) | Group 2 |
| `quant` | Cross-sectional & time-series factor modeling, multi-factor ranking, Fama-French | Group 3 |
| `news_macro` | Macroeconomic series (Fed funds, CPI, yield curve) and news sentiment | Group 3 |
| `regime` | Market regime detection (HMM, volatility clustering, trend state) | Group 3 |
| `strategies` | Systematic rules engines, execution criteria, signal aggregation | Group 4 |
| `backtesting` | Event-driven backtester with transaction costs, slippage, and liquidity bounds | Group 4 |
| `risk` | Parametric/Historical VaR, Expected Shortfall, Monte Carlo stress testing | Group 4 |
| `portfolio` | Mean-variance optimization, Black-Litterman, Risk Parity, constraints solver | Group 5 |
| `research` | Explainable decision synthesis, scenario workbench, reproducibility tracking | Group 5 |

---

## 6. Financial-System Safety & Integrity Rules

1. **Zero Data Fabrication:** The system must never fabricate market data, historical returns, Sharpe ratios, risk metrics, or backtest results. When data is unavailable, it is represented strictly as `unknown` or `None`.
2. **Explicit Modality Separation:** The platform must never blur distinctions between:
   * Historical Observations (actual verified past market data)
   * Model Outputs (statistical estimates from algorithms)
   * Backtest Results (simulated performance subject to look-ahead & selection bias)
   * Hypothetical Scenarios (what-if stress test projections)
   * Predictions (probabilistic model forecasts)
   * User Assumptions (client-defined parameters)
3. **Regulatory & Risk Disclaimers:** All customer-facing views must prominently feature the institutional disclaimer declaring that past performance does not guarantee future results and that the system does not offer guaranteed profits or bounded losses.

---

## 7. Observability & Tracing Architecture

* **Request ID:** Every HTTP request carries an `X-Request-ID`. Generated via UUIDv4 if omitted by the client. Binds to Python `contextvars` to annotate all application logs.
* **Structured Logging:** Emits JSON in production and readable colorized output in development. Automatically redacts credentials, passwords, and tokens.
* **Telemetry:** In-memory collector captures request volume, status codes, and latency distributions accessible via `GET /api/v1/system/info`.
