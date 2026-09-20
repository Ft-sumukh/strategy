"""
AEGIS INVEST — Unit Tests for Risk Engine & Stress Testing Engine
"""

import pytest
from app.analytics.risk.engine import RiskEngine
from app.analytics.stress.engine import StressTestEngine


def test_risk_profile_metrics():
    engine = RiskEngine(risk_free_rate=0.04)

    # 30 days of simulated returns
    returns = [-0.01, 0.02, -0.015, 0.005, 0.012, -0.03, 0.025, 0.01, -0.008, 0.015] * 3
    benchmark = [-0.008, 0.015, -0.01, 0.004, 0.01, -0.02, 0.018, 0.008, -0.005, 0.012] * 3

    asset_returns = {
        "AAPL": returns,
        "MSFT": [r * 0.9 for r in returns],
    }
    weights = {"AAPL": 0.6, "MSFT": 0.4}

    res = engine.compute_risk_profile(returns, benchmark, asset_returns, weights)

    assert res["annualized_volatility"] > 0.0
    assert res["var_95"] > 0.0
    assert res["cvar_95"] >= res["var_95"]  # Expected shortfall is at least as large as VaR
    assert res["beta"] > 0.0
    assert "AAPL" in res["correlation_matrix"]
    assert res["correlation_matrix"]["AAPL"]["AAPL"] == 1.0


def test_stress_test_scenarios():
    engine = StressTestEngine()
    scenarios = engine.list_scenarios()
    assert len(scenarios) >= 5

    holdings = [{"ticker": "AAPL", "weight": 0.6}, {"ticker": "NVDA", "weight": 0.4}]
    res = engine.run_stress_scenario("2008_GFC", holdings)

    assert res["scenario_key"] == "2008_GFC"
    assert res["estimated_portfolio_return"] < 0.0  # GFC causes negative return
    assert res["estimated_drawdown"] > 0.0
    assert "AAPL" in res["position_impacts"]
    assert "NVDA" in res["position_impacts"]
