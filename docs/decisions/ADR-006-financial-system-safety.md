# ADR-006: Financial-System Safety & Research Integrity Principles

## Status
Accepted

## Context
Financial analytics software carries severe real-world consequences if misdesigned:
* Users may deploy capital based on software outputs.
* Fabricating missing data or presenting simulated backtests as real returns violates ethical and regulatory standards.
* Simplistic "AI stock prediction" tools that claim guaranteed profits or minimum losses deceive users and degrade trust.

## Decision
Establish foundational architectural constraints codified in the codebase and documentation:

1. **Zero Data Fabrication Principle:**
   The platform must **never** fabricate market data, historical returns, Sharpe ratios, risk metrics, financial statements, news items, or source attributions. If data is unavailable or a feature is not yet built, it must remain explicitly `unknown` or raise an informative `NotImplementedError`. Missing fields must never be populated with invented default values.

2. **No Fake Features Rule:**
   The frontend and API must never show fake mockup cards claiming "AI Confidence: 94%" or "Expected Return: 18.2%" when no underlying quantitative calculation exists. Features that belong to future modules must honestly state:
   `Coming in a future research module`.

3. **Strict Modality Separation:**
   Future research engines and UI views must strictly delineate the following data modalities:
   * **Historical Observation:** Actual verified past market prices and fundamentals.
   * **Model Output:** Statistical and machine learning model estimations.
   * **Backtest Result:** In-sample or out-of-sample simulated performance subject to liquidity and execution caveats.
   * **Hypothetical Scenario:** What-if stress test evaluations.
   * **Prediction:** Probabilistic forecasts with explicit confidence intervals.
   * **User Assumption:** Assumptions provided directly by the user.

4. **Institutional Disclaimer Architecture:**
   The application shell must embed standardized regulatory disclaimers explaining that AEGIS is an analytical research tool, not a registered investment advisor, and that securities investing involves risk of loss without guaranteed outcomes.

## Consequences
### Positive
* Protects research integrity and institutional credibility.
* Prevents silent bugs where synthetic numbers are mistaken for real financial metrics.
* Ensures regulatory readiness as the platform expands.

### Negative
* Requires rejecting "quick and flashy" demo features in favor of rigorous, mathematically verified engines.
