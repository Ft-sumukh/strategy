"""
Integration tests for AEGIS INVEST Phase 2 Financial Intelligence Endpoints:
- GET /api/v1/fundamentals/{ticker}
- GET /api/v1/valuation/{ticker}
- POST /api/v1/valuation/{ticker}/dcf
- GET /api/v1/technicals/{ticker}
- GET /api/v1/factors/{ticker}
- GET /api/v1/stocks/{ticker}/intelligence
- GET /api/v1/screener
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fundamentals_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/fundamentals/AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert "growth" in data
    assert "profitability" in data
    assert "balance_sheet_health" in data
    assert "cash_flow_quality" in data
    assert "scorecard" in data
    assert len(data["scorecard"]["categories"]) == 6
    assert data["scorecard"]["overall_score"] > 0
    assert len(data["income_statements"]) > 0


@pytest.mark.asyncio
async def test_valuation_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/valuation/MSFT")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "MSFT"
    assert "multiples" in data
    assert data["multiples"]["pe_ratio"] is not None
    assert "dcf" in data
    assert data["dcf"]["implied_share_price"] > 0
    assert len(data["dcf"]["sensitivity_matrix"]) == 7


@pytest.mark.asyncio
async def test_dcf_interactive_endpoint(client: AsyncClient):
    payload = {
        "wacc": 0.085,
        "terminal_growth_rate": 0.025,
        "growth_rate_stage1": 0.12,
    }
    resp = await client.post("/api/v1/valuation/NVDA/dcf", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "NVDA"
    assert data["wacc"] == 0.085
    assert data["terminal_growth_rate"] == 0.025
    assert data["implied_share_price"] > 0
    assert len(data["projections"]) == 5


@pytest.mark.asyncio
async def test_technicals_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/technicals/GOOG")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "GOOG"
    assert "moving_averages" in data
    assert "rsi" in data
    assert "macd" in data
    assert "bollinger" in data
    assert len(data["signals"]) > 0
    assert data["overall_sentiment"] in ["BULLISH", "BEARISH", "NEUTRAL"]


@pytest.mark.asyncio
async def test_factors_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/factors/AMZN")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AMZN"
    assert "factors" in data
    assert len(data["factors"]) == 7
    assert "summary_radar" in data
    assert "Momentum" in data["summary_radar"]
    assert "Quality" in data["summary_radar"]


@pytest.mark.asyncio
async def test_stock_intelligence_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/stocks/AAPL/intelligence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert data["profile"]["name"] == "Apple Inc."
    assert "fundamentals_summary" in data
    assert "valuation_summary" in data
    assert "technicals_summary" in data
    assert "factors_summary" in data
    assert data["data_provenance"]["quality_status"] == "AUDITED"


@pytest.mark.asyncio
async def test_screener_endpoint(client: AsyncClient):
    # Test unconstrained screener
    resp = await client.get("/api/v1/screener")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 5
    assert len(data["items"]) >= 5

    # Test sector filtering
    resp_tech = await client.get("/api/v1/screener?sector=Technology")
    assert resp_tech.status_code == 200
    data_tech = resp_tech.json()
    for item in data_tech["items"]:
        assert "Technology" in item["sector"]

    # Test sorting
    resp_sort = await client.get("/api/v1/screener?sort_by=scorecard_score&sort_direction=desc")
    assert resp_sort.status_code == 200
    scores = [item["scorecard_score"] for item in resp_sort.json()["items"]]
    assert scores == sorted(scores, reverse=True)
