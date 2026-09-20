# ADR-001: Monorepo Architecture

## Status
Accepted

## Context
AEGIS INVEST requires multiple synchronized software subsystems:
* A Next.js web application for user-facing research and portfolio analytics.
* A FastAPI Python backend for high-performance API services, quantitative modeling, and data pipelines.
* Shared schemas, contracts, configuration parameters, and utility packages.
* Unified infrastructure automation, database migrations, and CI workflows.

Managing separate independent repositories creates synchronization friction, drift in API contracts, version fragmentation, and complex local developer onboarding.

## Decision
Adopt a structured monorepo design organized into:
* `apps/web`: Frontend Next.js application
* `apps/api`: Backend FastAPI platform
* `packages/*`: Shared TypeScript types, configuration constants, and utilities
* `infrastructure/*`: Docker container definitions, database scripts, bootstrap tools
* `docs/*`: Architecture blueprints, ADRs, and API references
* `tests/*`: Monorepo integration and end-to-end test suites

We use npm workspaces at the repository root for Node.js dependency management while keeping Python dependencies clean and isolated in `apps/api/requirements.txt` and `pyproject.toml`.

## Consequences
### Positive
* Single source of truth for the entire platform.
* Atomic cross-subsystem changes (e.g. updating API schema and frontend types in the same commit).
* Streamlined CI pipelines and local developer setup with one repository clone.

### Negative
* Requires consistent workspace tooling to prevent cross-contamination.
* CI configuration must use path-filtering to avoid running backend CI on frontend-only changes and vice versa.

## Alternatives Considered
* **Polyrepo (Separate git repositories):** Rejected due to high risk of contract divergence, submodule overhead, and cumbersome local multi-repo orchestration.
