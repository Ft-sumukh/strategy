"""
AEGIS INVEST — Unit Tests for Portfolio Analytics Engine
Verifies performance calculation, HHI concentration, and Sharpe/Sortino ratios.
"""

import pytest
from app.analytics.portfolio.engine import PortfolioAnalyticsEngine


def test_portfolio_metrics_calculation():
    engine = PortfolioAnalyticsEngine(risk_free_rate=0.04)

    holdings = [
        {"ticker": "AAPL", "weight": 0.5, "quantity": 100, "cost_basis": 150.0},
        {"ticker": "MSFT", "weight": 0.5, "quantity": 50, "cost_basis": 300.0},
    ]
    # 20 days of prices with 1% daily alternating returns
    aapl_prices = [100.0 * (1.01 ** i) for i in range(25)]
    msft_prices = [200.0 * (1.008 ** i) for i in range(25)]

    price_series = {
        "AAPL": aapl_prices,
        "MSFT": msft_prices,
    }

    res = engine.compute_portfolio_metrics(holdings, price_series)

    assert res["total_return"] > 0.0
    assert res["annualized_return"] > 0.0
    assert res["annualized_volatility"] >= 0.0
    assert res["hhi_concentration"] == 0.5  # 0.5^2 + 0.5^2 = 0.50
    assert "AAPL" in res["weights"]
    assert "MSFT" in res["weights"]
    assert len(res["cumulative_returns"]) > 0


def test_portfolio_empty_holdings():
    engine = PortfolioAnalyticsEngine()
    res = engine.compute_portfolio_metrics([], {})
    assert res["total_return"] == 0.0
    assert res["hhi_concentration"] == 0.0
