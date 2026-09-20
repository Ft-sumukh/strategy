"""
AEGIS INVEST — Unit Tests for Backtesting & Optimization Engines
"""

from datetime import datetime, timezone, timedelta
import pytest
from app.analytics.backtesting.engine import BacktestEngine
from app.analytics.optimization.engine import PortfolioOptimizationEngine


def test_backtest_execution():
    engine = BacktestEngine(risk_free_rate=0.04)

    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 6, 1, tzinfo=timezone.utc)

    # 100 days of price data
    daily_prices = {
        "AAPL": [{"timestamp": start_date + timedelta(days=i), "close": 150.0 * (1.002 ** i)} for i in range(100)],
        "MSFT": [{"timestamp": start_date + timedelta(days=i), "close": 250.0 * (1.0015 ** i)} for i in range(100)],
    }

    def signal_fn(dt, universe, price_hist):
        return {"AAPL": 0.5, "MSFT": 0.5}

    res = engine.run_backtest(
        daily_prices=daily_prices,
        strategy_signal_generator=signal_fn,
        universe=["AAPL", "MSFT"],
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        rebalance_frequency="MONTHLY",
        transaction_cost_bps=10.0,
        slippage_bps=5.0,
    )

    assert res["total_return"] > 0.0
    assert len(res["equity_points"]) > 0
    assert len(res["trades"]) > 0
    assert res["trades_count"] > 0


def test_portfolio_optimization():
    engine = PortfolioOptimizationEngine(risk_free_rate=0.04)
    universe = ["AAPL", "MSFT", "NVDA"]

    # 30 days of simulated returns
    asset_returns = {
        "AAPL": [0.01, -0.005, 0.008, -0.002, 0.012] * 6,
        "MSFT": [0.008, -0.003, 0.006, -0.001, 0.009] * 6,
        "NVDA": [0.025, -0.015, 0.02, -0.008, 0.03] * 6,
    }

    # 1. Max Sharpe
    res_sharpe = engine.optimize_portfolio(universe, asset_returns, objective="MAX_SHARPE")
    assert res_sharpe["status"] == "OPTIMAL"
    assert sum(res_sharpe["optimized_weights"].values()) == pytest.approx(1.0, rel=1e-3)

    # 2. Risk Parity
    res_rp = engine.optimize_portfolio(universe, asset_returns, objective="RISK_PARITY")
    assert res_rp["status"] == "OPTIMAL"
    assert sum(res_rp["optimized_weights"].values()) == pytest.approx(1.0, rel=1e-3)
    # NVDA has higher volatility so Risk Parity should give NVDA a smaller weight than MSFT
    assert res_rp["optimized_weights"]["NVDA"] <= res_rp["optimized_weights"]["MSFT"]
