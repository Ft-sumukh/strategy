# ADR-003: PostgreSQL Relational Database & Alembic Migrations

## Status
Accepted

## Context
Financial analytics, strategy definitions, portfolio parameters, and audit trails demand:
* Strict ACID transaction guarantees.
* Relational integrity (foreign keys, constraints, unique indexes).
* Rich indexing (B-Tree, GiST/BRIN for time-series ranges, JSONB for semi-structured metadata).
* Controlled, auditable, and reversible schema migration workflows.

## Decision
Use **PostgreSQL 16** as the primary relational persistence store, accessed through **SQLAlchemy 2.0 AsyncEngine** and migrated exclusively through **Alembic**.
In development and unit testing, support SQLite (`sqlite+aiosqlite`) transparently for zero-dependency test runs while deploying PostgreSQL in containerized and production environments.

In Group 1, we establish:
* `Base` declarative model with UTC `TimestampMixin` and `UUIDPrimaryKeyMixin`.
* Initial migration `0001_initial_foundation` establishing the `system_audit` table.
* Strictly defer financial domain models (stocks, prices, trades, portfolios) to subsequent phases.

## Consequences
### Positive
* Rock-solid data integrity for critical financial data.
* Reproducible, version-controlled database state.
* Clean testing via fast in-memory SQLite alongside full PostgreSQL production fidelity.

### Negative
* Requires migration hygiene; no out-of-band schema alterations.

## Alternatives Considered
* **MongoDB / Document Store:** Rejected because financial ledgers and structured time-series data require strong relational integrity and transactional consistency.
