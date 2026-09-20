"""
AEGIS INVEST — Sentiment Analytics Engine
Computes article-level financial sentiment, rolling multi-window momentum (1D, 7D, 30D, 90D),
sentiment dispersion (variance/ambiguity), and company/sector/market aggregations.

FINANCIAL-SYSTEM PRINCIPLE (§ 11):
Sentiment is a descriptive measurement of text tone, NOT a guarantee of corporate future performance.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import math
import re
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SentimentResult:
    sentiment: str  # POSITIVE, NEUTRAL, NEGATIVE
    sentiment_score: float  # -1.0 to +1.0
    confidence: float  # 0.0 to 1.0
    model_version: str = "lexicon_fin_v1"
    processed_at: str = ""


@dataclass
class SentimentMomentumMetrics:
    window: str  # 1D, 7D, 30D, 90D
    current_sentiment: float
    historical_average: float
    change: float
    dispersion: float
    article_count: int


@dataclass
class AggregatedSentimentResult:
    entity_type: str  # COMPANY, SECTOR, MARKET
    entity_id: str
    headline_sentiment: str  # POSITIVE, NEUTRAL, NEGATIVE, MIXED
    current_score: float
    dispersion: float
    momentum_metrics: Dict[str, SentimentMomentumMetrics] = field(default_factory=dict)
    as_of_date: str = ""
    disclaimer: str = "Sentiment reflects textual analysis of published news articles and does not represent future price predictions."


class SentimentEngine:
    """Institutional-grade financial sentiment and momentum engine."""

    # Curated financial lexicon with polarity weights
    POSITIVE_TERMS: Dict[str, float] = {
        "record": 0.8, "surge": 0.85, "beat": 0.9, "outperform": 0.8,
        "expansion": 0.6, "growth": 0.6, "profit": 0.7, "dividend": 0.5,
        "repurchase": 0.5, "buyback": 0.6, "upgrade": 0.75, "accelerate": 0.7,
        "reaccelerate": 0.8, "strong": 0.5, "gain": 0.5, "rally": 0.7,
        "all-time high": 0.9, "exceed": 0.7, "breakthrough": 0.85,
        "efficiency": 0.5, "cooling inflation": 0.6, "solid": 0.5,
    }

    NEGATIVE_TERMS: Dict[str, float] = {
        "plunge": -0.85, "miss": -0.9, "slump": -0.8, "drop": -0.5,
        "decline": -0.6, "antitrust": -0.7, "investigation": -0.75, "probe": -0.75,
        "scrutiny": -0.6, "lawsuit": -0.7, "subpoena": -0.8, "penalty": -0.75,
        "downgrade": -0.8, "warning": -0.7, "recession": -0.8, "cut": -0.5,
        "loss": -0.7, "headwind": -0.5, "shortage": -0.6, "litigation": -0.65,
        "restructure": -0.4, "layoff": -0.6, "weakness": -0.6,
    }

    def analyze_text(self, text: str) -> SentimentResult:
        """Analyzes text tone using institutional financial lexicon."""
        if not text:
            return SentimentResult(
                sentiment="NEUTRAL",
                sentiment_score=0.0,
                confidence=0.5,
                processed_at=datetime.now(timezone.utc).isoformat(),
            )

        lower_text = text.lower()
        pos_score = 0.0
        neg_score = 0.0
        match_count = 0

        for term, weight in self.POSITIVE_TERMS.items():
            pattern = rf"\b{re.escape(term)}\b"
            matches = len(re.findall(pattern, lower_text))
            if matches > 0:
                pos_score += matches * weight
                match_count += matches

        for term, weight in self.NEGATIVE_TERMS.items():
            pattern = rf"\b{re.escape(term)}\b"
            matches = len(re.findall(pattern, lower_text))
            if matches > 0:
                neg_score += matches * abs(weight)
                match_count += matches

        total_score = pos_score - neg_score
        # Normalize score into [-1.0, 1.0] using hyperbolic tangent scaling
        normalized_score = math.tanh(total_score / 2.0) if match_count > 0 else 0.0

        if normalized_score >= 0.20:
            sentiment = "POSITIVE"
        elif normalized_score <= -0.20:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"

        confidence = min(0.98, max(0.60, 0.60 + (match_count * 0.08)))

        return SentimentResult(
            sentiment=sentiment,
            sentiment_score=round(normalized_score, 3),
            confidence=round(confidence, 2),
            model_version="lexicon_fin_v1",
            processed_at=datetime.now(timezone.utc).isoformat(),
        )

    def calculate_dispersion(self, scores: List[float]) -> float:
        """Computes standard deviation (dispersion) of article sentiment scores."""
        if len(scores) < 2:
            return 0.0
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        return round(math.sqrt(variance), 4)

    def compute_dispersion(self, scores: List[float]) -> float:
        """Alias for calculate_dispersion."""
        return self.calculate_dispersion(scores)

    def aggregate_sentiment(
        self,
        articles: List[Dict[str, Any]],
        entity_type: str = "COMPANY",
        entity_id: str = "AAPL",
        as_of_date: Optional[datetime] = None,
    ) -> AggregatedSentimentResult:
        """Convenience method matching test interface for aggregating sentiment."""
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        class MockArticle:
            def __init__(self, data: Dict[str, Any]):
                self.sentiment_score = data.get("sentiment_score", 0.0)
                dt_str = data.get("published_at")
                if isinstance(dt_str, str):
                    try:
                        self.published_at = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                    except Exception:
                        self.published_at = as_of_date
                elif isinstance(dt_str, datetime):
                    self.published_at = dt_str
                else:
                    self.published_at = as_of_date

        mock_articles = [MockArticle(a) for a in articles]
        return self.aggregate_company_sentiment(entity_id, mock_articles, as_of_date)

    def calculate_momentum(
        self,
        article_dates_and_scores: List[Tuple[datetime, float]],
        as_of_date: Optional[datetime] = None,
    ) -> Dict[str, SentimentMomentumMetrics]:
        """Calculates rolling sentiment momentum across 1D, 7D, 30D, and 90D windows."""
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        windows = {"1D": 1, "7D": 7, "30D": 30, "90D": 90}
        results: Dict[str, SentimentMomentumMetrics] = {}

        for w_name, days in windows.items():
            start_curr = as_of_date - timedelta(days=days)
            start_prev = as_of_date - timedelta(days=days * 2)

            curr_scores = [score for dt, score in article_dates_and_scores if start_curr <= dt <= as_of_date]
            prev_scores = [score for dt, score in article_dates_and_scores if start_prev <= dt < start_curr]

            curr_avg = sum(curr_scores) / len(curr_scores) if curr_scores else 0.0
            prev_avg = sum(prev_scores) / len(prev_scores) if prev_scores else curr_avg
            change = curr_avg - prev_avg
            dispersion = self.calculate_dispersion(curr_scores)

            results[w_name] = SentimentMomentumMetrics(
                window=w_name,
                current_sentiment=round(curr_avg, 3),
                historical_average=round(prev_avg, 3),
                change=round(change, 3),
                dispersion=dispersion,
                article_count=len(curr_scores),
            )

        return results

    def aggregate_company_sentiment(
        self,
        ticker: str,
        articles: List[Any],  # Objects with published_at and sentiment_score
        as_of_date: Optional[datetime] = None,
    ) -> AggregatedSentimentResult:
        """
        Computes weighted company-level sentiment.
        Weighting factors:
        - Recency exponential decay: e^(-lambda * days) with half-life of 14 days
        - Dispersion and multi-window momentum
        """
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        if not articles:
            return AggregatedSentimentResult(
                entity_type="COMPANY",
                entity_id=ticker.upper(),
                headline_sentiment="NEUTRAL",
                current_score=0.0,
                dispersion=0.0,
                as_of_date=str(as_of_date)[:10],
            )

        # Decay constant for 14-day half-life: lambda = ln(2) / 14 ~= 0.0495
        decay_lambda = 0.0495
        weighted_sum = 0.0
        weight_total = 0.0
        raw_scores: List[float] = []
        pairs: List[Tuple[datetime, float]] = []

        for a in articles:
            score = float(getattr(a, "sentiment_score", 0.0))
            pub_at = getattr(a, "published_at", as_of_date)
            days_ago = max(0.0, (as_of_date - pub_at).total_seconds() / 86400.0)
            recency_weight = math.exp(-decay_lambda * days_ago)

            weighted_sum += score * recency_weight
            weight_total += recency_weight
            raw_scores.append(score)
            pairs.append((pub_at, score))

        final_score = weighted_sum / weight_total if weight_total > 0 else 0.0
        dispersion = self.calculate_dispersion(raw_scores)
        momentum = self.calculate_momentum(pairs, as_of_date)

        if dispersion > 0.45:
            headline = "MIXED"
        elif final_score >= 0.20:
            headline = "POSITIVE"
        elif final_score <= -0.20:
            headline = "NEGATIVE"
        else:
            headline = "NEUTRAL"

        return AggregatedSentimentResult(
            entity_type="COMPANY",
            entity_id=ticker.upper(),
            headline_sentiment=headline,
            current_score=round(final_score, 3),
            dispersion=dispersion,
            momentum_metrics=momentum,
            as_of_date=str(as_of_date)[:10],
        )

    def aggregate_market_sentiment(
        self,
        company_sentiments: List[AggregatedSentimentResult],
        as_of_date: Optional[datetime] = None,
    ) -> AggregatedSentimentResult:
        """Aggregates market-level sentiment across universe."""
        if as_of_date is None:
            as_of_date = datetime.now(timezone.utc)

        if not company_sentiments:
            return AggregatedSentimentResult(
                entity_type="MARKET",
                entity_id="US_BROAD_MARKET",
                headline_sentiment="NEUTRAL",
                current_score=0.0,
                dispersion=0.0,
                as_of_date=str(as_of_date)[:10],
            )

        scores = [cs.current_score for cs in company_sentiments]
        avg_score = sum(scores) / len(scores)
        dispersion = self.calculate_dispersion(scores)

        if dispersion > 0.40:
            headline = "MIXED"
        elif avg_score >= 0.15:
            headline = "POSITIVE"
        elif avg_score <= -0.15:
            headline = "NEGATIVE"
        else:
            headline = "NEUTRAL"

        return AggregatedSentimentResult(
            entity_type="MARKET",
            entity_id="US_BROAD_MARKET",
            headline_sentiment=headline,
            current_score=round(avg_score, 3),
            dispersion=dispersion,
            as_of_date=str(as_of_date)[:10],
        )
