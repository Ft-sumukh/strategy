"""
AEGIS INVEST — Fundamentals API Endpoints
Serves multi-year audited statements (Income Statement, Balance Sheet, Cash Flow),
growth metrics, margin analysis, capital efficiency, balance sheet health,
earnings quality (Sloan accruals), and transparent 6-category scorecards.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.financials import (
    BalanceSheetResponse,
    CashFlowStatementResponse,
    FullFundamentalsResponse,
    IncomeStatementResponse,
)
from app.services.financial_service import FinancialIntelligenceService

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals"])


@router.get(
    "/{ticker}",
    response_model=FullFundamentalsResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Fundamental Analysis & Scorecard",
    description="Returns audited financial statements, YoY growth, margins, ROIC, Sloan accruals, and 6-pillar scorecard.",
)
async def get_fundamentals(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> FullFundamentalsResponse:
    service = FinancialIntelligenceService(db)
    return await service.get_fundamentals(ticker)


@router.get(
    "/{ticker}/income-statement",
    response_model=List[IncomeStatementResponse],
    status_code=status.HTTP_200_OK,
    summary="Standardized Income Statements",
    description="Returns multi-year standardized income statements with quality metadata.",
)
async def get_income_statements(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> List[IncomeStatementResponse]:
    service = FinancialIntelligenceService(db)
    data = await service.get_fundamentals(ticker)
    return data.income_statements


@router.get(
    "/{ticker}/balance-sheet",
    response_model=List[BalanceSheetResponse],
    status_code=status.HTTP_200_OK,
    summary="Standardized Balance Sheets",
    description="Returns multi-year standardized balance sheets with liquidity and debt breakdowns.",
)
async def get_balance_sheets(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> List[BalanceSheetResponse]:
    service = FinancialIntelligenceService(db)
    data = await service.get_fundamentals(ticker)
    return data.balance_sheets


@router.get(
    "/{ticker}/cash-flow",
    response_model=List[CashFlowStatementResponse],
    status_code=status.HTTP_200_OK,
    summary="Standardized Cash Flow Statements",
    description="Returns multi-year cash flow statements (Operating, Investing, Financing, Free Cash Flow).",
)
async def get_cash_flow_statements(
    ticker: str,
    db: AsyncSession = Depends(get_db),
) -> List[CashFlowStatementResponse]:
    service = FinancialIntelligenceService(db)
    data = await service.get_fundamentals(ticker)
    return data.cash_flows
