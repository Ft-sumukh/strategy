"""
Unit tests for Fundamentals Analytics Engine.
Verifies growth metrics, margins, ROE, ROIC, Sloan accruals, and scorecard.
"""

from types import SimpleNamespace
import pytest
from app.analytics.fundamentals.engine import FundamentalsEngine


@pytest.fixture
def engine():
    return FundamentalsEngine()


def test_growth_metrics(engine):
    # Year 0: Rev 120, NI 30, EPS 3.0
    # Year 1: Rev 100, NI 25, EPS 2.5
    # Year 3: Rev 70
    stmts = [
        SimpleNamespace(revenue=120.0, net_income=30.0, diluted_eps=3.0, eps=3.0, ebitda=40.0),
        SimpleNamespace(revenue=100.0, net_income=25.0, diluted_eps=2.5, eps=2.5, ebitda=35.0),
        SimpleNamespace(revenue=85.0, net_income=20.0, diluted_eps=2.0, eps=2.0, ebitda=30.0),
        SimpleNamespace(revenue=70.0, net_income=15.0, diluted_eps=1.5, eps=1.5, ebitda=25.0),
    ]

    growth = engine.compute_growth(stmts)
    assert growth.revenue_yoy == pytest.approx(0.20, abs=1e-3)
    assert growth.net_income_yoy == pytest.approx(0.20, abs=1e-3)
    assert growth.eps_yoy == pytest.approx(0.20, abs=1e-3)
    assert growth.ebitda_yoy == pytest.approx(0.1428, abs=1e-3)
    # 3-year CAGR: (120 / 70) ** (1/3) - 1 = 1.71428 ** 0.33333 - 1 ~= 0.1968
    assert growth.revenue_cagr_3y == pytest.approx(0.1968, abs=1e-3)


def test_profitability_metrics(engine):
    inc = SimpleNamespace(
        revenue=1000.0,
        gross_profit=450.0,
        operating_income=300.0,
        ebitda=350.0,
        net_income=240.0,
        tax_expense=60.0,
        pre_tax_income=300.0,
    )
    bs = SimpleNamespace(
        total_assets=2000.0,
        shareholders_equity=1200.0,
        total_debt=400.0,
        cash_and_equivalents=200.0,
        short_term_investments=100.0,
    )

    prof = engine.compute_profitability(inc, bs)
    assert prof.gross_margin == pytest.approx(0.45)
    assert prof.operating_margin == pytest.approx(0.30)
    assert prof.ebitda_margin == pytest.approx(0.35)
    assert prof.net_margin == pytest.approx(0.24)
    assert prof.return_on_assets == pytest.approx(0.12)
    assert prof.return_on_equity == pytest.approx(0.20)
    # Effective tax rate = 60 / 300 = 0.20
    # NOPAT = 300 * (1 - 0.20) = 240
    # Invested Capital = 400 + 1200 - (200 + 100) = 1300
    # ROIC = 240 / 1300 = 0.1846
    assert prof.return_on_invested_capital == pytest.approx(0.1846, abs=1e-3)


def test_balance_sheet_health(engine):
    bs = SimpleNamespace(
        total_debt=500.0,
        shareholders_equity=1000.0,
        cash_and_equivalents=300.0,
        short_term_investments=400.0,
        current_assets=1200.0,
        current_liabilities=600.0,
        short_term_debt=100.0,
        long_term_debt=400.0,
    )

    health = engine.compute_balance_sheet_health(bs, ebitda=250.0, operating_income=200.0, interest_expense=20.0)
    assert health.debt_to_equity == pytest.approx(0.5)
    # Net debt = 500 - (300 + 400) = -200 (Net Cash)
    assert health.net_debt == -200.0
    assert health.is_net_cash is True
    assert health.current_ratio == pytest.approx(2.0)
    assert health.quick_ratio == pytest.approx(700.0 / 600.0)
    assert health.interest_coverage == pytest.approx(10.0)


def test_earnings_quality_sloan_accruals(engine):
    inc = SimpleNamespace(net_income=100.0)
    cf = SimpleNamespace(operating_cash_flow=130.0)
    bs = SimpleNamespace(total_assets=1000.0)

    # Sloan accruals = (100 - 130) / 1000 = -0.03 (Cash generation > Net income -> High quality)
    eq = engine.compute_earnings_quality(inc, cf, bs)
    assert eq.sloan_accruals_ratio == pytest.approx(-0.03)
    assert eq.cash_backed_earnings is True
    assert "High Quality" in eq.accruals_interpretation or "Normal Quality" in eq.accruals_interpretation


def test_scorecard_generation(engine):
    growth = engine.compute_growth([
        SimpleNamespace(revenue=120.0, net_income=30.0, diluted_eps=3.0, eps=3.0, ebitda=40.0),
        SimpleNamespace(revenue=100.0, net_income=25.0, diluted_eps=2.5, eps=2.5, ebitda=35.0),
        SimpleNamespace(revenue=85.0, net_income=20.0, diluted_eps=2.0, eps=2.0, ebitda=30.0),
        SimpleNamespace(revenue=70.0, net_income=15.0, diluted_eps=1.5, eps=1.5, ebitda=25.0),
    ])
    inc = SimpleNamespace(revenue=120.0, gross_profit=60.0, operating_income=36.0, ebitda=40.0, net_income=30.0, tax_expense=6.0, pre_tax_income=36.0)
    bs = SimpleNamespace(total_assets=200.0, shareholders_equity=120.0, total_debt=20.0, cash_and_equivalents=50.0, short_term_investments=20.0, current_assets=100.0, current_liabilities=50.0)
    cf = SimpleNamespace(operating_cash_flow=35.0, capital_expenditure=5.0, free_cash_flow=30.0)

    prof = engine.compute_profitability(inc, bs)
    health = engine.compute_balance_sheet_health(bs, ebitda=40.0)
    cf_qual = engine.compute_cash_flow_quality(cf, revenue=120.0, ebitda=40.0, net_income=30.0)
    eq = engine.compute_earnings_quality(inc, cf, bs)

    scorecard = engine.generate_scorecard(growth, prof, health, cf_qual, eq)
    assert 0 <= scorecard.overall_score <= 100
    assert len(scorecard.categories) == 6
    assert scorecard.rating in ["Exemplary", "Strong", "Moderate", "Cautious", "Distressed"]
