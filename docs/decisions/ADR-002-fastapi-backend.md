# ADR-002: FastAPI for Backend Engineering

## Status
Accepted

## Context
The AEGIS backend must support:
* High-throughput asynchronous HTTP APIs.
* Strict request/response validation with automatic OpenAPI documentation.
* Native interoperability with the Python quantitative and data science ecosystem (NumPy, SciPy, Pandas, PyTorch, Scikit-Learn) for future modules.
* Clean layered architecture (API $\rightarrow$ Middleware $\rightarrow$ Services $\rightarrow$ Repositories $\rightarrow$ Database).

## Decision
Adopt **FastAPI** paired with **Pydantic v2** and **Uvicorn** as the backend framework.
Adopt a layered architecture:
* `api/v1/`: Routing and parameter binding.
* `middleware/`: Request tracing, structured access logging, security headers.
* `services/`: Domain business logic and provider abstractions.
* `repositories/`: Data access abstractions.
* `db/`: SQLAlchemy 2.0 async engine and session lifecycle.
* `core/`: Pydantic settings, structured logging, and global exception handling.

## Consequences
### Positive
* High performance with native async/await.
* Automatic OpenAPI 3.1 JSON and Swagger UI generation.
* Robust validation with detailed type errors.
* Seamless future integration with quantitative Python libraries.

### Negative
* Requires careful discipline to avoid mixing ORM queries directly into route handlers.

## Alternatives Considered
* **Django / Django REST Framework:** Rejected due to heavyweight ORM conventions less suited for specialized quantitative pipelines and high-throughput async APIs.
* **Flask:** Rejected due to lack of native async support, lack of integrated request validation, and manual OpenAPI generation.
