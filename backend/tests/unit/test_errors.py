"""
Tests for error handling and standard error envelope.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_404_error_envelope(client: AsyncClient):
    """Verifies that 404 responses conform to the standard error envelope."""
    response = await client.get("/api/v1/nonexistent-route")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]
    assert "request_id" in data["error"]
    assert "timestamp" in data["error"]


@pytest.mark.asyncio
async def test_method_not_allowed_error_envelope(client: AsyncClient):
    """Verifies that 405 responses conform to the standard error envelope."""
    response = await client.post("/api/v1/health")
    assert response.status_code == 405

    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"
