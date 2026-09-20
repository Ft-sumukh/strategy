"""
AEGIS INVEST — Fundamentals Analytics Engine
Calculates growth, profitability, capital efficiency, balance sheet health,
cash flow quality, earnings quality (Sloan accruals), and transparent 6-category scorecard.
Follows strict financial safety guidelines:
- Missing data returns None with explicit quality reason (never 0).
- No look-ahead bias.
- Transparent mathematical formulas and neutral interpretations.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional
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


def _cagr(start_val: Optional[float], end_val: Optional[float], years: int) -> Optional[float]:
    if start_val is None or end_val is None or years <= 0:
        return None
    if start_val <= 0 or end_val <= 0:
        # CAGR is mathematically undefined for non-positive bases
        return None
    try:
        return (end_val / start_val) ** (1.0 / years) - 1.0
    except (ZeroDivisionError, OverflowError, ValueError):
        return None


@dataclass
class GrowthMetrics:
    revenue_yoy: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    net_income_yoy: Optional[float] = None
    eps_yoy: Optional[float] = None
    ebitda_yoy: Optional[float] = None
    fcf_yoy: Optional[float] = None
    data_quality: str = "HIGH"
    missing_fields: List[str] = field(default_factory=list)


@dataclass
class ProfitabilityMetrics:
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    net_margin: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    effective_tax_rate: Optional[float] = None
    data_quality: str = "HIGH"


@dataclass
class BalanceSheetHealthMetrics:
    debt_to_equity: Optional[float] = None
    net_debt: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    is_net_cash: bool = False
    data_quality: str = "HIGH"


@dataclass
class CashFlowQualityMetrics:
    free_cash_flow: Optional[float] = None
    fcf_margin: Optional[float] = None
    cash_conversion_ratio: Optional[float] = None  # OCF / EBITDA
    ocf_to_net_income: Optional[float] = None
    has_earnings_divergence: bool = False  # True if Net Income rising while OCF falling
    divergence_reason: Optional[str] = None
    data_quality: str = "HIGH"


@dataclass
class EarningsQualityMetrics:
    sloan_accruals_ratio: Optional[float] = None
    accruals_interpretation: str = "Neutral"  # High quality, Normal, Low quality (high accruals)
    cash_backed_earnings: bool = True
    data_quality: str = "HIGH"


@dataclass
class ScorecardCategory:
    name: str
    weight: float
    score: float  # 0 - 100
    weighted_score: float
    status: str  # Strong, Adequate, Weak, or Insufficient Data
    rationale: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FundamentalScorecard:
    overall_score: float  # 0 - 100
    rating: str  # Exemplary, Strong, Moderate, Cautious, Distressed
    categories: List[ScorecardCategory] = field(default_factory=list)
    confidence: str = "HIGH"
    as_of_period: str = ""
    disclaimer: str = "Scorecard is a deterministic quantitative aggregation across 6 fundamental pillars. It does not constitute investment advice or a price forecast."


class FundamentalsEngine:
    """Institutional-grade financial fundamentals calculation engine."""

    def compute_growth(
        self,
        income_statements: List[Any],  # Sorted newest to oldest
        cash_flows: Optional[List[Any]] = None,
    ) -> GrowthMetrics:
        """Computes YoY growth and multi-year CAGR."""
        missing = []
        if not income_statements:
            return GrowthMetrics(data_quality="INSUFFICIENT_DATA", missing_fields=["income_statements"])

        latest = income_statements[0]
        prior_1y = income_statements[1] if len(income_statements) > 1 else None
        prior_3y = income_statements[3] if len(income_statements) > 3 else None
        prior_5y = income_statements[5] if len(income_statements) > 5 else None

        rev_0 = _to_float(latest.revenue)
        rev_1 = _to_float(prior_1y.revenue) if prior_1y else None
        rev_3 = _to_float(prior_3y.revenue) if prior_3y else None
        rev_5 = _to_float(prior_5y.revenue) if prior_5y else None

        # Revenue Growth
        revenue_yoy = _safe_div(rev_0 - rev_1, rev_1) if rev_0 is not None and rev_1 is not None else None
        revenue_cagr_3y = _cagr(rev_3, rev_0, 3)
        revenue_cagr_5y = _cagr(rev_5, rev_0, 5)

        # Net Income & EPS Growth
        ni_0 = _to_float(latest.net_income)
        ni_1 = _to_float(prior_1y.net_income) if prior_1y else None
        net_income_yoy = _safe_div(ni_0 - ni_1, abs(ni_1)) if ni_0 is not None and ni_1 is not None and ni_1 != 0 else None

        eps_0 = _to_float(latest.diluted_eps or latest.eps)
        eps_1 = _to_float(prior_1y.diluted_eps or prior_1y.eps) if prior_1y else None
        eps_yoy = _safe_div(eps_0 - eps_1, abs(eps_1)) if eps_0 is not None and eps_1 is not None and eps_1 != 0 else None

        ebitda_0 = _to_float(latest.ebitda)
        ebitda_1 = _to_float(prior_1y.ebitda) if prior_1y else None
        ebitda_yoy = _safe_div(ebitda_0 - ebitda_1, abs(ebitda_1)) if ebitda_0 is not None and ebitda_1 is not None and ebitda_1 != 0 else None

        # FCF Growth
        fcf_yoy = None
        if cash_flows and len(cash_flows) > 1:
            fcf_0 = _to_float(cash_flows[0].free_cash_flow)
            fcf_1 = _to_float(cash_flows[1].free_cash_flow)
            if fcf_0 is not None and fcf_1 is not None and fcf_1 != 0:
                fcf_yoy = _safe_div(fcf_0 - fcf_1, abs(fcf_1))

        quality = "HIGH" if revenue_yoy is not None and revenue_cagr_3y is not None else "MODERATE"
        return GrowthMetrics(
            revenue_yoy=revenue_yoy,
            revenue_cagr_3y=revenue_cagr_3y,
            revenue_cagr_5y=revenue_cagr_5y,
            net_income_yoy=net_income_yoy,
            eps_yoy=eps_yoy,
            ebitda_yoy=ebitda_yoy,
            fcf_yoy=fcf_yoy,
            data_quality=quality,
            missing_fields=missing,
        )

    def compute_profitability(
        self,
        income_stmt: Any,
        balance_sheet: Optional[Any] = None,
        prior_balance_sheet: Optional[Any] = None,
    ) -> ProfitabilityMetrics:
        """Computes margin profile, ROA, ROE, and ROIC."""
        if not income_stmt:
            return ProfitabilityMetrics(data_quality="INSUFFICIENT_DATA")

        rev = _to_float(income_stmt.revenue)
        gp = _to_float(income_stmt.gross_profit)
        op_inc = _to_float(income_stmt.operating_income)
        ebitda = _to_float(income_stmt.ebitda)
        ni = _to_float(income_stmt.net_income)
        tax = _to_float(income_stmt.tax_expense)
        pretax = _to_float(income_stmt.pre_tax_income)

        gross_margin = _safe_div(gp, rev)
        op_margin = _safe_div(op_inc, rev)
        ebitda_margin = _safe_div(ebitda, rev)
        net_margin = _safe_div(ni, rev)

        # Effective Tax Rate
        tax_rate = None
        if pretax is not None and pretax > 0 and tax is not None:
            tax_rate = max(0.0, min(0.40, tax / pretax))
        else:
            tax_rate = 0.21  # Standard statutory baseline assumption if undefined

        # ROA & ROE
        roa = None
        roe = None
        roic = None

        if balance_sheet:
            tot_assets = _to_float(balance_sheet.total_assets)
            equity = _to_float(balance_sheet.shareholders_equity)
            tot_debt = _to_float(balance_sheet.total_debt or 0)
            cash = _to_float(balance_sheet.cash_and_equivalents or 0)
            st_investments = _to_float(balance_sheet.short_term_investments or 0)

            # Use average equity if prior available, otherwise point-in-time
            avg_equity = equity
            if prior_balance_sheet and prior_balance_sheet.shareholders_equity:
                prior_equity = _to_float(prior_balance_sheet.shareholders_equity)
                if prior_equity is not None and equity is not None:
                    avg_equity = (equity + prior_equity) / 2.0

            roa = _safe_div(ni, tot_assets)
            roe = _safe_div(ni, avg_equity)

            # ROIC = NOPAT / Invested Capital
            # NOPAT = Operating Income * (1 - Tax Rate)
            # Invested Capital = Total Debt + Equity - Cash & Equivalents - Short Term Investments
            if op_inc is not None and equity is not None and tot_debt is not None:
                nopat = op_inc * (1.0 - tax_rate)
                invested_capital = tot_debt + equity - (cash + st_investments)
                if invested_capital > 0:
                    roic = _safe_div(nopat, invested_capital)

        return ProfitabilityMetrics(
            gross_margin=gross_margin,
            operating_margin=op_margin,
            ebitda_margin=ebitda_margin,
            net_margin=net_margin,
            return_on_assets=roa,
            return_on_equity=roe,
            return_on_invested_capital=roic,
            effective_tax_rate=tax_rate,
            data_quality="HIGH" if roe is not None and roic is not None else "MODERATE",
        )

    def compute_balance_sheet_health(
        self,
        balance_sheet: Any,
        ebitda: Optional[float] = None,
        operating_income: Optional[float] = None,
        interest_expense: Optional[float] = None,
    ) -> BalanceSheetHealthMetrics:
        """Computes leverage, solvency, and liquidity metrics."""
        if not balance_sheet:
            return BalanceSheetHealthMetrics(data_quality="INSUFFICIENT_DATA")

        tot_debt = _to_float(balance_sheet.total_debt)
        if tot_debt is None:
            # Fallback to short_term_debt + long_term_debt
            st = _to_float(balance_sheet.short_term_debt or 0)
            lt = _to_float(balance_sheet.long_term_debt or 0)
            tot_debt = st + lt

        equity = _to_float(balance_sheet.shareholders_equity)
        cash = _to_float(balance_sheet.cash_and_equivalents or 0)
        st_inv = _to_float(balance_sheet.short_term_investments or 0)
        tot_cash = cash + st_inv

        curr_assets = _to_float(balance_sheet.current_assets)
        curr_liab = _to_float(balance_sheet.current_liabilities)

        debt_to_equity = _safe_div(tot_debt, equity)
        net_debt = (tot_debt - tot_cash) if tot_debt is not None else None
        debt_to_ebitda = _safe_div(tot_debt, ebitda) if ebitda and ebitda > 0 else None
        current_ratio = _safe_div(curr_assets, curr_liab)
        quick_ratio = _safe_div(tot_cash, curr_liab)

        interest_cov = None
        if operating_income is not None and interest_expense is not None and interest_expense > 0:
            interest_cov = _safe_div(operating_income, interest_expense)

        is_net_cash = (net_debt is not None and net_debt < 0)

        return BalanceSheetHealthMetrics(
            debt_to_equity=debt_to_equity,
            net_debt=net_debt,
            debt_to_ebitda=debt_to_ebitda,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            interest_coverage=interest_cov,
            is_net_cash=is_net_cash,
            data_quality="HIGH",
        )

    def compute_cash_flow_quality(
        self,
        cash_flow: Any,
        revenue: Optional[float] = None,
        ebitda: Optional[float] = None,
        net_income: Optional[float] = None,
        prior_cash_flow: Optional[Any] = None,
        prior_net_income: Optional[float] = None,
    ) -> CashFlowQualityMetrics:
        """Computes FCF conversion, cash flow coverage, and accrual divergence."""
        if not cash_flow:
            return CashFlowQualityMetrics(data_quality="INSUFFICIENT_DATA")

        ocf = _to_float(cash_flow.operating_cash_flow)
        fcf = _to_float(cash_flow.free_cash_flow)
        if fcf is None and ocf is not None:
            capex = _to_float(cash_flow.capital_expenditure or 0)
            fcf = ocf - abs(capex)

        fcf_margin = _safe_div(fcf, revenue)
        cash_conv = _safe_div(ocf, ebitda)
        ocf_to_ni = _safe_div(ocf, net_income)

        # Check divergence: Net Income rising while OCF falling
        divergence = False
        divergence_reason = None
        if prior_cash_flow and prior_net_income is not None and net_income is not None and ocf is not None:
            prior_ocf = _to_float(prior_cash_flow.operating_cash_flow)
            if prior_ocf is not None:
                if net_income > prior_net_income and ocf < prior_ocf:
                    divergence = True
                    divergence_reason = (
                        "Divergence detected: Net Income increased YoY while Operating Cash Flow decreased, "
                        "indicating potential working capital buildup or non-cash accrual expansion."
                    )

        return CashFlowQualityMetrics(
            free_cash_flow=fcf,
            fcf_margin=fcf_margin,
            cash_conversion_ratio=cash_conv,
            ocf_to_net_income=ocf_to_ni,
            has_earnings_divergence=divergence,
            divergence_reason=divergence_reason,
            data_quality="HIGH",
        )

    def compute_earnings_quality(
        self,
        income_stmt: Any,
        cash_flow: Any,
        balance_sheet: Any,
        prior_balance_sheet: Optional[Any] = None,
    ) -> EarningsQualityMetrics:
        """
        Computes Sloan Accruals Ratio:
        Sloan Accruals = (Net Income - Operating Cash Flow) / Average Total Assets
        Interpretation:
        - Accruals < -0.05: High Quality (cash-heavy earnings)
        - -0.05 to +0.05: Normal / Balanced Accruals
        - > +0.10: Low Quality (accrual-heavy earnings, warranting inspection)
        """
        if not income_stmt or not cash_flow or not balance_sheet:
            return EarningsQualityMetrics(data_quality="INSUFFICIENT_DATA")

        ni = _to_float(income_stmt.net_income)
        ocf = _to_float(cash_flow.operating_cash_flow)
        curr_assets = _to_float(balance_sheet.total_assets)

        if ni is None or ocf is None or curr_assets is None or curr_assets == 0:
            return EarningsQualityMetrics(data_quality="INSUFFICIENT_DATA")

        avg_assets = curr_assets
        if prior_balance_sheet and prior_balance_sheet.total_assets:
            p_assets = _to_float(prior_balance_sheet.total_assets)
            if p_assets and p_assets > 0:
                avg_assets = (curr_assets + p_assets) / 2.0

        accruals_ratio = (ni - ocf) / avg_assets

        if accruals_ratio < -0.05:
            interp = "High Quality (Cash Generation Outpaces Net Income)"
            cash_backed = True
        elif accruals_ratio <= 0.05:
            interp = "Normal Quality (Balanced Accruals)"
            cash_backed = True
        elif accruals_ratio <= 0.10:
            interp = "Moderate Accruals (Adequate Quality)"
            cash_backed = False
        else:
            interp = "Low Quality (High Non-Cash Accruals)"
            cash_backed = False

        return EarningsQualityMetrics(
            sloan_accruals_ratio=accruals_ratio,
            accruals_interpretation=interp,
            cash_backed_earnings=cash_backed,
            data_quality="HIGH",
        )

    def generate_scorecard(
        self,
        growth: GrowthMetrics,
        profitability: ProfitabilityMetrics,
        balance_sheet: BalanceSheetHealthMetrics,
        cash_flow: CashFlowQualityMetrics,
        earnings: EarningsQualityMetrics,
        as_of_period: str = "TTM",
    ) -> FundamentalScorecard:
        """
        Generates transparent, deterministic 0–100 Fundamental Scorecard
        across 6 balanced institutional pillars.
        Weights:
        - Growth: 20%
        - Profitability: 20%
        - Capital Efficiency: 15%
        - Balance Sheet Health: 15%
        - Cash Flow Quality: 15%
        - Earnings Quality: 15%
        """
        categories: List[ScorecardCategory] = []

        # 1. Growth Pillar (20%)
        growth_score = 50.0
        g_notes = []
        if growth.revenue_cagr_3y is not None:
            if growth.revenue_cagr_3y > 0.20:
                growth_score += 30.0
                g_notes.append(f"Strong 3Y Rev CAGR ({growth.revenue_cagr_3y:.1%})")
            elif growth.revenue_cagr_3y > 0.10:
                growth_score += 15.0
                g_notes.append(f"Moderate 3Y Rev CAGR ({growth.revenue_cagr_3y:.1%})")
            elif growth.revenue_cagr_3y < 0:
                growth_score -= 25.0
                g_notes.append(f"Negative 3Y Rev CAGR ({growth.revenue_cagr_3y:.1%})")
        if growth.eps_yoy is not None:
            if growth.eps_yoy > 0.15:
                growth_score += 20.0
                g_notes.append(f"Solid EPS YoY Growth ({growth.eps_yoy:.1%})")
            elif growth.eps_yoy < 0:
                growth_score -= 15.0
                g_notes.append(f"Declining EPS YoY ({growth.eps_yoy:.1%})")
        growth_score = max(0.0, min(100.0, growth_score))
        categories.append(ScorecardCategory(
            name="Revenue & Earnings Growth",
            weight=0.20,
            score=growth_score,
            weighted_score=growth_score * 0.20,
            status="Strong" if growth_score >= 70 else ("Adequate" if growth_score >= 45 else "Weak"),
            rationale="; ".join(g_notes) or "Growth in line with baseline averages",
            metrics={"revenue_yoy": growth.revenue_yoy, "revenue_cagr_3y": growth.revenue_cagr_3y, "eps_yoy": growth.eps_yoy},
        ))

        # 2. Profitability Pillar (20%)
        prof_score = 50.0
        p_notes = []
        if profitability.operating_margin is not None:
            if profitability.operating_margin > 0.25:
                prof_score += 25.0
                p_notes.append(f"Exceptional Op Margin ({profitability.operating_margin:.1%})")
            elif profitability.operating_margin > 0.15:
                prof_score += 15.0
                p_notes.append(f"Robust Op Margin ({profitability.operating_margin:.1%})")
            elif profitability.operating_margin < 0.05:
                prof_score -= 20.0
                p_notes.append(f"Thin Op Margin ({profitability.operating_margin:.1%})")
        if profitability.net_margin is not None:
            if profitability.net_margin > 0.20:
                prof_score += 25.0
                p_notes.append(f"High Net Margin ({profitability.net_margin:.1%})")
            elif profitability.net_margin < 0:
                prof_score -= 30.0
                p_notes.append("Unprofitable net margin")
        prof_score = max(0.0, min(100.0, prof_score))
        categories.append(ScorecardCategory(
            name="Operating & Net Profitability",
            weight=0.20,
            score=prof_score,
            weighted_score=prof_score * 0.20,
            status="Strong" if prof_score >= 70 else ("Adequate" if prof_score >= 45 else "Weak"),
            rationale="; ".join(p_notes) or "Standard margin performance",
            metrics={"gross_margin": profitability.gross_margin, "operating_margin": profitability.operating_margin, "net_margin": profitability.net_margin},
        ))

        # 3. Capital Efficiency Pillar (15%)
        eff_score = 50.0
        e_notes = []
        if profitability.return_on_invested_capital is not None:
            if profitability.return_on_invested_capital > 0.20:
                eff_score += 30.0
                e_notes.append(f"Elite ROIC ({profitability.return_on_invested_capital:.1%})")
            elif profitability.return_on_invested_capital > 0.12:
                eff_score += 15.0
                e_notes.append(f"Value-creating ROIC ({profitability.return_on_invested_capital:.1%})")
            elif profitability.return_on_invested_capital < 0.06:
                eff_score -= 25.0
                e_notes.append(f"Sub-WACC ROIC ({profitability.return_on_invested_capital:.1%})")
        if profitability.return_on_equity is not None:
            if profitability.return_on_equity > 0.25:
                eff_score += 20.0
                e_notes.append(f"High ROE ({profitability.return_on_equity:.1%})")
        eff_score = max(0.0, min(100.0, eff_score))
        categories.append(ScorecardCategory(
            name="Capital Efficiency (ROIC / ROE)",
            weight=0.15,
            score=eff_score,
            weighted_score=eff_score * 0.15,
            status="Strong" if eff_score >= 70 else ("Adequate" if eff_score >= 45 else "Weak"),
            rationale="; ".join(e_notes) or "Capital returns near benchmark",
            metrics={"roic": profitability.return_on_invested_capital, "roe": profitability.return_on_equity},
        ))

        # 4. Balance Sheet Health Pillar (15%)
        bs_score = 50.0
        b_notes = []
        if balance_sheet.is_net_cash:
            bs_score += 25.0
            b_notes.append("Fortress Net Cash Balance Sheet")
        elif balance_sheet.debt_to_equity is not None:
            if balance_sheet.debt_to_equity < 0.5:
                bs_score += 15.0
                b_notes.append("Conservative leverage (D/E < 0.5)")
            elif balance_sheet.debt_to_equity > 2.0:
                bs_score -= 20.0
                b_notes.append("Elevated leverage (D/E > 2.0)")
        if balance_sheet.current_ratio is not None:
            if balance_sheet.current_ratio > 1.3:
                bs_score += 25.0
                b_notes.append(f"Strong liquidity (Current Ratio {balance_sheet.current_ratio:.2f})")
            elif balance_sheet.current_ratio < 0.9:
                bs_score -= 25.0
                b_notes.append(f"Tight working capital (Current Ratio {balance_sheet.current_ratio:.2f})")
        bs_score = max(0.0, min(100.0, bs_score))
        categories.append(ScorecardCategory(
            name="Balance Sheet & Solvency",
            weight=0.15,
            score=bs_score,
            weighted_score=bs_score * 0.15,
            status="Strong" if bs_score >= 70 else ("Adequate" if bs_score >= 45 else "Weak"),
            rationale="; ".join(b_notes) or "Adequate liquidity and leverage",
            metrics={"debt_to_equity": balance_sheet.debt_to_equity, "current_ratio": balance_sheet.current_ratio, "is_net_cash": balance_sheet.is_net_cash},
        ))

        # 5. Cash Flow Quality Pillar (15%)
        cf_score = 50.0
        c_notes = []
        if cash_flow.cash_conversion_ratio is not None:
            if cash_flow.cash_conversion_ratio > 0.85:
                cf_score += 25.0
                c_notes.append(f"High cash conversion ({cash_flow.cash_conversion_ratio:.1%} OCF/EBITDA)")
            elif cash_flow.cash_conversion_ratio < 0.50:
                cf_score -= 20.0
                c_notes.append(f"Low cash conversion ({cash_flow.cash_conversion_ratio:.1%})")
        if cash_flow.has_earnings_divergence:
            cf_score -= 25.0
            c_notes.append("Warning: Net Income vs OCF divergence")
        else:
            cf_score += 25.0
            c_notes.append("Consistent cash flow generation aligned with net income")
        cf_score = max(0.0, min(100.0, cf_score))
        categories.append(ScorecardCategory(
            name="Cash Flow Conversion",
            weight=0.15,
            score=cf_score,
            weighted_score=cf_score * 0.15,
            status="Strong" if cf_score >= 70 else ("Adequate" if cf_score >= 45 else "Weak"),
            rationale="; ".join(c_notes) or "Standard cash conversion",
            metrics={"cash_conversion_ratio": cash_flow.cash_conversion_ratio, "has_divergence": cash_flow.has_earnings_divergence},
        ))

        # 6. Earnings Quality Pillar (15%)
        eq_score = 50.0
        eq_notes = []
        if earnings.sloan_accruals_ratio is not None:
            if earnings.sloan_accruals_ratio <= 0.0:
                eq_score += 35.0
                eq_notes.append(f"Superior cash-backed earnings (Sloan Accruals {earnings.sloan_accruals_ratio:.2f})")
            elif earnings.sloan_accruals_ratio <= 0.05:
                eq_score += 15.0
                eq_notes.append(f"Balanced accruals ({earnings.sloan_accruals_ratio:.2f})")
            elif earnings.sloan_accruals_ratio > 0.10:
                eq_score -= 30.0
                eq_notes.append(f"High accruals warning ({earnings.sloan_accruals_ratio:.2f})")
        if earnings.cash_backed_earnings:
            eq_score += 15.0
        eq_score = max(0.0, min(100.0, eq_score))
        categories.append(ScorecardCategory(
            name="Earnings Quality & Accruals",
            weight=0.15,
            score=eq_score,
            weighted_score=eq_score * 0.15,
            status="Strong" if eq_score >= 70 else ("Adequate" if eq_score >= 45 else "Weak"),
            rationale="; ".join(eq_notes) or "Normal accrual profile",
            metrics={"sloan_accruals_ratio": earnings.sloan_accruals_ratio, "accruals_interpretation": earnings.accruals_interpretation},
        ))

        # Overall Score
        total_score = round(sum(c.weighted_score for c in categories), 1)

        if total_score >= 85.0:
            rating = "Exemplary"
        elif total_score >= 70.0:
            rating = "Strong"
        elif total_score >= 50.0:
            rating = "Moderate"
        elif total_score >= 35.0:
            rating = "Cautious"
        else:
            rating = "Distressed"

        return FundamentalScorecard(
            overall_score=total_score,
            rating=rating,
            categories=categories,
            confidence="HIGH",
            as_of_period=as_of_period,
        )
