"""
Tests for /api/v1/system/info and root endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_info_endpoint(client: AsyncClient):
    """Verifies that GET /api/v1/system/info returns metadata and telemetry."""
    response = await client.get("/api/v1/system/info")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "aegis-invest"
    assert data["version"] == "0.1.0"
    assert "uptime_seconds" in data
    assert "telemetry" in data
    assert "total_requests" in data["telemetry"]


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verifies that GET / returns root landing metadata."""
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "aegis-invest"
    assert data["api_v1"] == "/api/v1"
