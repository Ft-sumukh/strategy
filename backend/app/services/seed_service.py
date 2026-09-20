"""
AEGIS INVEST — Financial Database Seed Service
Populates PostgreSQL / SQLite with deterministic audited company profiles,
historical financial statements, 5-year OHLCV price histories, macroeconomic series,
news & event intelligence, and systematic strategy definitions.
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.financials import (
    BalanceSheet,
    CashFlowStatement,
    Company,
    IncomeStatement,
    MarketPriceBar,
)
from app.models.macro import MacroObservation, MacroSeries
from app.models.news import NewsArticle, NewsEntity, NewsEvent
from app.models.strategy import StrategyDefinition
from app.providers.macro.provider import DemoMacroDataProvider
from app.providers.news.provider import DemoNewsProvider
from app.repositories.financial_repository import FinancialRepository
from app.services.fundamental_provider import get_fundamental_data_provider
from app.services.market_provider import get_market_data_provider
from app.services.strategy_service import DEFAULT_STRATEGIES_CATALOG

logger = get_logger("aegis.seed")


async def seed_financial_database(session: AsyncSession) -> None:
    """Seeds the database with flagship assets, macro, news, and strategies if not already populated."""
    repo = FinancialRepository(session)
    fundamental_provider = get_fundamental_data_provider()
    market_provider = get_market_data_provider()

    flagship_tickers = ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"]

    # Check if companies already exist
    existing_companies, _ = await repo.list_companies(limit=10)
    if len(existing_companies) < len(flagship_tickers):
        logger.info("Seeding database with flagship financial intelligence data...")
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=365 * 4)

        for ticker in flagship_tickers:
            profile = fundamental_provider.get_company_profile(ticker)
            if not profile:
                continue

            # 1. Company
            await repo.upsert_company({
                "ticker": profile.ticker,
                "name": profile.name,
                "exchange": profile.exchange,
                "sector": profile.sector,
                "industry": profile.industry,
                "country": profile.country,
                "currency": profile.currency,
                "description": profile.description,
                "website": profile.website,
                "market_cap": profile.market_cap,
                "shares_outstanding": profile.shares_outstanding,
                "status": profile.status,
                "is_synthetic": True,
            })

            # 2. Income Statements
            inc_stmts = fundamental_provider.get_income_statements(ticker)
            for s in inc_stmts:
                existing_s = await repo.get_income_statements(ticker, s.period_type, limit=20)
                if not any(x.period == s.period for x in existing_s):
                    session.add(IncomeStatement(
                        ticker=s.ticker, period=s.period, period_type=s.period_type,
                        filing_date=s.filing_date, currency=s.currency, revenue=s.revenue,
                        cost_of_revenue=s.cost_of_revenue, gross_profit=s.gross_profit,
                        operating_expenses=s.operating_expenses, operating_income=s.operating_income,
                        ebitda=s.ebitda, ebit=s.ebit, interest_expense=s.interest_expense,
                        pre_tax_income=s.pre_tax_income, tax_expense=s.tax_expense,
                        net_income=s.net_income, eps=s.eps, diluted_eps=s.diluted_eps,
                        source=s.source, data_version=s.data_version, quality_status=s.quality_status,
                        is_synthetic=True
                    ))

            # 3. Balance Sheets
            bs_stmts = fundamental_provider.get_balance_sheets(ticker)
            for b in bs_stmts:
                existing_b = await repo.get_balance_sheets(ticker, b.period_type, limit=20)
                if not any(x.period == b.period for x in existing_b):
                    session.add(BalanceSheet(
                        ticker=b.ticker, period=b.period, period_type=b.period_type,
                        filing_date=b.filing_date, currency=b.currency,
                        cash_and_equivalents=b.cash_and_equivalents, short_term_investments=b.short_term_investments,
                        current_assets=b.current_assets, goodwill=b.goodwill, intangible_assets=b.intangible_assets,
                        total_assets=b.total_assets, current_liabilities=b.current_liabilities,
                        short_term_debt=b.short_term_debt, long_term_debt=b.long_term_debt,
                        total_debt=b.total_debt, total_liabilities=b.total_liabilities,
                        shareholders_equity=b.shareholders_equity, source=b.source,
                        data_version=b.data_version, quality_status=b.quality_status, is_synthetic=True
                    ))

            # 4. Cash Flow Statements
            cf_stmts = fundamental_provider.get_cash_flow_statements(ticker)
            for c in cf_stmts:
                existing_c = await repo.get_cash_flows(ticker, c.period_type, limit=20)
                if not any(x.period == c.period for x in existing_c):
                    session.add(CashFlowStatement(
                        ticker=c.ticker, period=c.period, period_type=c.period_type,
                        filing_date=c.filing_date, currency=c.currency,
                        operating_cash_flow=c.operating_cash_flow, capital_expenditure=c.capital_expenditure,
                        investing_cash_flow=c.investing_cash_flow, financing_cash_flow=c.financing_cash_flow,
                        free_cash_flow=c.free_cash_flow, source=c.source,
                        data_version=c.data_version, quality_status=c.quality_status, is_synthetic=True
                    ))

            # 5. Price Bars (Daily)
            existing_bars = await repo.get_price_bars(ticker, limit=5)
            if not existing_bars:
                bars = await market_provider.fetch_historical_bars(ticker, start_date, end_date)
                for bar in bars:
                    session.add(MarketPriceBar(
                        ticker=ticker, timestamp=bar.timestamp, open=bar.open,
                        high=bar.high, low=bar.low, close=bar.close,
                        adj_close=bar.close, volume=bar.volume, vwap=bar.vwap,
                        interval="1d", is_adjusted=True, data_source="demo_historical"
                    ))

        await session.commit()
        logger.info("Database financial intelligence seeding complete.")

    # 6. Seed Macro Series & Observations
    stmt_macro = select(MacroSeries).limit(1)
    res_macro = await session.execute(stmt_macro)
    if not res_macro.scalar_one_or_none():
        logger.info("Seeding macroeconomic series & observations...")
        macro_provider = DemoMacroDataProvider()
        for s in await macro_provider.get_all_series():
            series_obj = MacroSeries(
                series_code=s.series_code,
                name=s.name,
                country=s.country,
                frequency=s.frequency,
                unit=s.unit,
                description=s.description,
                source=s.source,
            )
            session.add(series_obj)

            # Observations
            obs_list = await macro_provider.get_observations(s.series_code)
            for o in obs_list:
                session.add(MacroObservation(
                    series_code=o.series_code,
                    timestamp=o.timestamp,
                    value=o.value,
                    source=o.source,
                    data_version=o.data_version,
                    quality_status=o.quality_status,
                ))
        await session.commit()
        logger.info("Macroeconomic series seeding complete.")

    # 7. Seed News Articles
    stmt_news = select(NewsArticle).limit(1)
    res_news = await session.execute(stmt_news)
    if not res_news.scalar_one_or_none():
        logger.info("Seeding news & event intelligence...")
        news_provider = DemoNewsProvider()
        articles = await news_provider.search_news(limit=50)
        for a in articles:
            # Generate deterministic UUID string from id
            art_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, a.id))
            art_obj = NewsArticle(
                id=art_uuid,
                headline=a.headline,
                summary=a.summary,
                content=a.content,
                publisher=a.publisher,
                source=a.source,
                url=a.url,
                published_at=a.published_at,
                ticker=a.ticker,
                sector=a.sector,
                industry=a.industry,
                country=a.country,
                category=a.category,
                language=a.language,
                content_hash=a.content_hash,
                data_source="demo_news",
                data_version="v1.0",
                quality_status="VERIFIED",
                is_synthetic=True,
            )
            session.add(art_obj)
            await session.flush()

            # Add entities
            for ent in a.entities:
                session.add(NewsEntity(
                    article_id=art_obj.id,
                    entity_type=ent.get("entity_type", "Company"),
                    entity_name=ent.get("entity_name", ""),
                    confidence=ent.get("confidence", 0.9),
                ))

            # Add events
            for ev in a.events:
                ev_date = None
                if ev.get("event_date"):
                    try:
                        if isinstance(ev["event_date"], datetime):
                            ev_date = ev["event_date"].date()
                        else:
                            ev_date = datetime.fromisoformat(str(ev["event_date"])).date()
                    except Exception:
                        pass
                session.add(NewsEvent(
                    article_id=art_obj.id,
                    event_type=ev.get("event_type", "MARKET_EVENT"),
                    event_date=ev_date,
                    confidence=ev.get("confidence", 0.9),
                ))
        await session.commit()
        logger.info("News & event intelligence seeding complete.")

    # 8. Seed Systematic Strategy Definitions
    stmt_strat = select(StrategyDefinition).limit(1)
    res_strat = await session.execute(stmt_strat)
    if not res_strat.scalar_one_or_none():
        logger.info("Seeding systematic strategy definitions...")
        for strat in DEFAULT_STRATEGIES_CATALOG:
            univ = ",".join(strat["universe"]) if isinstance(strat["universe"], list) else str(strat.get("universe", "US_LARGE_CAP"))
            params = json.loads(strat["parameters"]) if isinstance(strat.get("parameters"), str) else (strat.get("parameters") or {})
            constraints = json.loads(strat["risk_constraints"]) if isinstance(strat.get("risk_constraints"), str) else (strat.get("risk_constraints") or {})
            session.add(StrategyDefinition(
                strategy_key=strat["strategy_key"],
                name=strat["name"],
                category=strat["category"],
                description=strat["description"],
                universe=univ,
                rebalance_frequency=strat["rebalance_frequency"],
                parameters=params,
                risk_constraints=constraints,
                version=strat["version"],
                is_active=strat["is_active"],
            ))
        await session.commit()
        logger.info("Systematic strategy definitions seeding complete.")

    # 9. Seed Demo Portfolio (Phase 4)
    from app.models.portfolio_models import Portfolio, PortfolioHolding
    stmt_port = select(Portfolio).limit(1)
    res_port = await session.execute(stmt_port)
    if not res_port.scalar_one_or_none():
        logger.info("Seeding demo multi-asset portfolio...")
        demo_port = Portfolio(
            name="Flagship Core Growth Portfolio",
            description="Institutional multi-asset portfolio balanced across secular growth, quality compounders, and defensive allocations.",
            user_id="default_user",
        )
        session.add(demo_port)
        await session.flush()

        holdings_weights = [
            ("AAPL", 0.18, 120, 185.0),
            ("MSFT", 0.18, 55, 410.0),
            ("NVDA", 0.18, 150, 120.0),
            ("GOOG", 0.14, 85, 175.0),
            ("AMZN", 0.14, 75, 180.0),
            ("BRK.B", 0.08, 20, 440.0),
            ("JPM", 0.05, 25, 210.0),
            ("COST", 0.05, 8, 850.0),
        ]
        for ticker, w, qty, cost in holdings_weights:
            session.add(PortfolioHolding(
                portfolio_id=demo_port.id,
                ticker=ticker,
                weight=w,
                quantity=qty,
                cost_basis=cost,
            ))
        await session.commit()
        logger.info("Demo portfolio seeding complete.")

    # 10. Seed Research Workspace, Watchlists, Theses, and Alerts (Phase 5)
    from app.models.workspace import (
        AlertRule,
        InvestmentThesis,
        ModelRegistryItem,
        ThesisVersion,
        Watchlist,
        WatchlistItem,
    )

    # Watchlists
    stmt_wl = select(Watchlist).limit(1)
    res_wl = await session.execute(stmt_wl)
    if not res_wl.scalar_one_or_none():
        logger.info("Seeding institutional watchlists...")
        wl1 = Watchlist(name="AI & Cloud Infrastructure Leaders", description="Enterprise AI compute, hyperscalers, and semiconductor supply chain.", user_id="default_user")
        session.add(wl1)
        await session.flush()
        for t in ["NVDA", "MSFT", "GOOG", "AMZN"]:
            session.add(WatchlistItem(watchlist_id=wl1.id, ticker=t))

        wl2 = Watchlist(name="High-Quality Compounders", description="High ROIC, clean accounting accruals, and strong free cash flow conversion.", user_id="default_user")
        session.add(wl2)
        await session.flush()
        for t in ["AAPL", "BRK.B", "COST", "JPM"]:
            session.add(WatchlistItem(watchlist_id=wl2.id, ticker=t))
        await session.commit()

    # Theses
    stmt_th = select(InvestmentThesis).limit(1)
    res_th = await session.execute(stmt_th)
    if not res_th.scalar_one_or_none():
        logger.info("Seeding investment theses...")
        th = InvestmentThesis(
            user_id="default_user",
            ticker="NVDA",
            title="NVIDIA — Full-Stack Accelerated Computing Moat",
            summary="Market leadership in datacenter GPU clusters, CUDA ecosystem stickiness, and sovereign AI compute buildouts.",
            investment_case="NVIDIA maintains >80% share in high-performance AI accelerators. Compute and networking integration via InfiniBand/NVLink provides substantial total cost of ownership advantages.",
            time_horizon="2-3 Years",
            key_assumptions=[
                "Hyperscaler AI Capex continues expanding at >20% CAGR through 2026",
                "Gross margins sustain above 70% supported by software and networking attach rate",
                "CUDA software ecosystem prevents rapid commoditization from custom ASICs",
            ],
            invalidation_conditions=[
                "Operating margin compresses >300 bps QoQ",
                "Custom silicon from top 3 hyperscalers captures >30% of tier-1 training workloads",
                "US export restriction escalations eliminate additional revenue pools",
            ],
            status="ACTIVE",
            version=1,
        )
        session.add(th)
        await session.flush()
        session.add(ThesisVersion(
            thesis_id=th.id,
            version_number=1,
            snapshot={"title": th.title, "summary": th.summary, "investment_case": th.investment_case},
            change_rationale="Initial thesis baseline.",
        ))
        await session.commit()

    # Alerts
    stmt_al = select(AlertRule).limit(1)
    res_al = await session.execute(stmt_al)
    if not res_al.scalar_one_or_none():
        session.add(AlertRule(
            user_id="default_user",
            ticker="NVDA",
            alert_type="VALUATION_PE",
            condition="GREATER_THAN",
            threshold="45.0",
            status="ACTIVE",
        ))
        session.add(AlertRule(
            user_id="default_user",
            alert_type="REGIME_CHANGE",
            condition="CHANGES_TO",
            threshold="RISK_OFF",
            status="ACTIVE",
        ))
        await session.commit()

    # Model Registry
    stmt_mr = select(ModelRegistryItem).limit(1)
    res_mr = await session.execute(stmt_mr)
    if not res_mr.scalar_one_or_none():
        from app.services.model_monitoring_service import DEFAULT_MODELS_METADATA
        for m in DEFAULT_MODELS_METADATA:
            session.add(ModelRegistryItem(
                model_name=m["model_name"],
                model_type=m["model_type"],
                version=m["version"],
                provider=m["provider"],
                training_period=m["training_period"],
                feature_set=m["feature_set"],
                performance_metrics=m["performance_metrics"],
                drift_metrics=m["drift_metrics"],
                status=m["status"],
            ))
        await session.commit()
        logger.info("All Phase 1-5 database seeding complete.")
