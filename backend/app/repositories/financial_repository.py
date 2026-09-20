"""
AEGIS INVEST — Financial Intelligence Repository Layer
Provides optimized queries for Companies, Historical Financial Statements,
Market Price Bars, and Multi-Factor Screener Filters.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financials import (
    BalanceSheet,
    CashFlowStatement,
    Company,
    IncomeStatement,
    MarketPriceBar,
)
from app.repositories.base import BaseRepository


class FinancialRepository:
    """Repository handling all financial domain model queries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # --------------------------------------------------------------------------
    # Company Queries
    # --------------------------------------------------------------------------
    async def get_company_by_ticker(self, ticker: str) -> Optional[Company]:
        stmt = select(Company).where(func.upper(Company.ticker) == ticker.upper())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_companies(
        self,
        sector: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Company], int]:
        filters = []
        if sector and sector.lower() != "all":
            filters.append(func.lower(Company.sector) == sector.lower())
        if search:
            s = f"%{search.lower()}%"
            filters.append(or_(func.lower(Company.ticker).like(s), func.lower(Company.name).like(s)))

        where_clause = and_(*filters) if filters else True

        # Total count query
        count_stmt = select(func.count(Company.id)).where(where_clause)
        total_count = (await self.session.execute(count_stmt)).scalar() or 0

        # Items query
        stmt = select(Company).where(where_clause).order_by(Company.ticker).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total_count

    async def upsert_company(self, company_data: Dict[str, Any]) -> Company:
        existing = await self.get_company_by_ticker(company_data["ticker"])
        if existing:
            for k, v in company_data.items():
                setattr(existing, k, v)
            await self.session.flush()
            return existing
        else:
            new_comp = Company(**company_data)
            self.session.add(new_comp)
            await self.session.flush()
            return new_comp

    # --------------------------------------------------------------------------
    # Financial Statement Queries
    # --------------------------------------------------------------------------
    async def get_income_statements(
        self,
        ticker: str,
        period_type: str = "ANNUAL",
        limit: int = 10,
    ) -> List[IncomeStatement]:
        stmt = (
            select(IncomeStatement)
            .where(
                and_(
                    func.upper(IncomeStatement.ticker) == ticker.upper(),
                    IncomeStatement.period_type == period_type,
                )
            )
            .order_by(desc(IncomeStatement.period))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_balance_sheets(
        self,
        ticker: str,
        period_type: str = "ANNUAL",
        limit: int = 10,
    ) -> List[BalanceSheet]:
        stmt = (
            select(BalanceSheet)
            .where(
                and_(
                    func.upper(BalanceSheet.ticker) == ticker.upper(),
                    BalanceSheet.period_type == period_type,
                )
            )
            .order_by(desc(BalanceSheet.period))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_cash_flows(
        self,
        ticker: str,
        period_type: str = "ANNUAL",
        limit: int = 10,
    ) -> List[CashFlowStatement]:
        stmt = (
            select(CashFlowStatement)
            .where(
                and_(
                    func.upper(CashFlowStatement.ticker) == ticker.upper(),
                    CashFlowStatement.period_type == period_type,
                )
            )
            .order_by(desc(CashFlowStatement.period))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # Market Price Bars Queries
    # --------------------------------------------------------------------------
    async def get_price_bars(
        self,
        ticker: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d",
        limit: int = 500,
    ) -> List[MarketPriceBar]:
        filters = [
            func.upper(MarketPriceBar.ticker) == ticker.upper(),
            MarketPriceBar.interval == interval,
        ]
        if start_date:
            filters.append(MarketPriceBar.timestamp >= start_date)
        if end_date:
            filters.append(MarketPriceBar.timestamp <= end_date)

        stmt = (
            select(MarketPriceBar)
            .where(and_(*filters))
            .order_by(asc(MarketPriceBar.timestamp))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_price_bar(self, ticker: str) -> Optional[MarketPriceBar]:
        stmt = (
            select(MarketPriceBar)
            .where(func.upper(MarketPriceBar.ticker) == ticker.upper())
            .order_by(desc(MarketPriceBar.timestamp))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # --------------------------------------------------------------------------
    # Multi-Factor Stock Screener Backend Query
    # --------------------------------------------------------------------------
    async def run_screener_query(
        self,
        sector: Optional[str] = None,
        min_market_cap: Optional[Decimal] = None,
        max_market_cap: Optional[Decimal] = None,
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Company], int]:
        """
        Executes a safe parameterized multi-factor query on the database.
        Prevents arbitrary SQL injection by validating fields.
        """
        filters = [Company.status == "ACTIVE"]

        if sector and sector.lower() != "all":
            filters.append(func.lower(Company.sector) == sector.lower())
        if min_market_cap is not None:
            filters.append(Company.market_cap >= min_market_cap)
        if max_market_cap is not None:
            filters.append(Company.market_cap <= max_market_cap)

        where_clause = and_(*filters)

        # Count total matching
        count_stmt = select(func.count(Company.id)).where(where_clause)
        total = (await self.session.execute(count_stmt)).scalar() or 0

        # Sort order
        sort_column_map = {
            "ticker": Company.ticker,
            "name": Company.name,
            "market_cap": Company.market_cap,
            "sector": Company.sector,
        }
        col = sort_column_map.get(sort_by, Company.market_cap)
        order_expr = desc(col) if sort_order.lower() == "desc" else asc(col)

        stmt = select(Company).where(where_clause).order_by(order_expr).limit(limit).offset(offset)
        results = await self.session.execute(stmt)
        return list(results.scalars().all()), total
