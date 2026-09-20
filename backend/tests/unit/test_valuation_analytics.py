"""
Unit tests for Valuation Analytics Engine.
Verifies multiples, historical percentiles, peer comparison, and DCF model with sensitivity grid.
"""

from types import SimpleNamespace
import pytest
from app.analytics.valuation.engine import ValuationEngine


@pytest.fixture
def engine():
    return ValuationEngine()


def test_valuation_multiples(engine):
    inc = SimpleNamespace(
        revenue=1000.0,
        ebitda=300.0,
        net_income=200.0,
        diluted_eps=10.0,
        eps=10.0,
    )
    bs = SimpleNamespace(
        total_debt=400.0,
        cash_and_equivalents=100.0,
        short_term_investments=100.0,
        shareholders_equity=800.0,
    )
    cf = SimpleNamespace(free_cash_flow=180.0)

    # Current price = 200.0, Shares = 20.0 -> Market Cap = 4000.0
    # Net Debt = 400 - 200 = 200
    # EV = 4000 + 200 = 4200
    # P/E = 200 / 10 = 20.0
    # EV/EBITDA = 4200 / 300 = 14.0
    # P/S = 4000 / 1000 = 4.0
    # P/B = 4000 / 800 = 5.0
    # FCF Yield = 180 / 4000 = 0.045 (4.5%)
    multiples = engine.compute_multiples(
        current_price=200.0,
        shares_outstanding=20.0,
        income_stmt=inc,
        balance_sheet=bs,
        cash_flow=cf,
    )

    assert multiples.market_cap == pytest.approx(4000.0)
    assert multiples.enterprise_value == pytest.approx(4200.0)
    assert multiples.pe_ratio == pytest.approx(20.0)
    assert multiples.ev_to_ebitda == pytest.approx(14.0)
    assert multiples.ps_ratio == pytest.approx(4.0)
    assert multiples.pb_ratio == pytest.approx(5.0)
    assert multiples.fcf_yield == pytest.approx(0.045)


def test_historical_context(engine):
    history = [15.0, 18.0, 20.0, 22.0, 25.0, 30.0]
    ctx = engine.calculate_historical_context("P/E", 21.0, history)
    assert ctx.min_3y == 15.0
    assert ctx.max_3y == 30.0
    # 21 is greater than 3 items (15, 18, 20) out of 6 -> 50th percentile
    assert ctx.percentile_3y == pytest.approx(50.0)


def test_dcf_model_and_sensitivity(engine):
    # Test deterministic DCF
    # FCF base = 100, g1 = 10%, WACC = 9%, g_term = 2.5%, Shares = 10
    # Debt = 100, Cash = 200, Current Price = 250
    result = engine.run_dcf_model(
        ticker="TEST",
        current_price=250.0,
        shares_outstanding=10.0,
        fcf_base=100.0,
        growth_rate_stage1=0.10,
        terminal_growth_rate=0.025,
        wacc=0.09,
        total_debt=100.0,
        cash_and_investments=200.0,
    )

    assert result.ticker == "TEST"
    assert len(result.projections) == 5
    assert result.projections[0].projected_fcf == pytest.approx(110.0)
    assert result.projections[4].projected_fcf == pytest.approx(161.05, abs=0.1)

    # Verify terminal value: FCF_5 * (1 + 0.025) / (0.09 - 0.025) = 161.051 * 1.025 / 0.065 ~= 2539.6
    assert result.terminal_value > 2500.0
    assert result.enterprise_value > 0
    assert result.equity_value == pytest.approx(result.enterprise_value - 100.0 + 200.0, abs=1e-2)
    assert result.implied_share_price > 0

    # Verify sensitivity matrix dimensions
    # 7 WACC steps x 5 Growth steps
    assert len(result.sensitivity_matrix) == 7
    assert len(result.sensitivity_matrix[0]) == 5
    assert len(result.sensitivity_wacc_labels) == 7
    assert len(result.sensitivity_growth_labels) == 5
