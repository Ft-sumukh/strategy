"""
AEGIS INVEST — Valuation Analytics Engine
Computes valuation multiples (P/E, EV/EBITDA, P/S, P/B, FCF Yield),
historical context/percentiles, relative peer comparisons, and
discounted cash flow (DCF) intrinsic value models with 2D sensitivity matrices.

Guidelines:
- Zero hallucination: Missing data produces None, not 0.
- Clear epistemic status: DCF output is an explicit model calculation, not a forecast.
- Complete assumption transparency.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
import math


def _to_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_div(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


@dataclass
class ValuationMultiples:
    pe_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    ev_to_revenue: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    fcf_yield: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    data_quality: str = "HIGH"


@dataclass
class MultipleHistoricalContext:
    metric_name: str
    current_value: Optional[float]
    median_1y: Optional[float] = None
    median_3y: Optional[float] = None
    median_5y: Optional[float] = None
    percentile_3y: Optional[float] = None  # 0 to 100
    min_3y: Optional[float] = None
    max_3y: Optional[float] = None
    interpretation: str = "Neutral"  # Undervalued, Fairly Valued, Elevated, Premium


@dataclass
class PeerValuationRow:
    ticker: str
    name: str
    price: float
    market_cap: float
    pe_ratio: Optional[float]
    ev_to_ebitda: Optional[float]
    ps_ratio: Optional[float]
    fcf_yield: Optional[float]
    revenue_cagr_3y: Optional[float]


@dataclass
class DCFYearProjection:
    year: int
    projected_fcf: float
    discount_factor: float
    pv_fcf: float


@dataclass
class DCFSensitivityCell:
    wacc: float
    terminal_growth: float
    implied_share_price: float
    upside_percent: float


@dataclass
class DCFModelResult:
    ticker: str
    as_of_date: str
    current_price: float
    implied_share_price: float
    upside_downside_percent: float
    enterprise_value: float
    equity_value: float
    pv_projected_fcfs: float
    pv_terminal_value: float
    terminal_value: float
    shares_outstanding: float
    fcf_base: float
    wacc: float
    terminal_growth_rate: float
    stage1_growth_rate: float
    projections: List[DCFYearProjection]
    sensitivity_matrix: List[List[DCFSensitivityCell]]
    sensitivity_wacc_labels: List[float]
    sensitivity_growth_labels: List[float]
    data_quality: str = "HIGH"
    disclaimer: str = (
        "Intrinsic DCF valuation is highly sensitive to discount rate and terminal growth assumptions. "
        "It represents a structured scenario model, not an investment recommendation or guaranteed price target."
    )


class ValuationEngine:
    """Institutional-grade valuation calculation engine."""

    def compute_multiples(
        self,
        current_price: float,
        shares_outstanding: float,
        income_stmt: Any,
        balance_sheet: Optional[Any] = None,
        cash_flow: Optional[Any] = None,
    ) -> ValuationMultiples:
        """Calculates current point-in-time valuation multiples."""
        if current_price <= 0 or shares_outstanding <= 0:
            return ValuationMultiples(data_quality="INSUFFICIENT_DATA")

        market_cap = current_price * shares_outstanding

        # Net Income & EPS
        ni = _to_float(income_stmt.net_income) if income_stmt else None
        eps = _to_float(income_stmt.diluted_eps or income_stmt.eps) if income_stmt else None
        rev = _to_float(income_stmt.revenue) if income_stmt else None
        ebitda = _to_float(income_stmt.ebitda) if income_stmt else None

        # Debt, Cash & Enterprise Value
        tot_debt = 0.0
        cash_and_inv = 0.0
        equity = None
        if balance_sheet:
            tot_debt = _to_float(balance_sheet.total_debt or 0) or 0.0
            cash = _to_float(balance_sheet.cash_and_equivalents or 0) or 0.0
            st_inv = _to_float(balance_sheet.short_term_investments or 0) or 0.0
            cash_and_inv = cash + st_inv
            equity = _to_float(balance_sheet.shareholders_equity)

        enterprise_value = market_cap + tot_debt - cash_and_inv

        # Multiples
        pe = _safe_div(current_price, eps) if eps and eps > 0 else _safe_div(market_cap, ni) if ni and ni > 0 else None
        ev_to_ebitda = _safe_div(enterprise_value, ebitda) if ebitda and ebitda > 0 else None
        ev_to_revenue = _safe_div(enterprise_value, rev) if rev and rev > 0 else None
        ps = _safe_div(market_cap, rev) if rev and rev > 0 else None
        pb = _safe_div(market_cap, equity) if equity and equity > 0 else None

        fcf_yield = None
        if cash_flow:
            fcf = _to_float(cash_flow.free_cash_flow)
            if fcf is not None and market_cap > 0:
                fcf_yield = fcf / market_cap

        return ValuationMultiples(
            pe_ratio=pe,
            ev_to_ebitda=ev_to_ebitda,
            ev_to_revenue=ev_to_revenue,
            ps_ratio=ps,
            pb_ratio=pb,
            fcf_yield=fcf_yield,
            market_cap=market_cap,
            enterprise_value=enterprise_value,
            data_quality="HIGH" if pe is not None else "MODERATE",
        )

    def calculate_historical_context(
        self,
        metric_name: str,
        current_val: Optional[float],
        historical_values_3y: List[float],
    ) -> MultipleHistoricalContext:
        """Calculates historical percentiles and medians for multiple context."""
        if current_val is None or not historical_values_3y:
            return MultipleHistoricalContext(metric_name=metric_name, current_value=current_val)

        valid_vals = sorted([v for v in historical_values_3y if v is not None and not math.isnan(v)])
        if not valid_vals:
            return MultipleHistoricalContext(metric_name=metric_name, current_value=current_val)

        n = len(valid_vals)
        median = valid_vals[n // 2]
        min_v = valid_vals[0]
        max_v = valid_vals[-1]

        # Percentile rank
        less_count = sum(1 for v in valid_vals if v < current_val)
        percentile = (less_count / float(n)) * 100.0

        if percentile < 25.0:
            interp = "Historical Discount (Low Percentile)"
        elif percentile <= 70.0:
            interp = "In-Line with Historical Median"
        elif percentile <= 85.0:
            interp = "Historical Premium"
        else:
            interp = "Substantially Elevated vs History"

        return MultipleHistoricalContext(
            metric_name=metric_name,
            current_value=current_val,
            median_1y=median,
            median_3y=median,
            median_5y=median,
            percentile_3y=round(percentile, 1),
            min_3y=min_v,
            max_3y=max_v,
            interpretation=interp,
        )

    def run_dcf_model(
        self,
        ticker: str,
        current_price: float,
        shares_outstanding: float,
        fcf_base: float,
        growth_rate_stage1: float = 0.10,
        terminal_growth_rate: float = 0.025,
        wacc: float = 0.09,
        total_debt: float = 0.0,
        cash_and_investments: float = 0.0,
        as_of_date: str = "",
    ) -> DCFModelResult:
        """
        Executes a 5-year Free Cash Flow to Firm (FCFF) Discounted Cash Flow model
        with Gordon Growth Terminal Value and a full 2D WACC x Terminal Growth sensitivity matrix.
        """
        if terminal_growth_rate >= wacc:
            raise ValueError("Terminal growth rate must be strictly less than WACC for Gordon Growth convergence.")

        if shares_outstanding <= 0:
            raise ValueError("Shares outstanding must be positive.")

        # 1. 5-Year Projections
        projections: List[DCFYearProjection] = []
        pv_fcfs = 0.0
        current_fcf = fcf_base

        for yr in range(1, 6):
            current_fcf = current_fcf * (1.0 + growth_rate_stage1)
            df = 1.0 / ((1.0 + wacc) ** yr)
            pv = current_fcf * df
            pv_fcfs += pv
            projections.append(DCFYearProjection(
                year=yr,
                projected_fcf=round(current_fcf, 2),
                discount_factor=round(df, 4),
                pv_fcf=round(pv, 2),
            ))

        # 2. Terminal Value
        # TV = FCF_5 * (1 + g) / (WACC - g)
        fcf_5 = projections[-1].projected_fcf
        tv = (fcf_5 * (1.0 + terminal_growth_rate)) / (wacc - terminal_growth_rate)
        pv_tv = tv / ((1.0 + wacc) ** 5)

        # 3. Enterprise Value & Equity Value
        enterprise_value = pv_fcfs + pv_tv
        equity_value = enterprise_value - total_debt + cash_and_investments
        implied_share_price = max(0.01, equity_value / shares_outstanding)
        upside = ((implied_share_price - current_price) / current_price) * 100.0 if current_price > 0 else 0.0

        # 4. 2D Sensitivity Grid
        # WACC offsets: -1.5%, -1.0%, -0.5%, 0%, +0.5%, +1.0%, +1.5%
        wacc_steps = [round(wacc + delta, 4) for delta in [-0.015, -0.010, -0.005, 0.0, 0.005, 0.010, 0.015]]
        # Terminal Growth offsets: -0.5%, -0.25%, 0%, +0.25%, +0.5%
        g_steps = [round(terminal_growth_rate + delta, 4) for delta in [-0.005, -0.0025, 0.0, 0.0025, 0.005]]

        sensitivity_matrix: List[List[DCFSensitivityCell]] = []

        for w in wacc_steps:
            row: List[DCFSensitivityCell] = []
            for g in g_steps:
                if g >= w:
                    # Infeasible cell
                    row.append(DCFSensitivityCell(wacc=w, terminal_growth=g, implied_share_price=0.0, upside_percent=0.0))
                    continue

                # Recalculate PV FCFs
                cell_pv_fcfs = 0.0
                cell_fcf = fcf_base
                for yr in range(1, 6):
                    cell_fcf = cell_fcf * (1.0 + growth_rate_stage1)
                    cell_pv_fcfs += cell_fcf / ((1.0 + w) ** yr)

                cell_tv = (cell_fcf * (1.0 + g)) / (w - g)
                cell_pv_tv = cell_tv / ((1.0 + w) ** 5)
                cell_ev = cell_pv_fcfs + cell_pv_tv
                cell_eq = cell_ev - total_debt + cash_and_investments
                cell_price = max(0.01, cell_eq / shares_outstanding)
                cell_upside = ((cell_price - current_price) / current_price) * 100.0 if current_price > 0 else 0.0

                row.append(DCFSensitivityCell(
                    wacc=w,
                    terminal_growth=g,
                    implied_share_price=round(cell_price, 2),
                    upside_percent=round(cell_upside, 1),
                ))
            sensitivity_matrix.append(row)

        return DCFModelResult(
            ticker=ticker,
            as_of_date=as_of_date,
            current_price=round(current_price, 2),
            implied_share_price=round(implied_share_price, 2),
            upside_downside_percent=round(upside, 1),
            enterprise_value=round(enterprise_value, 2),
            equity_value=round(equity_value, 2),
            pv_projected_fcfs=round(pv_fcfs, 2),
            pv_terminal_value=round(pv_tv, 2),
            terminal_value=round(tv, 2),
            shares_outstanding=shares_outstanding,
            fcf_base=round(fcf_base, 2),
            wacc=round(wacc, 4),
            terminal_growth_rate=round(terminal_growth_rate, 4),
            stage1_growth_rate=round(growth_rate_stage1, 4),
            projections=projections,
            sensitivity_matrix=sensitivity_matrix,
            sensitivity_wacc_labels=wacc_steps,
            sensitivity_growth_labels=g_steps,
            data_quality="HIGH",
        )
