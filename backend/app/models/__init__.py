"""
AEGIS INVEST — Models Package
Exports foundation database models, financial intelligence entities,
news NLP records, macroeconomic series, market regimes, systematic strategies,
portfolio holdings, backtests, risk models, AI reasoning entities, and research workspace models.
"""

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.models.experiment import ExperimentRecord
from app.models.financials import (
    BalanceSheet,
    CashFlowStatement,
    Company,
    IncomeStatement,
    MarketPriceBar,
)
from app.models.macro import MacroObservation, MacroSeries
from app.models.news import NewsArticle, NewsEntity, NewsEvent
from app.models.regime import MarketRegimeRecord
from app.models.sentiment import AggregateSentiment, SentimentRecord
from app.models.strategy import StrategyDefinition, StrategySignalRecord
from app.models.system import SystemAudit
from app.models.portfolio_models import Portfolio, PortfolioHolding, PortfolioSnapshot
from app.models.backtest import BacktestConfig, BacktestRun, BacktestEquityPoint, BacktestTrade
from app.models.risk import RiskMetricRecord, StressTestScenario, StressTestResult
from app.models.optimization import OptimizationRunRecord
from app.models.ai import AIConversation, AIMessage, AIToolCall, AIEvidence, AIAuditLog
from app.models.workspace import (
    Watchlist,
    WatchlistItem,
    AlertRule,
    AlertEvent,
    InvestmentThesis,
    ThesisVersion,
    ResearchReport,
    ModelRegistryItem,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "utc_now",
    "SystemAudit",
    "Company",
    "MarketPriceBar",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlowStatement",
    "NewsArticle",
    "NewsEntity",
    "NewsEvent",
    "SentimentRecord",
    "AggregateSentiment",
    "MacroSeries",
    "MacroObservation",
    "MarketRegimeRecord",
    "StrategyDefinition",
    "StrategySignalRecord",
    "ExperimentRecord",
    # Phase 4
    "Portfolio",
    "PortfolioHolding",
    "PortfolioSnapshot",
    "BacktestConfig",
    "BacktestRun",
    "BacktestEquityPoint",
    "BacktestTrade",
    "RiskMetricRecord",
    "StressTestScenario",
    "StressTestResult",
    "OptimizationRunRecord",
    # Phase 5
    "AIConversation",
    "AIMessage",
    "AIToolCall",
    "AIEvidence",
    "AIAuditLog",
    "Watchlist",
    "WatchlistItem",
    "AlertRule",
    "AlertEvent",
    "InvestmentThesis",
    "ThesisVersion",
    "ResearchReport",
    "ModelRegistryItem",
]
