# AEGIS INVEST — Development Scripts

Convenient automation scripts for local environment management, testing, and database migrations.

| Script | Purpose |
| :--- | :--- |
| `setup.ps1` | Installs Python backend packages and frontend npm dependencies. |
| `dev.ps1` | Concurrently launches backend (:8000) and frontend (:3000) servers. |
| `backend.ps1` | Launches FastAPI backend with auto-reload. |
| `frontend.ps1` | Launches Next.js frontend development server. |
| `test.ps1` | Executes all backend pytest and frontend vitest/typecheck suites. |
| `db.ps1` | Manages Alembic migrations (`-Action upgrade`, `downgrade`, `status`, `revision`). |

Linux/macOS developers may alternatively invoke targets directly via `make` (`make dev`, `make test`, `make db-upgrade`).
