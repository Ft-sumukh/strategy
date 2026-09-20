# ADR-005: API Versioning & Standard Error Envelope

## Status
Accepted

## Context
A financial intelligence platform cannot tolerate breaking changes in API contracts. Furthermore, client applications, automated trading connectors, and developer integrations need deterministic error reporting that never leaks internal infrastructure details (e.g. database connection strings or stack traces).

## Decision
1. **URI Versioning:** All endpoints are versioned explicitly under `/api/v1/`. Future breaking changes will introduce `/api/v2/` in parallel.
2. **Standard Error Envelope:** All HTTP errors (4xx and 5xx) must return a uniform RFC-7807-inspired JSON structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": [],
    "request_id": "uuid-here",
    "timestamp": "2026-09-11T14:40:00Z"
  }
}
```
3. **Traceability:** Every response must include `X-Request-ID` and `X-Response-Time-MS`.
4. **Information Hiding:** In production environments, unhandled 500 errors must display a safe generic message rather than Python tracebacks.

## Consequences
### Positive
* Frontend and external consumers can rely on deterministic error handling.
* Every error is correlated with backend logs via `request_id`.
* Elimination of information leakage vulnerabilities.

### Negative
* Requires overriding default FastAPI and Starlette exception handlers to enforce envelope conformity.
