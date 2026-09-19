from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import MarketOverview, PortfolioRisk, ScreenerResponse, StockProfile
from app.providers.demo import market_overview, portfolio_risk, screener, stock

app = FastAPI(title="Aegis Invest API", version="0.1.0", description="Decision-intelligence demo API. Data is synthetic unless a provider response says otherwise.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_status": "synthetic"}


@app.get("/api/v1/market/overview", response_model=MarketOverview)
def get_market_overview() -> MarketOverview:
    return market_overview()


@app.get("/api/v1/screener", response_model=ScreenerResponse)
def get_screener(min_quality: int = Query(0, ge=0, le=100), sector: str | None = None) -> ScreenerResponse:
    result = screener()
    result.results = [row for row in result.results if row.quality_score >= min_quality and (not sector or row.sector.lower() == sector.lower())]
    return result


@app.get("/api/v1/stocks/{ticker}", response_model=StockProfile)
def get_stock(ticker: str) -> StockProfile:
    return stock(ticker)


@app.get("/api/v1/portfolio/risk", response_model=PortfolioRisk)
def get_portfolio_risk() -> PortfolioRisk:
    return portfolio_risk()
