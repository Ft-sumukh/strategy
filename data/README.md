# AEGIS INVEST — Data Directory Architecture

This directory houses the structured storage layers for financial data ingestion, processing, and historical research datasets.

## Directory Structure

- `raw/`: Unaltered, raw responses from upstream market data, SEC filings, earnings calls, and news feeds. Stored in immutable formats with timestamps and provider lineage headers.
- `processed/`: Cleaned, validated, normalized, and split-adjusted datasets ready for factor modeling, portfolio optimization, and backtesting.
- `historical/`: Point-in-time historical archives used for out-of-sample backtesting without survivorship bias or lookahead bias.
- `demo/`: Static seed datasets used for deterministic demonstration environments, testing, and offline development. Clearly marked with `is_synthetic: true` / `data_source: "historical_demo"`.

## Financial Data Integrity Principles

1. **Immutability**: Raw ingestion files are write-once, read-many (WORM).
2. **Lineage Tracking**: Every processed data point maintains audit metadata identifying source provider, fetch timestamp, and calculation version.
3. **No Hallucinated Data**: Missing records are represented as `null` or explicit gap markers; prices are never fabricated or linearly interpolated across missing market days.
