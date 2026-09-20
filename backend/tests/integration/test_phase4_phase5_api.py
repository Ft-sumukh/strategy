"""
AEGIS INVEST — Integration Tests for Phase 4 & Phase 5 APIs
Tests Portfolios, Backtesting, Risk, Stress Testing, Optimization, AI Research, Watchlists, and Theses.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_portfolios_crud_and_analytics(client: AsyncClient):
    # 1. List seeded portfolios
    res = await client.get("/api/v1/portfolios")
    assert res.status_code == 200
    portfolios = res.json()
    assert len(portfolios) >= 1
    port_id = portfolios[0]["id"]

    # 2. Get portfolio by ID
    res_get = await client.get(f"/api/v1/portfolios/{port_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == port_id

    # 3. Get portfolio analytics
    res_an = await client.get(f"/api/v1/portfolios/{port_id}/analytics")
    assert res_an.status_code == 200
    data = res_an.json()
    assert "metrics" in data
    assert "hhi_concentration" in data["metrics"]


@pytest.mark.asyncio
async def test_risk_and_stress_testing_api(client: AsyncClient):
    # Get demo portfolio
    res_ports = await client.get("/api/v1/portfolios")
    port_id = res_ports.json()[0]["id"]

    # 1. Risk Profile
    res_risk = await client.get(f"/api/v1/risk/portfolio/{port_id}")
    assert res_risk.status_code == 200
    assert "risk_metrics" in res_risk.json()

    # 2. Stress Scenarios list
    res_sc = await client.get("/api/v1/stress-test/scenarios")
    assert res_sc.status_code == 200
    assert len(res_sc.json()) >= 5

    # 3. Run Stress Test
    res_run_stress = await client.post(
        "/api/v1/stress-test/run",
        json={"portfolio_id": port_id, "scenario_key": "2008_GFC"},
    )
    assert res_run_stress.status_code == 200
    assert "stress_test_result" in res_run_stress.json()


@pytest.mark.asyncio
async def test_optimization_and_backtest_api(client: AsyncClient):
    # Get demo portfolio
    res_ports = await client.get("/api/v1/portfolios")
    port_id = res_ports.json()[0]["id"]

    # 1. Run Optimization
    res_opt = await client.post(
        "/api/v1/optimization/run",
        json={"portfolio_id": port_id, "objective": "MAX_SHARPE", "min_weight": 0.05, "max_weight": 0.35},
    )
    assert res_opt.status_code == 200
    assert "optimization_result" in res_opt.json()

    # 2. Run Backtest
    res_bt = await client.post(
        "/api/v1/backtesting/run",
        json={
            "name": "Integration Test Backtest",
            "strategy_key": "momentum",
            "universe": ["AAPL", "MSFT", "NVDA"],
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "initial_capital": 100000.0,
            "rebalance_frequency": "MONTHLY",
        },
    )
    assert res_bt.status_code == 200
    assert "metrics" in res_bt.json()


@pytest.mark.asyncio
async def test_ai_research_and_workspace_api(client: AsyncClient):
    # 1. AI Provider Status
    res_status = await client.get("/api/v1/ai/status")
    assert res_status.status_code == 200
    st_data = res_status.json()
    assert "llm_provider" in st_data
    assert "llm_model" in st_data
    assert st_data["status"] in ["configured", "missing_credentials"]

    # 2. AI Research
    res_ai = await client.post(
        "/api/v1/ai/research",
        json={"query": "Analyze NVDA valuation and competitive moat", "subject_ticker": "NVDA"},
    )
    assert res_ai.status_code == 200
    ai_data = res_ai.json()
    assert "response" in ai_data
    assert len(ai_data["citations"]) > 0

    # 2. Watchlists
    res_wl = await client.get("/api/v1/workspace/watchlists")
    assert res_wl.status_code == 200
    assert len(res_wl.json()) >= 1

    # 3. Theses
    res_th = await client.get("/api/v1/workspace/theses")
    assert res_th.status_code == 200
    assert len(res_th.json()) >= 1

    # 4. Alerts
    res_al = await client.get("/api/v1/workspace/alerts")
    assert res_al.status_code == 200
    assert len(res_al.json()) >= 1

    # 5. Models Registry
    res_md = await client.get("/api/v1/models")
    assert res_md.status_code == 200
    assert len(res_md.json()) >= 4
