"""
AEGIS INVEST — Pydantic Schemas Package
Exports core request, response, health, financial, news, sentiment, macro, regime, and strategy validation contracts.
"""

from app.schemas.common import APIResponse, BaseSchema, PaginatedResponse
from app.schemas.health import (
    ComponentStatus,
    HealthResponse,
    ReadinessResponse,
    SystemInfoResponse,
)
from app.schemas.news import (
    NewsArticleListResponse,
    NewsArticleOut,
    NewsEntityOut,
    NewsEventOut,
)
from app.schemas.sentiment import (
    AggregatedSentimentOut,
    SectorSentimentOut,
    SentimentMomentumDetail,
)
from app.schemas.macro import (
    AssetMacroSensitivityOut,
    MacroObservationOut,
    MacroSensitivityFactorOut,
    MacroSeriesOut,
    YieldCurvePoint,
    YieldCurveResponse,
)
from app.schemas.regime import (
    HistoricalRegimePeriodOut,
    RegimeEvaluationOut,
    RegimeSignalDetailOut,
)
from app.schemas.strategy import (
    BenchmarkComparisonOut,
    ExperimentCreateRequest,
    ExperimentRecordOut,
    StrategyDefinitionOut,
    StrategyRunRequest,
    StrategyRunResponse,
    StrategySignalOut,
    TournamentMetricsOut,
    TournamentRunRequest,
    TournamentRunResponse,
)

__all__ = [
    "BaseSchema",
    "APIResponse",
    "PaginatedResponse",
    "ComponentStatus",
    "HealthResponse",
    "ReadinessResponse",
    "SystemInfoResponse",
    "NewsArticleOut",
    "NewsEntityOut",
    "NewsEventOut",
    "NewsArticleListResponse",
    "SentimentMomentumDetail",
    "AggregatedSentimentOut",
    "SectorSentimentOut",
    "MacroObservationOut",
    "MacroSeriesOut",
    "YieldCurvePoint",
    "YieldCurveResponse",
    "MacroSensitivityFactorOut",
    "AssetMacroSensitivityOut",
    "RegimeSignalDetailOut",
    "HistoricalRegimePeriodOut",
    "RegimeEvaluationOut",
    "StrategyDefinitionOut",
    "StrategySignalOut",
    "StrategyRunRequest",
    "StrategyRunResponse",
    "TournamentRunRequest",
    "TournamentMetricsOut",
    "BenchmarkComparisonOut",
    "TournamentRunResponse",
    "ExperimentCreateRequest",
    "ExperimentRecordOut",
]
