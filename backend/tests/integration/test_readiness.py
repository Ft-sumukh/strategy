"""
Tests for /api/v1/readiness (Readiness Probe).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_readiness_endpoint_success(client: AsyncClient):
    """Verifies that GET /api/v1/readiness returns 200 with database component ok."""
    response = await client.get("/api/v1/readiness")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "aegis-invest"
    assert "database" in data["components"]
    assert data["components"]["database"]["status"] == "ok"
    assert data["components"]["database"]["latency_ms"] is not None
    assert "redis" in data["components"]
    assert data["components"]["redis"]["status"] == "disabled"


@pytest.mark.asyncio
async def test_health_readiness_canonical_endpoint_success(client: AsyncClient):
    """Verifies that GET /api/v1/health/readiness returns 200."""
    response = await client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "healthy")
    assert "database" in data["components"]
