"""
AEGIS INVEST — Macroeconomic Foundation Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema


class MacroObservationOut(BaseSchema):
    series_code: str
    timestamp: datetime
    value: float
    source: Optional[str] = None


class MacroSeriesOut(BaseSchema):
    series_code: str
    name: str
    country: str
    frequency: str
    unit: str
    description: Optional[str] = None
    source: Optional[str] = None
    latest_value: Optional[float] = None
    latest_timestamp: Optional[datetime] = None
    history: List[MacroObservationOut] = Field(default_factory=list)


class YieldCurvePoint(BaseSchema):
    tenor: str  # 3M, 2Y, 5Y, 10Y, 30Y
    tenor_years: float
    yield_pct: float
    series_code: str


class YieldCurveResponse(BaseSchema):
    as_of_date: str
    curve_points: List[YieldCurvePoint]
    spread_10y_2y: float
    is_inverted: bool
    inversion_depth_bps: float
    regime_context: str
    disclaimer: str = (
        "Yield curve data reflects sovereign benchmark debt market yields. "
        "Historical curve inversions have preceded economic contractions but do not guarantee future timing."
    )


class MacroSensitivityFactorOut(BaseSchema):
    series_code: str
    factor_name: str
    beta: float
    correlation: float
    r_squared: float
    p_value: float
    sample_size: int
    exposure_direction: str
    interpretation: str
    description: str


class AssetMacroSensitivityOut(BaseSchema):
    ticker: str
    as_of_date: str
    sample_period_days: int
    sensitivities: List[MacroSensitivityFactorOut] = Field(default_factory=list)
    dominant_macro_risk: str
    resilience_score: float
    data_quality: str
    disclaimer: str = (
        "Macro sensitivities reflect empirical historical co-movements and regression estimates. "
        "They are descriptive measurements of factor exposure and do not constitute causal predictions."
    )
