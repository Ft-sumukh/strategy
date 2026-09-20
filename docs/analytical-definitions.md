# AEGIS INVEST — Analytical Definitions & Mathematical Formulations

This document establishes the institutional mathematical definitions, inputs, economic interpretations, and operational limitations for all quantitative models and financial analytics implemented in **AEGIS INVEST Phase 2 (Financial Intelligence Engine)**.

---

## 1. Fundamental Metrics & Quality Ratios

### 1.1 Return on Equity (ROE)
- **Mathematical Formula**:
  $$\text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}}$$
- **Inputs**:
  - `Net Income`: Trailing Twelve Months (TTM) GAAP Net Income after taxes.
  - `Shareholders' Equity`: Book value of equity (point-in-time or average over period).
- **Interpretation**: Measures accounting profitability generated per dollar of equity capital invested.
- **Limitations**: Susceptible to artificial inflation via financial leverage (debt) and share repurchases that reduce equity book value.

### 1.2 Return on Invested Capital (ROIC)
- **Mathematical Formula**:
  $$\text{ROIC} = \frac{\text{NOPAT}}{\text{Invested Capital}}$$
  $$\text{NOPAT} = \text{Operating Income (EBIT)} \times (1 - t_{\text{eff}})$$
  $$\text{Invested Capital} = \text{Total Debt} + \text{Shareholders' Equity} - (\text{Cash} + \text{Short-Term Investments})$$
- **Inputs**:
  - `Operating Income`: Trailing operating profit from core operations.
  - $t_{\text{eff}}$: Effective income tax rate ($\text{Tax Expense} / \text{Pre-Tax Income}$).
  - `Cash & Short-Term Investments`: Excess operating liquidity subtracted from invested capital.
- **Interpretation**: Gauge of core economic value creation independent of capital structure financing decisions.
- **Limitations**: Non-operating intangible capital (e.g. capitalized R&D) is not capitalized in standard GAAP statements.

### 1.3 Sloan Accruals Ratio
- **Mathematical Formula**:
  $$\text{Accruals Ratio} = \frac{\text{Net Income} - \text{Operating Cash Flow}}{\text{Average Total Assets}}$$
- **Interpretation**:
  - $\text{Accruals} \le 0.00$: **High Quality** — Cash flow from operations exceeds accounting net income.
  - $0.00 < \text{Accruals} \le 0.05$: **Normal Quality** — Standard working capital accruals.
  - $\text{Accruals} > 0.10$: **Low Quality Warning** — Non-cash accounting profits outpace cash generation.
- **Limitations**: Rapid top-line growth naturally expands receivables and inventory, which can transiently increase accruals without accounting manipulation.

### 1.4 Compound Annual Growth Rate (CAGR)
- **Mathematical Formula**:
  $$\text{CAGR}_{n} = \left( \frac{\text{Metric}_t}{\text{Metric}_{t-n}} \right)^{\frac{1}{n}} - 1$$
- **Limitations**: Undefined or mathematically invalid when starting values are non-positive. Aegis strictly returns `null` rather than falsifying negative-base CAGRs.

---

## 2. Valuation Multiples & Intrinsic Models

### 2.1 Price-to-Earnings (P/E)
- **Formula**: $\text{P/E} = \frac{\text{Market Price Per Share}}{\text{Diluted GAAP EPS}}$
- **Interpretation**: Cost per dollar of trailing accounting profit.

### 2.2 Enterprise Value to EBITDA (EV/EBITDA)
- **Formula**:
  $$\text{EV} = \text{Market Cap} + \text{Total Debt} - (\text{Cash} + \text{Short-Term Investments})$$
  $$\text{EV/EBITDA} = \frac{\text{EV}}{\text{EBITDA}}$$
- **Interpretation**: Capital structure-neutral multiple of operating pre-depreciation cash generation.

### 2.3 Free Cash Flow Yield (FCF Yield)
- **Formula**:
  $$\text{FCF Yield} = \frac{\text{Operating Cash Flow} - |\text{Capital Expenditures}|}{\text{Market Capitalization}}$$
- **Interpretation**: Discretionary cash generation percentage returned or reinvestible relative to market price.

### 2.4 Discounted Cash Flow (DCF) Model
- **5-Year Projection**:
  $$FCF_t = FCF_0 \times (1 + g_1)^t \quad \text{for } t \in [1, 5]$$
  $$PV(FCF) = \sum_{t=1}^5 \frac{FCF_t}{(1 + WACC)^t}$$
- **Terminal Value (Gordon Growth)**:
  $$TV = \frac{FCF_5 \times (1 + g_{\text{term}})}{WACC - g_{\text{term}}} \quad (WACC > g_{\text{term}})$$
  $$PV(TV) = \frac{TV}{(1 + WACC)^5}$$
- **Enterprise & Equity Value**:
  $$\text{Enterprise Value} = PV(FCF) + PV(TV)$$
  $$\text{Equity Value} = \text{Enterprise Value} - \text{Total Debt} + \text{Cash}$$
  $$\text{Implied Share Price} = \frac{\text{Equity Value}}{\text{Shares Outstanding}}$$
- **Limitations**: Highly sensitive to discount rate ($WACC$) and terminal growth ($g_{\text{term}}$). Aegis pairs all DCF calculations with a 2D sensitivity matrix and explicit epistemic disclaimers.

---

## 3. Technical Indicators & Price Momentum

### 3.1 Relative Strength Index (RSI 14 — Wilder Smoothing)
- **Formula**:
  $$U_t = \max(0, P_t - P_{t-1}), \quad D_t = \max(0, P_{t-1} - P_t)$$
  $$\text{AvgGain}_t = \frac{\text{AvgGain}_{t-1} \times 13 + U_t}{14}$$
  $$\text{AvgLoss}_t = \frac{\text{AvgLoss}_{t-1} \times 13 + D_t}{14}$$
  $$RS = \frac{\text{AvgGain}}{\text{AvgLoss}}, \quad RSI = 100 - \frac{100}{1 + RS}$$
- **Interpretation**: $> 70$ Overbought; $< 30$ Oversold; $30 - 70$ Neutral.

### 3.2 Moving Average Convergence Divergence (MACD 12, 26, 9)
- **Fast EMA**: $\alpha = \frac{2}{12 + 1} = \frac{2}{13}$
- **Slow EMA**: $\alpha = \frac{2}{26 + 1} = \frac{2}{27}$
- **MACD Line**: $\text{EMA}_{12}(P) - \text{EMA}_{26}(P)$
- **Signal Line**: $\text{EMA}_9(\text{MACD Line})$
- **Histogram**: $\text{MACD Line} - \text{Signal Line}$

### 3.3 Bollinger Bands (20, 2)
- **Middle Band**: $SMA_{20}(P)$
- **Upper Band**: $\text{Middle} + 2 \times \sigma_{20}$
- **Lower Band**: $\text{Middle} - 2 \times \sigma_{20}$
- **Bandwidth**: $\frac{\text{Upper} - \text{Lower}}{\text{Middle}}$

### 3.4 Average True Range (ATR 14)
- **True Range**: $TR = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$
- **Wilder Smoothing**: $ATR_t = \frac{ATR_{t-1} \times 13 + TR_t}{14}$

### 3.5 Annualized Historical Volatility
- **Formula**:
  $$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$
  where $\sigma_{\text{daily}}$ is the sample standard deviation of logarithmic or daily percentage returns over a rolling window (20, 60, or 252 trading days).

---

## 4. Quantitative Equity Style Factors

Aegis computes 7 standard style factor exposures with Z-score standardization and universe percentile ranking:

1. **Momentum**: 12-month return minus recent 1-month return and price-to-200 SMA spread.
2. **Value**: Composite of Earnings Yield ($E/P$), Book-to-Market ($B/M$), and FCF Yield ($FCF / P$).
3. **Quality**: Composite of ROE, ROIC, operating margin, and Sloan accrual integrity.
4. **Size**: Natural logarithm of Market Capitalization ($\ln(\text{Market Cap})$).
5. **Low Volatility**: Inverted 252-day annualized price volatility (higher score = lower variance).
6. **Growth**: 3-Year revenue CAGR and YoY top-line expansion.
7. **Liquidity**: Estimated average daily dollar trading volume ($ADV = \text{Price} \times \text{Volume}$).

### Normalization Formula
$$z = \frac{x - \mu_{\text{bench}}}{\sigma_{\text{bench}}}$$
$$\text{Percentile Rank} = \Phi(z) \times 100$$
where $\Phi(z)$ is the standard normal cumulative distribution function.
