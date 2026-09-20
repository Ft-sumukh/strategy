"""
AEGIS INVEST — Financial Intelligence Domain Service
Orchestrates fundamental, valuation, technical, factor, and screener analysis
by bridging database models, external data providers, and institutional analytics engines.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.factors.engine import FactorsEngine, MultiFactorProfile
from app.analytics.fundamentals.engine import (
    BalanceSheetHealthMetrics,
    CashFlowQualityMetrics,
    EarningsQualityMetrics,
    FundamentalScorecard,
    FundamentalsEngine,
    GrowthMetrics,
    ProfitabilityMetrics,
)
from app.analytics.technicals.engine import TechnicalAnalysisResult, TechnicalEngine
from app.analytics.valuation.engine import (
    DCFModelResult,
    MultipleHistoricalContext,
    PeerValuationRow,
    ValuationEngine,
    ValuationMultiples,
)
from app.core.exceptions import EntityNotFoundException
from app.models.financials import BalanceSheet, CashFlowStatement, Company, IncomeStatement, MarketPriceBar
from app.repositories.financial_repository import FinancialRepository
from app.schemas.financials import (
    BalanceSheetHealthSchema,
    BalanceSheetResponse,
    CashFlowQualitySchema,
    CashFlowStatementResponse,
    CompanyIntelligenceResponse,
    CompanyProfileSchema,
    DCFCalculationRequest,
    DCFModelResultSchema,
    DCFSensitivityCellSchema,
    DCFYearProjectionSchema,
    EarningsQualitySchema,
    FactorScoreSchema,
    FullFactorsResponse,
    FullFundamentalsResponse,
    FullTechnicalsResponse,
    FullValuationResponse,
    FundamentalScorecardSchema,
    GrowthMetricsSchema,
    IncomeStatementResponse,
    MultipleHistoricalContextSchema,
    PeerValuationRowSchema,
    ProfitabilityMetricsSchema,
    ScorecardCategorySchema,
    ScreenerResponse,
    ScreenerStockItem,
    TechnicalSignalSchema,
    ValuationMultiplesSchema,
)
from app.services.base import BaseService
from app.services.fundamental_provider import get_fundamental_data_provider


class FinancialIntelligenceService(BaseService):
    """Domain service powering the Aegis Financial Intelligence Engine."""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.repo = FinancialRepository(session)
        self.fundamentals_engine = FundamentalsEngine()
        self.valuation_engine = ValuationEngine()
        self.technical_engine = TechnicalEngine()
        self.factors_engine = FactorsEngine()
        self.provider = get_fundamental_data_provider()

    async def get_company(self, ticker: str) -> Company:
        company = await self.repo.get_company_by_ticker(ticker)
        if not company:
            # Check provider fallback
            prof = self.provider.get_company_profile(ticker)
            if prof:
                return Company(
                    ticker=prof.ticker,
                    name=prof.name,
                    exchange=prof.exchange,
                    sector=prof.sector,
                    industry=prof.industry,
                    country=prof.country,
                    currency=prof.currency,
                    description=prof.description,
                    website=prof.website,
                    market_cap=prof.market_cap,
                    shares_outstanding=prof.shares_outstanding,
                    status=prof.status,
                    is_synthetic=True,
                )
            raise EntityNotFoundException("Company", ticker.upper())
        return company

    async def get_fundamentals(self, ticker: str) -> FullFundamentalsResponse:
        ticker = ticker.upper()
        await self.get_company(ticker)

        # Retrieve statements (sorted descending by period/filing)
        inc_stmts = await self.repo.get_income_statements(ticker, limit=10)
        bs_stmts = await self.repo.get_balance_sheets(ticker, limit=10)
        cf_stmts = await self.repo.get_cash_flows(ticker, limit=10)

        # Provider fallback if DB has not yet been seeded
        if not inc_stmts:
            inc_stmts = self.provider.get_income_statements(ticker)
        if not bs_stmts:
            bs_stmts = self.provider.get_balance_sheets(ticker)
        if not cf_stmts:
            cf_stmts = self.provider.get_cash_flow_statements(ticker)

        latest_inc = inc_stmts[0] if inc_stmts else None
        prior_inc = inc_stmts[1] if len(inc_stmts) > 1 else None
        latest_bs = bs_stmts[0] if bs_stmts else None
        prior_bs = bs_stmts[1] if len(bs_stmts) > 1 else None
        latest_cf = cf_stmts[0] if cf_stmts else None
        prior_cf = cf_stmts[1] if len(cf_stmts) > 1 else None

        # 1. Growth
        growth = self.fundamentals_engine.compute_growth(inc_stmts, cf_stmts)

        # 2. Profitability
        prof = self.fundamentals_engine.compute_profitability(latest_inc, latest_bs, prior_bs)

        # 3. Balance Sheet Health
        ebitda_val = float(latest_inc.ebitda) if latest_inc and latest_inc.ebitda else None
        op_inc_val = float(latest_inc.operating_income) if latest_inc and latest_inc.operating_income else None
        int_exp_val = float(latest_inc.interest_expense) if latest_inc and latest_inc.interest_expense else None
        bs_health = self.fundamentals_engine.compute_balance_sheet_health(
            latest_bs, ebitda=ebitda_val, operating_income=op_inc_val, interest_expense=int_exp_val
        )

        # 4. Cash Flow Quality
        rev_val = float(latest_inc.revenue) if latest_inc and latest_inc.revenue else None
        ni_val = float(latest_inc.net_income) if latest_inc and latest_inc.net_income else None
        p_ni_val = float(prior_inc.net_income) if prior_inc and prior_inc.net_income else None
        cf_quality = self.fundamentals_engine.compute_cash_flow_quality(
            latest_cf, revenue=rev_val, ebitda=ebitda_val, net_income=ni_val, prior_cash_flow=prior_cf, prior_net_income=p_ni_val
        )

        # 5. Earnings Quality (Sloan Accruals)
        eq = self.fundamentals_engine.compute_earnings_quality(latest_inc, latest_cf, latest_bs, prior_bs)

        # 6. Scorecard
        scorecard = self.fundamentals_engine.generate_scorecard(growth, prof, bs_health, cf_quality, eq)

        # Format statement lists
        def _to_inc_resp(s: Any) -> IncomeStatementResponse:
            return IncomeStatementResponse(
                ticker=s.ticker, period=s.period, period_type=s.period_type,
                filing_date=s.filing_date, currency=s.currency,
                revenue=s.revenue, cost_of_revenue=s.cost_of_revenue,
                gross_profit=s.gross_profit, operating_expenses=s.operating_expenses,
                operating_income=s.operating_income, ebitda=s.ebitda, ebit=s.ebit,
                interest_expense=s.interest_expense, pre_tax_income=s.pre_tax_income,
                tax_expense=s.tax_expense, net_income=s.net_income,
                eps=s.eps, diluted_eps=s.diluted_eps, source=s.source,
                quality_status=s.quality_status, is_synthetic=True,
            )

        def _to_bs_resp(b: Any) -> BalanceSheetResponse:
            return BalanceSheetResponse(
                ticker=b.ticker, period=b.period, period_type=b.period_type,
                filing_date=b.filing_date, currency=b.currency,
                cash_and_equivalents=b.cash_and_equivalents,
                short_term_investments=b.short_term_investments,
                current_assets=b.current_assets, goodwill=b.goodwill,
                intangible_assets=b.intangible_assets, total_assets=b.total_assets,
                current_liabilities=b.current_liabilities, short_term_debt=b.short_term_debt,
                long_term_debt=b.long_term_debt, total_debt=b.total_debt,
                total_liabilities=b.total_liabilities, shareholders_equity=b.shareholders_equity,
                source=b.source, quality_status=b.quality_status, is_synthetic=True,
            )

        def _to_cf_resp(c: Any) -> CashFlowStatementResponse:
            return CashFlowStatementResponse(
                ticker=c.ticker, period=c.period, period_type=c.period_type,
                filing_date=c.filing_date, currency=c.currency,
                operating_cash_flow=c.operating_cash_flow,
                capital_expenditure=c.capital_expenditure,
                investing_cash_flow=c.investing_cash_flow,
                financing_cash_flow=c.financing_cash_flow,
                free_cash_flow=c.free_cash_flow, source=c.source,
                quality_status=c.quality_status, is_synthetic=True,
            )

        return FullFundamentalsResponse(
            ticker=ticker,
            as_of_period="2025 / TTM",
            growth=GrowthMetricsSchema(**growth.__dict__),
            profitability=ProfitabilityMetricsSchema(**prof.__dict__),
            balance_sheet_health=BalanceSheetHealthSchema(**bs_health.__dict__),
            cash_flow_quality=CashFlowQualitySchema(**cf_quality.__dict__),
            earnings_quality=EarningsQualitySchema(**eq.__dict__),
            scorecard=FundamentalScorecardSchema(
                overall_score=scorecard.overall_score,
                rating=scorecard.rating,
                categories=[ScorecardCategorySchema(**cat.__dict__) for cat in scorecard.categories],
                confidence=scorecard.confidence,
                as_of_period=scorecard.as_of_period,
                disclaimer=scorecard.disclaimer,
            ),
            income_statements=[_to_inc_resp(s) for s in inc_stmts],
            balance_sheets=[_to_bs_resp(b) for b in bs_stmts],
            cash_flows=[_to_cf_resp(c) for c in cf_stmts],
        )

    async def get_technicals(self, ticker: str) -> FullTechnicalsResponse:
        ticker = ticker.upper()
        await self.get_company(ticker)

        # Retrieve price bars
        bars = await self.repo.get_price_bars(ticker, limit=400)
        if not bars:
            # Fallback to market provider
            end_d = datetime.now(timezone.utc)
            start_d = end_d.replace(year=end_d.year - 2)
            from app.services.market_provider import get_market_data_provider
            m_prov = get_market_data_provider()
            bars = await m_prov.fetch_historical_bars(ticker, start_d, end_d)

        # Engine expects bars sorted ascending
        sorted_bars = sorted(bars, key=lambda b: b.timestamp)
        result = self.technical_engine.compute_technicals(ticker, sorted_bars)

        return FullTechnicalsResponse(
            ticker=ticker,
            as_of_date=result.as_of_date,
            latest_close=result.latest_close,
            moving_averages=result.moving_averages.__dict__,
            rsi=result.rsi.__dict__,
            macd=result.macd.__dict__,
            bollinger=result.bollinger.__dict__,
            volatility_and_trend=result.volatility_and_trend.__dict__,
            momentum=result.momentum.__dict__,
            signals=[TechnicalSignalSchema(**s.__dict__) for s in result.signals],
            overall_sentiment=result.overall_sentiment,
            data_quality=result.data_quality,
        )

    async def get_valuation(self, ticker: str, dcf_params: Optional[DCFCalculationRequest] = None) -> FullValuationResponse:
        ticker = ticker.upper()
        company = await self.get_company(ticker)

        # Get latest price
        technicals = await self.get_technicals(ticker)
        current_price = technicals.latest_close if technicals.latest_close > 0 else 150.0

        # Statements
        inc_stmts = await self.repo.get_income_statements(ticker, limit=5)
        bs_stmts = await self.repo.get_balance_sheets(ticker, limit=5)
        cf_stmts = await self.repo.get_cash_flows(ticker, limit=5)

        if not inc_stmts:
            inc_stmts = self.provider.get_income_statements(ticker)
        if not bs_stmts:
            bs_stmts = self.provider.get_balance_sheets(ticker)
        if not cf_stmts:
            cf_stmts = self.provider.get_cash_flow_statements(ticker)

        latest_inc = inc_stmts[0] if inc_stmts else None
        latest_bs = bs_stmts[0] if bs_stmts else None
        latest_cf = cf_stmts[0] if cf_stmts else None

        shares = float(company.shares_outstanding or 1_000_000_000)

        # Multiples
        multiples = self.valuation_engine.compute_multiples(
            current_price=current_price,
            shares_outstanding=shares,
            income_stmt=latest_inc,
            balance_sheet=latest_bs,
            cash_flow=latest_cf,
        )

        # Historical Context
        pe_history = [28.5, 30.2, 33.1, 27.4, 29.8, 31.5]
        ev_ebitda_history = [18.2, 20.1, 22.4, 19.5, 21.0, 23.2]
        ps_history = [6.5, 7.2, 8.1, 6.9, 7.5, 8.0]

        ctx_list = [
            MultipleHistoricalContextSchema(**self.valuation_engine.calculate_historical_context("P/E", multiples.pe_ratio, pe_history).__dict__),
            MultipleHistoricalContextSchema(**self.valuation_engine.calculate_historical_context("EV/EBITDA", multiples.ev_to_ebitda, ev_ebitda_history).__dict__),
            MultipleHistoricalContextSchema(**self.valuation_engine.calculate_historical_context("P/S", multiples.ps_ratio, ps_history).__dict__),
        ]

        # Peer Comparison
        peer_tickers = ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"]
        peer_rows: List[PeerValuationRowSchema] = []
        for p_t in peer_tickers:
            p_prof = self.provider.get_company_profile(p_t)
            if not p_prof:
                continue
            # Basic valuation multiples for peer
            p_inc = self.provider.get_income_statements(p_t)
            p_cf = self.provider.get_cash_flow_statements(p_t)
            p_price = float(p_prof.market_cap or 1000) / float(p_prof.shares_outstanding or 10)
            p_pe = (p_price / float(p_inc[0].diluted_eps)) if p_inc and p_inc[0].diluted_eps and p_inc[0].diluted_eps > 0 else 30.0
            p_fcf_y = (float(p_cf[0].free_cash_flow) / float(p_prof.market_cap)) if p_cf and p_cf[0].free_cash_flow and p_prof.market_cap else 0.035
            peer_rows.append(PeerValuationRowSchema(
                ticker=p_t,
                name=p_prof.name,
                price=round(p_price, 2),
                market_cap=float(p_prof.market_cap or 0),
                pe_ratio=round(p_pe, 1),
                ev_to_ebitda=20.5,
                ps_ratio=7.2,
                fcf_yield=round(p_fcf_y, 4),
                revenue_cagr_3y=0.14,
            ))

        # DCF Model
        fcf_base = float(latest_cf.free_cash_flow) if latest_cf and latest_cf.free_cash_flow else 50_000_000_000.0
        tot_debt = float(latest_bs.total_debt or 0) if latest_bs else 0.0
        tot_cash = float(latest_bs.cash_and_equivalents or 0) + float(latest_bs.short_term_investments or 0) if latest_bs else 0.0

        req_wacc = dcf_params.wacc if dcf_params and dcf_params.wacc else 0.09
        req_tg = dcf_params.terminal_growth_rate if dcf_params and dcf_params.terminal_growth_rate else 0.025
        req_g1 = dcf_params.growth_rate_stage1 if dcf_params and dcf_params.growth_rate_stage1 else 0.10

        dcf_res = self.valuation_engine.run_dcf_model(
            ticker=ticker,
            current_price=current_price,
            shares_outstanding=shares,
            fcf_base=fcf_base,
            growth_rate_stage1=req_g1,
            terminal_growth_rate=req_tg,
            wacc=req_wacc,
            total_debt=tot_debt,
            cash_and_investments=tot_cash,
            as_of_date=technicals.as_of_date,
        )

        dcf_schema = DCFModelResultSchema(
            ticker=dcf_res.ticker,
            as_of_date=dcf_res.as_of_date,
            current_price=dcf_res.current_price,
            implied_share_price=dcf_res.implied_share_price,
            upside_downside_percent=dcf_res.upside_downside_percent,
            enterprise_value=dcf_res.enterprise_value,
            equity_value=dcf_res.equity_value,
            pv_projected_fcfs=dcf_res.pv_projected_fcfs,
            pv_terminal_value=dcf_res.pv_terminal_value,
            terminal_value=dcf_res.terminal_value,
            shares_outstanding=dcf_res.shares_outstanding,
            fcf_base=dcf_res.fcf_base,
            wacc=dcf_res.wacc,
            terminal_growth_rate=dcf_res.terminal_growth_rate,
            stage1_growth_rate=dcf_res.stage1_growth_rate,
            projections=[DCFYearProjectionSchema(**p.__dict__) for p in dcf_res.projections],
            sensitivity_matrix=[
                [DCFSensitivityCellSchema(**cell.__dict__) for cell in row]
                for row in dcf_res.sensitivity_matrix
            ],
            sensitivity_wacc_labels=dcf_res.sensitivity_wacc_labels,
            sensitivity_growth_labels=dcf_res.sensitivity_growth_labels,
            data_quality=dcf_res.data_quality,
            disclaimer=dcf_res.disclaimer,
        )

        return FullValuationResponse(
            ticker=ticker,
            current_price=round(current_price, 2),
            multiples=ValuationMultiplesSchema(**multiples.__dict__),
            historical_context=ctx_list,
            peers=peer_rows,
            dcf=dcf_schema,
        )

    async def get_factors(self, ticker: str) -> FullFactorsResponse:
        ticker = ticker.upper()
        company = await self.get_company(ticker)
        technicals = await self.get_technicals(ticker)
        fundamentals = await self.get_fundamentals(ticker)

        inc_stmts = await self.repo.get_income_statements(ticker, limit=2)
        bs_stmts = await self.repo.get_balance_sheets(ticker, limit=2)
        cf_stmts = await self.repo.get_cash_flows(ticker, limit=2)

        latest_inc = inc_stmts[0] if inc_stmts else None
        latest_bs = bs_stmts[0] if bs_stmts else None
        latest_cf = cf_stmts[0] if cf_stmts else None

        current_price = technicals.latest_close
        market_cap = float(company.market_cap or (current_price * float(company.shares_outstanding or 1_000_000_000)))

        profile = self.factors_engine.compute_factors(
            ticker=ticker,
            current_price=current_price,
            market_cap=market_cap,
            income_stmt=latest_inc,
            balance_sheet=latest_bs,
            cash_flow=latest_cf,
            technicals=technicals,
            growth_metrics=fundamentals.growth,
            profitability_metrics=fundamentals.profitability,
            sloan_accruals=fundamentals.earnings_quality.sloan_accruals_ratio,
            as_of_date=technicals.as_of_date,
        )

        factors_map = {
            k: FactorScoreSchema(
                factor_name=v.factor_name,
                composite_score=v.composite_score,
                z_score=v.z_score,
                percentile=v.percentile,
                exposure=v.exposure,
                raw_metrics=v.raw_metrics,
                data_quality=v.data_quality,
                description=v.description,
            )
            for k, v in profile.factors.items()
        }

        return FullFactorsResponse(
            ticker=ticker,
            as_of_date=profile.as_of_date,
            factors=factors_map,
            summary_radar=profile.summary_radar,
            data_quality=profile.data_quality,
            disclaimer=profile.disclaimer,
        )

    async def get_company_intelligence(self, ticker: str) -> CompanyIntelligenceResponse:
        ticker = ticker.upper()
        company = await self.get_company(ticker)
        technicals = await self.get_technicals(ticker)
        fundamentals = await self.get_fundamentals(ticker)
        valuation = await self.get_valuation(ticker)
        factors = await self.get_factors(ticker)

        # Price change calculation
        curr_p = technicals.latest_close
        ret_1m = technicals.momentum.return_1m or 0.005
        change_24h = curr_p * (ret_1m / 21.0)  # estimated 1-day change
        pct_24h = (change_24h / (curr_p - change_24h)) * 100.0 if curr_p > change_24h else 0.0

        prof_schema = CompanyProfileSchema(
            ticker=company.ticker,
            name=company.name,
            exchange=company.exchange,
            sector=company.sector,
            industry=company.industry,
            country=company.country,
            currency=company.currency,
            description=company.description,
            website=company.website,
            market_cap=company.market_cap,
            shares_outstanding=company.shares_outstanding,
            status=company.status,
            is_synthetic=company.is_synthetic,
        )

        return CompanyIntelligenceResponse(
            ticker=ticker,
            profile=prof_schema,
            current_price=round(curr_p, 2),
            price_change_24h=round(change_24h, 2),
            price_change_percent_24h=round(pct_24h, 2),
            fundamentals_summary=fundamentals.scorecard,
            valuation_summary=valuation.multiples,
            technicals_summary=technicals,
            factors_summary=factors,
            data_provenance={
                "data_source": "DEMO_HISTORICAL_SEC_EDGAR",
                "as_of_date": technicals.as_of_date,
                "reporting_currency": "USD",
                "quality_status": "AUDITED",
                "is_synthetic": True,
            },
        )

    async def run_screener(
        self,
        sector: Optional[str] = None,
        min_market_cap: Optional[float] = None,
        max_market_cap: Optional[float] = None,
        min_pe: Optional[float] = None,
        max_pe: Optional[float] = None,
        min_fcf_yield: Optional[float] = None,
        min_scorecard: Optional[float] = None,
        sort_by: str = "market_cap",
        sort_direction: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> ScreenerResponse:
        """Multi-factor stock screener across flagship universe."""
        flagship_tickers = ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"]
        items: List[ScreenerStockItem] = []

        for t in flagship_tickers:
            comp = await self.get_company(t)
            # Fetch fundamentals and technicals
            funds = await self.get_fundamentals(t)
            techs = await self.get_technicals(t)
            valu = await self.get_valuation(t)
            facts = await self.get_factors(t)

            mc = float(comp.market_cap or (techs.latest_close * float(comp.shares_outstanding or 1_000_000_000)))
            pe = valu.multiples.pe_ratio
            fcf_y = valu.multiples.fcf_yield
            score = funds.scorecard.overall_score
            cagr = funds.growth.revenue_cagr_3y
            roe = funds.profitability.return_on_equity

            # Sector Filter
            if sector and sector.lower() not in comp.sector.lower():
                continue

            # Market Cap Filter
            if min_market_cap is not None and mc < min_market_cap:
                continue
            if max_market_cap is not None and mc > max_market_cap:
                continue

            # P/E Filter
            if min_pe is not None and (pe is None or pe < min_pe):
                continue
            if max_pe is not None and (pe is None or pe > max_pe):
                continue

            # FCF Yield Filter
            if min_fcf_yield is not None and (fcf_y is None or fcf_y < min_fcf_yield):
                continue

            # Scorecard Filter
            if min_scorecard is not None and score < min_scorecard:
                continue

            items.append(ScreenerStockItem(
                ticker=comp.ticker,
                name=comp.name,
                sector=comp.sector,
                industry=comp.industry,
                market_cap=round(mc, 2),
                price=round(techs.latest_close, 2),
                pe_ratio=round(pe, 1) if pe is not None else None,
                ev_to_ebitda=round(valu.multiples.ev_to_ebitda, 1) if valu.multiples.ev_to_ebitda is not None else None,
                fcf_yield=round(fcf_y, 4) if fcf_y is not None else None,
                revenue_cagr_3y=round(cagr, 4) if cagr is not None else None,
                roe=round(roe, 4) if roe is not None else None,
                scorecard_score=score,
                rsi_14=techs.rsi.rsi_14,
                overall_sentiment=techs.overall_sentiment,
                momentum_factor=facts.summary_radar.get("Momentum"),
                quality_factor=facts.summary_radar.get("Quality"),
            ))

        # Sorting
        reverse = (sort_direction.lower() == "desc")
        if sort_by == "market_cap":
            items.sort(key=lambda x: x.market_cap or 0, reverse=reverse)
        elif sort_by == "pe_ratio":
            items.sort(key=lambda x: x.pe_ratio if x.pe_ratio is not None else (0 if reverse else 9999), reverse=reverse)
        elif sort_by == "scorecard_score":
            items.sort(key=lambda x: x.scorecard_score or 0, reverse=reverse)
        elif sort_by == "fcf_yield":
            items.sort(key=lambda x: x.fcf_yield if x.fcf_yield is not None else (0 if reverse else 9999), reverse=reverse)
        elif sort_by == "ticker":
            items.sort(key=lambda x: x.ticker, reverse=reverse)

        # Pagination
        total = len(items)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paged_items = items[start_idx:end_idx]

        return ScreenerResponse(
            total=total,
            page=page,
            limit=limit,
            items=paged_items,
            applied_filters={
                "sector": sector,
                "min_market_cap": min_market_cap,
                "max_market_cap": max_market_cap,
                "min_pe": min_pe,
                "max_pe": max_pe,
                "min_fcf_yield": min_fcf_yield,
                "min_scorecard": min_scorecard,
                "sort_by": sort_by,
                "sort_direction": sort_direction,
            },
        )
