# AEGIS INVEST — API Reference (v1)

All endpoints are versioned under the `/api/v1` prefix.

## 1. Request Headers

| Header | Type | Description |
| :--- | :--- | :--- |
| `Content-Type` | `string` | Must be `application/json` for request bodies |
| `Accept` | `string` | Must be `application/json` |
| `X-Request-ID` | `string (UUID)` | Optional client request ID. If omitted, the server automatically generates a UUIDv4 and returns it. |

## 2. Response Headers

| Header | Type | Description |
| :--- | :--- | :--- |
| `X-Request-ID` | `string` | The unique request identifier for correlation and log tracing |
| `X-Response-Time-MS` | `float` | Server execution duration in milliseconds |
| `X-Content-Type-Options` | `string` | `nosniff` |
| `X-Frame-Options` | `string` | `DENY` |

---

## 3. Endpoints

### 3.1 Process Liveness Probe
**`GET /api/v1/health`**

Confirms that the FastAPI process is alive and accepting connections.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "service": "aegis-invest",
  "version": "0.1.0",
  "timestamp": "2026-09-11T14:40:00.123456Z"
}
```

---

### 3.2 Service Readiness Probe
**`GET /api/v1/readiness`**

Verifies whether essential downstream dependencies (PostgreSQL database, Redis cache) are available and responsive.

**Response `200 OK` (Healthy):**
```json
{
  "status": "ok",
  "service": "aegis-invest",
  "version": "0.1.0",
  "timestamp": "2026-09-11T14:40:00.123456Z",
  "components": {
    "database": {
      "status": "ok",
      "latency_ms": 2.14,
      "details": null
    },
    "redis": {
      "status": "disabled",
      "latency_ms": null,
      "details": "Redis caching not enabled in current environment"
    }
  }
}
```

**Response `503 Service Unavailable` (Database Down):**
```json
{
  "status": "unavailable",
  "service": "aegis-invest",
  "version": "0.1.0",
  "timestamp": "2026-09-11T14:40:00.123456Z",
  "components": {
    "database": {
      "status": "unavailable",
      "latency_ms": 30.12,
      "details": "Database connection failed"
    },
    "redis": {
      "status": "disabled",
      "latency_ms": null,
      "details": "Redis caching not enabled in current environment"
    }
  }
}
```

---

### 3.3 System Metadata & Telemetry
**`GET /api/v1/system/info`**

Exposes operational telemetry and deployment environment metadata.

**Response `200 OK`:**
```json
{
  "service": "aegis-invest",
  "version": "0.1.0",
  "environment": "development",
  "uptime_seconds": 1284.5,
  "telemetry": {
    "uptime_seconds": 1284.5,
    "total_requests": 142,
    "total_errors": 0,
    "status_codes": {
      "200": 142
    },
    "avg_latency_ms": 3.42
  }
}
```

---

## 4. Standard Error Envelope

All API errors return a consistent RFC-compliant JSON structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed. Verify input parameters.",
    "details": [
      {
        "field": "body -> symbol",
        "message": "Field required",
        "type": "missing"
      }
    ],
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-09-11T14:40:00.123456Z"
  }
}
```

### Standard Error Codes:
* `VALIDATION_ERROR` (422)
* `BAD_REQUEST` (400)
* `UNAUTHORIZED` (401)
* `FORBIDDEN` (403)
* `NOT_FOUND` (404)
* `METHOD_NOT_ALLOWED` (405)
* `RATE_LIMIT_EXCEEDED` (429)
* `INTERNAL_SERVER_ERROR` (500)
* `DATABASE_CONNECTION_ERROR` (503)
* `SERVICE_UNAVAILABLE` (503)
