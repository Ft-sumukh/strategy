# AEGIS INVEST — Financial Data Strategy & Integrity

## 1. Multi-Provider Architecture

Financial market data is ingested through a normalized abstraction layer (`MarketDataProvider`). This decouples application logic from vendor-specific payloads and rate limits:

```text
[ Bloomberg / Polygon / AlphaVantage / Demo Feeds ]
                         │
                         ↓
             [ MarketDataProvider Interface ]
                         │
                         ↓
               [ Normalization Engine ]
                         │
        ┌────────────────┴────────────────┐
        ↓                                 ↓
[ OHLCV Point-in-Time ]          [ Corporate Actions ]
  (Split & Div Adjusted)          (Splits, Dividends, Spinoffs)
```

## 2. Storage Tiers

- **Raw Data Layer (`data/raw/`)**: Byte-for-byte immutable copies of vendor responses for deterministic audit replay.
- **Processed Data Layer (`data/processed/`)**: High-performance normalized time-series data indexed by `(ticker, timestamp, interval)`.
- **Historical Point-in-Time (`data/historical/`)**: Survivorship-bias-free data snapshots ensuring backtests simulate true historical conditions.
- **Deterministic Demo (`data/demo/`)**: Verified offline sample data for development and tests, explicitly tagged with `is_synthetic: true`.

## 3. Data Integrity & Validation Checks

- **Price Range Checks**: Ensures $\text{High} \ge \max(\text{Open}, \text{Close}, \text{Low})$ and $\text{Low} \le \min(\text{Open}, \text{Close}, \text{High})$.
- **Volume Non-Negativity**: Validates $\text{Volume} \ge 0$.
- **Anomaly Detection**: Flags sudden single-day price moves ($>50\%$) lacking corporate action justification for human audit review.
