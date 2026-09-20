"""
Unit tests for Financial Sentiment Analytics Engine.
"""

import pytest
from app.analytics.sentiment.engine import SentimentEngine


def test_sentiment_scoring_bounds():
    engine = SentimentEngine()

    bullish_text = "NVIDIA surges to record all-time high following massive profit growth and dividend increase"
    res_bull = engine.analyze_text(bullish_text)
    assert res_bull.sentiment == "POSITIVE"
    assert 0.0 < res_bull.sentiment_score <= 1.0

    bearish_text = "Tech firm plunges on severe revenue miss, regulatory antitrust investigation, and major layoffs"
    res_bear = engine.analyze_text(bearish_text)
    assert res_bear.sentiment == "NEGATIVE"
    assert -1.0 <= res_bear.sentiment_score < 0.0

    neutral_text = "Company maintains regular operations and holds scheduled shareholder meeting in Chicago"
    res_neut = engine.analyze_text(neutral_text)
    assert -0.15 <= res_neut.sentiment_score <= 0.15


def test_sentiment_dispersion():
    engine = SentimentEngine()

    # Low dispersion (all positive)
    scores_low_disp = [0.6, 0.7, 0.65, 0.58]
    disp_low = engine.compute_dispersion(scores_low_disp)
    assert disp_low < 0.05

    # High dispersion (conflicting polarized sentiment)
    scores_high_disp = [-0.8, 0.9, -0.6, 0.85]
    disp_high = engine.compute_dispersion(scores_high_disp)
    assert disp_high > 0.4


def test_sentiment_aggregation_and_momentum():
    engine = SentimentEngine()

    sample_articles = [
        {"headline": "Apple Beats Q3 Earnings", "sentiment_score": 0.75, "published_at": "2024-08-01T10:00:00Z"},
        {"headline": "Apple Unveils New Services", "sentiment_score": 0.50, "published_at": "2024-07-25T10:00:00Z"},
        {"headline": "Antitrust Scrutiny in Europe", "sentiment_score": -0.40, "published_at": "2024-06-15T10:00:00Z"},
    ]

    agg = engine.aggregate_sentiment(sample_articles, entity_type="COMPANY", entity_id="AAPL")
    assert agg.entity_id == "AAPL"
    assert -1.0 <= agg.current_score <= 1.0
    assert "7D" in agg.momentum_metrics
    assert "30D" in agg.momentum_metrics
    assert "90D" in agg.momentum_metrics
