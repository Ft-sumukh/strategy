"""
AEGIS INVEST — Financial Schemas (Pydantic v2)
Strongly typed models for fundamentals, valuation, technical analysis,
quantitative factors, company intelligence, and stock screener.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Statements
# ---------------------------------------------------------
class IncomeStatementResponse(BaseModel):
    ticker: str
    period: str
    period_type: str
    filing_date: Optional[date] = None
    currency: str = "USD"
    revenue: Optional[Decimal] = None
    cost_of_revenue: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    operating_expenses: Optional[Decimal] = None
    operating_income: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    ebit: Optional[Decimal] = None
    interest_expense: Optional[Decimal] = None
    pre_tax_income: Optional[Decimal] = None
    tax_expense: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    diluted_eps: Optional[Decimal] = None
    source: str = "SEC_EDGAR"
    quality_status: str = "AUDITED"
    is_synthetic: bool = False


class BalanceSheetResponse(BaseModel):
    ticker: str
    period: str
    period_type: str
    filing_date: Optional[date] = None
    currency: str = "USD"
    cash_and_equivalents: Optional[Decimal] = None
    short_term_investments: Optional[Decimal] = None
    current_assets: Optional[Decimal] = None
    goodwill: Optional[Decimal] = None
    intangible_assets: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    current_liabilities: Optional[Decimal] = None
    short_term_debt: Optional[Decimal] = None
    long_term_debt: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    shareholders_equity: Optional[Decimal] = None
    source: str = "SEC_EDGAR"
    quality_status: str = "AUDITED"
    is_synthetic: bool = False


class CashFlowStatementResponse(BaseModel):
    ticker: str
    period: str
    period_type: str
    filing_date: Optional[date] = None
    currency: str = "USD"
    operating_cash_flow: Optional[Decimal] = None
    capital_expenditure: Optional[Decimal] = None
    investing_cash_flow: Optional[Decimal] = None
    financing_cash_flow: Optional[Decimal] = None
    free_cash_flow: Optional[Decimal] = None
    source: str = "SEC_EDGAR"
    quality_status: str = "AUDITED"
    is_synthetic: bool = False


# ---------------------------------------------------------
# Fundamentals Analytics
# ---------------------------------------------------------
class GrowthMetricsSchema(BaseModel):
    revenue_yoy: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    revenue_cagr_5y: Optional[float] = None
    net_income_yoy: Optional[float] = None
    eps_yoy: Optional[float] = None
    ebitda_yoy: Optional[float] = None
    fcf_yoy: Optional[float] = None
    data_quality: str = "HIGH"
    missing_fields: List[str] = Field(default_factory=list)


class ProfitabilityMetricsSchema(BaseModel):
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    net_margin: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    effective_tax_rate: Optional[float] = None
    data_quality: str = "HIGH"


class BalanceSheetHealthSchema(BaseModel):
    debt_to_equity: Optional[float] = None
    net_debt: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None
    is_net_cash: bool = False
    data_quality: str = "HIGH"


class CashFlowQualitySchema(BaseModel):
    free_cash_flow: Optional[float] = None
    fcf_margin: Optional[float] = None
    cash_conversion_ratio: Optional[float] = None
    ocf_to_net_income: Optional[float] = None
    has_earnings_divergence: bool = False
    divergence_reason: Optional[str] = None
    data_quality: str = "HIGH"


class EarningsQualitySchema(BaseModel):
    sloan_accruals_ratio: Optional[float] = None
    accruals_interpretation: str = "Neutral"
    cash_backed_earnings: bool = True
    data_quality: str = "HIGH"


class ScorecardCategorySchema(BaseModel):
    name: str
    weight: float
    score: float
    weighted_score: float
    status: str
    rationale: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class FundamentalScorecardSchema(BaseModel):
    overall_score: float
    rating: str
    categories: List[ScorecardCategorySchema] = Field(default_factory=list)
    confidence: str = "HIGH"
    as_of_period: str = "TTM"
    disclaimer: str = ""


class FullFundamentalsResponse(BaseModel):
    ticker: str
    as_of_period: str = "TTM"
    growth: GrowthMetricsSchema
    profitability: ProfitabilityMetricsSchema
    balance_sheet_health: BalanceSheetHealthSchema
    cash_flow_quality: CashFlowQualitySchema
    earnings_quality: EarningsQualitySchema
    scorecard: FundamentalScorecardSchema
    income_statements: List[IncomeStatementResponse] = Field(default_factory=list)
    balance_sheets: List[BalanceSheetResponse] = Field(default_factory=list)
    cash_flows: List[CashFlowStatementResponse] = Field(default_factory=list)
    data_source: str = "SEC_EDGAR_DEMO"
    is_synthetic: bool = True


# ---------------------------------------------------------
# Valuation Analytics
# ---------------------------------------------------------
class ValuationMultiplesSchema(BaseModel):
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


class MultipleHistoricalContextSchema(BaseModel):
    metric_name: str
    current_value: Optional[float] = None
    median_1y: Optional[float] = None
    median_3y: Optional[float] = None
    median_5y: Optional[float] = None
    percentile_3y: Optional[float] = None
    min_3y: Optional[float] = None
    max_3y: Optional[float] = None
    interpretation: str = "Neutral"


class PeerValuationRowSchema(BaseModel):
    ticker: str
    name: str
    price: float
    market_cap: float
    pe_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    ps_ratio: Optional[float] = None
    fcf_yield: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None


class DCFYearProjectionSchema(BaseModel):
    year: int
    projected_fcf: float
    discount_factor: float
    pv_fcf: float


class DCFSensitivityCellSchema(BaseModel):
    wacc: float
    terminal_growth: float
    implied_share_price: float
    upside_percent: float


class DCFModelResultSchema(BaseModel):
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
    projections: List[DCFYearProjectionSchema] = Field(default_factory=list)
    sensitivity_matrix: List[List[DCFSensitivityCellSchema]] = Field(default_factory=list)
    sensitivity_wacc_labels: List[float] = Field(default_factory=list)
    sensitivity_growth_labels: List[float] = Field(default_factory=list)
    data_quality: str = "HIGH"
    disclaimer: str = ""


class DCFCalculationRequest(BaseModel):
    wacc: Optional[float] = Field(default=0.09, ge=0.04, le=0.25)
    terminal_growth_rate: Optional[float] = Field(default=0.025, ge=0.00, le=0.06)
    growth_rate_stage1: Optional[float] = Field(default=0.10, ge=-0.50, le=1.0)


class FullValuationResponse(BaseModel):
    ticker: str
    current_price: float
    multiples: ValuationMultiplesSchema
    historical_context: List[MultipleHistoricalContextSchema] = Field(default_factory=list)
    peers: List[PeerValuationRowSchema] = Field(default_factory=list)
    dcf: DCFModelResultSchema
    data_source: str = "AEGIS_VALUATION_ENGINE"


# ---------------------------------------------------------
# Technical Analysis
# ---------------------------------------------------------
class MovingAveragesSchema(BaseModel):
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_100: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None


class RSIIndicatorSchema(BaseModel):
    rsi_14: Optional[float] = None
    status: str = "NEUTRAL"
    interpretation: str = ""


class MACDIndicatorSchema(BaseModel):
    macd_line: Optional[float] = None
    signal_line: Optional[float] = None
    histogram: Optional[float] = None
    status: str = "NEUTRAL"


class BollingerBandsSchema(BaseModel):
    upper_band: Optional[float] = None
    middle_band: Optional[float] = None
    lower_band: Optional[float] = None
    bandwidth: Optional[float] = None
    percent_b: Optional[float] = None


class VolatilityAndTrendSchema(BaseModel):
    atr_14: Optional[float] = None
    adx_14: Optional[float] = None
    trend_strength: str = "WEAK"
    volatility_20d: Optional[float] = None
    volatility_60d: Optional[float] = None
    volatility_252d: Optional[float] = None


class MomentumMetricsSchema(BaseModel):
    return_1m: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_1y: Optional[float] = None
    roc_14: Optional[float] = None


class TechnicalSignalSchema(BaseModel):
    indicator: str
    value: float
    benchmark_threshold: str
    signal: str
    rationale: str
    timestamp: str


class FullTechnicalsResponse(BaseModel):
    ticker: str
    as_of_date: str
    latest_close: float
    moving_averages: MovingAveragesSchema
    rsi: RSIIndicatorSchema
    macd: MACDIndicatorSchema
    bollinger: BollingerBandsSchema
    volatility_and_trend: VolatilityAndTrendSchema
    momentum: MomentumMetricsSchema
    signals: List[TechnicalSignalSchema] = Field(default_factory=list)
    overall_sentiment: str = "NEUTRAL"
    data_quality: str = "HIGH"


# ---------------------------------------------------------
# Factors
# ---------------------------------------------------------
class FactorScoreSchema(BaseModel):
    factor_name: str
    composite_score: float
    z_score: float
    percentile: float
    exposure: str
    raw_metrics: Dict[str, Any] = Field(default_factory=dict)
    data_quality: str = "HIGH"
    description: str = ""


class FullFactorsResponse(BaseModel):
    ticker: str
    as_of_date: str
    factors: Dict[str, FactorScoreSchema] = Field(default_factory=dict)
    summary_radar: Dict[str, float] = Field(default_factory=dict)
    data_quality: str = "HIGH"
    disclaimer: str = ""


# ---------------------------------------------------------
# Consolidated Company Intelligence
# ---------------------------------------------------------
class CompanyProfileSchema(BaseModel):
    ticker: str
    name: str
    exchange: str
    sector: str
    industry: str
    country: str = "USA"
    currency: str = "USD"
    description: Optional[str] = None
    website: Optional[str] = None
    market_cap: Optional[Decimal] = None
    shares_outstanding: Optional[Decimal] = None
    status: str = "ACTIVE"
    is_synthetic: bool = False


class CompanyIntelligenceResponse(BaseModel):
    ticker: str
    profile: CompanyProfileSchema
    current_price: float
    price_change_24h: float
    price_change_percent_24h: float
    fundamentals_summary: FundamentalScorecardSchema
    valuation_summary: ValuationMultiplesSchema
    technicals_summary: FullTechnicalsResponse
    factors_summary: FullFactorsResponse
    data_provenance: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------
# Stock Screener
# ---------------------------------------------------------
class ScreenerStockItem(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: float
    price: float
    pe_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    fcf_yield: Optional[float] = None
    revenue_cagr_3y: Optional[float] = None
    roe: Optional[float] = None
    scorecard_score: Optional[float] = None
    rsi_14: Optional[float] = None
    overall_sentiment: str = "NEUTRAL"
    momentum_factor: Optional[float] = None
    quality_factor: Optional[float] = None


class ScreenerResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[ScreenerStockItem] = Field(default_factory=list)
    applied_filters: Dict[str, Any] = Field(default_factory=dict)
