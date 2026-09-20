"""
Tests for middleware (Request ID, Logging, Security Headers).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_generated_if_absent(client: AsyncClient):
    """Verifies X-Request-ID is generated and returned if client does not supply one."""
    response = await client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 10


@pytest.mark.asyncio
async def test_request_id_propagated_if_present(client: AsyncClient):
    """Verifies client-provided X-Request-ID is preserved throughout the response."""
    custom_id = "test-custom-request-id-998877"
    response = await client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_response_time_header(client: AsyncClient):
    """Verifies X-Response-Time-MS header is returned with a valid float value."""
    response = await client.get("/api/v1/health")
    assert "X-Response-Time-MS" in response.headers
    latency = float(response.headers["X-Response-Time-MS"])
    assert latency >= 0.0


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """Verifies enterprise security baseline headers are injected."""
    response = await client.get("/api/v1/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "strict-origin" in response.headers.get("Referrer-Policy", "")
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")
