"""
Tests for /api/v1/health (Liveness Probe).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_success(client: AsyncClient):
    """Verifies that GET /api/v1/health returns 200 with valid schema."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ("healthy", "ok")
    assert data["service"] == "aegis-invest"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers
