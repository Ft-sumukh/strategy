"""
AEGIS INVEST — News Data Provider Abstraction & Demo Implementation
Provides normalized news articles, entity extraction, and event classifications.
Ensures zero hallucinated breaking news: all demo articles are clearly attributed
as deterministic historical demo records.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class NormalizedArticle(BaseModel):
    id: str
    headline: str
    summary: str
    content: str
    publisher: str
    source: str = "SEC_EDGAR_DEMO"
    url: Optional[str] = None
    published_at: datetime
    retrieved_at: datetime
    ticker: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "USA"
    category: str = "UNKNOWN"
    language: str = "en"
    content_hash: str
    data_source: str = "demo_historical"
    data_version: str = "1.0"
    quality_status: str = "AUDITED"
    is_synthetic: bool = True
    entities: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    sentiment: str = "NEUTRAL"
    sentiment_score: float = 0.0


class NewsProvider(ABC):
    """Abstract interface for financial news providers."""

    @abstractmethod
    async def search_news(
        self,
        query: Optional[str] = None,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NormalizedArticle]:
        pass

    @abstractmethod
    async def get_company_news(self, ticker: str, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        pass

    @abstractmethod
    async def get_market_news(self, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        pass

    @abstractmethod
    async def get_sector_news(self, sector: str, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        pass


def _hash_content(headline: str, publisher: str, published_at: str) -> str:
    raw = f"{headline.strip()}|{publisher.strip()}|{published_at.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class DemoNewsProvider(NewsProvider):
    """Deterministic audited news provider with historical news timeline for flagship assets."""

    def __init__(self):
        base_time = datetime(2025, 2, 1, 14, 0, tzinfo=timezone.utc)
        raw_items = [
            {
                "id": "art-001",
                "headline": "NVIDIA Reports Record Q4 Revenue of $22.1B Driven by Data Center AI Acceleration",
                "summary": "NVIDIA posted fiscal fourth quarter revenue up 265% year-over-year, beating consensus expectations behind surging demand for Hopper architecture GPUs.",
                "content": "SANTA CLARA, Calif. — NVIDIA Corporation reported record financial results for its fourth quarter. Compute and networking revenue drove massive gross margin expansion, exceeding 76%. Management highlighted enterprise LLM training and inferencing workloads.",
                "publisher": "SEC EDGAR / Press",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
                "published_at": base_time - timedelta(days=2),
                "ticker": "NVDA",
                "sector": "Technology",
                "industry": "Semiconductors",
                "category": "EARNINGS",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.85,
                "entities": [
                    {"entity_type": "Company", "entity_name": "NVIDIA Corporation", "confidence": 1.0},
                    {"entity_type": "Ticker", "entity_name": "NVDA", "confidence": 1.0},
                    {"entity_type": "Product", "entity_name": "Hopper GPU", "confidence": 0.95},
                ],
                "events": [
                    {"event_type": "Earnings Beat", "event_date": base_time - timedelta(days=2), "confidence": 0.98}
                ],
            },
            {
                "id": "art-002",
                "headline": "Apple Expands Services Ecosystem and Authorizes Additional $110B Share Repurchase",
                "summary": "Apple delivered all-time high Services revenue of $23.9B and approved the largest share buyback program in U.S. corporate history.",
                "content": "CUPERTINO, Calif. — Apple Inc. announced financial results for its fiscal quarter. The board of directors declared a cash dividend and authorized an additional $110 billion for share repurchases, reflecting continued fortress balance sheet strength.",
                "publisher": "Bloomberg / Dow Jones",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
                "published_at": base_time - timedelta(days=5),
                "ticker": "AAPL",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "category": "CAPITAL_ALLOCATION",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.72,
                "entities": [
                    {"entity_type": "Company", "entity_name": "Apple Inc.", "confidence": 1.0},
                    {"entity_type": "Ticker", "entity_name": "AAPL", "confidence": 1.0},
                ],
                "events": [
                    {"event_type": "Capital Allocation", "event_date": base_time - timedelta(days=5), "confidence": 0.95}
                ],
            },
            {
                "id": "art-003",
                "headline": "Microsoft Azure Cloud Growth Re-accelerates to 31% YoY Powered by Enterprise Copilot Ingestion",
                "summary": "Microsoft Corporation posted strong second-quarter results with Intelligent Cloud revenue climbing, bolstered by 6 points of AI-driven cloud consumption.",
                "content": "REDMOND, Wash. — Microsoft Corp. reported revenue of $62.0 billion. CEO Satya Nadella noted Azure gained market share as enterprises deployed generative AI tools across hybrid environments.",
                "publisher": "Reuters Financial",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
                "published_at": base_time - timedelta(days=8),
                "ticker": "MSFT",
                "sector": "Technology",
                "industry": "Software—Infrastructure",
                "category": "EARNINGS",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.78,
                "entities": [
                    {"entity_type": "Company", "entity_name": "Microsoft Corporation", "confidence": 1.0},
                    {"entity_type": "Ticker", "entity_name": "MSFT", "confidence": 1.0},
                    {"entity_type": "Person", "entity_name": "Satya Nadella", "confidence": 0.95},
                ],
                "events": [
                    {"event_type": "Earnings Beat", "event_date": base_time - timedelta(days=8), "confidence": 0.92}
                ],
            },
            {
                "id": "art-004",
                "headline": "Alphabet Introduces Gemini 1.5 Pro with 1 Million Token Context Window Across Cloud Infrastructure",
                "summary": "Google Cloud unveiled major multimodal foundation model upgrades with breakthrough context processing capabilities for enterprise customers.",
                "content": "MOUNTAIN VIEW, Calif. — Alphabet Inc. announced next-generation AI model Gemini 1.5 Pro. The architecture features a dramatic expansion in context window capability, processing 1 hour of video or 700,000 words in a single prompt.",
                "publisher": "TechCrunch / PR Newswire",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
                "published_at": base_time - timedelta(days=12),
                "ticker": "GOOG",
                "sector": "Communication Services",
                "industry": "Internet Content & Information",
                "category": "PRODUCT",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.65,
                "entities": [
                    {"entity_type": "Company", "entity_name": "Alphabet Inc.", "confidence": 1.0},
                    {"entity_type": "Ticker", "entity_name": "GOOG", "confidence": 1.0},
                    {"entity_type": "Product", "entity_name": "Gemini 1.5 Pro", "confidence": 0.99},
                ],
                "events": [
                    {"event_type": "Product Launch", "event_date": base_time - timedelta(days=12), "confidence": 0.95}
                ],
            },
            {
                "id": "art-005",
                "headline": "Amazon AWS Operating Margins Expand to 29.6% Following Cost Realignment and High-Margin Cloud Demand",
                "summary": "Amazon.com Inc. reported operating income doubling year-over-year, led by fulfillment efficiency gains and AWS re-acceleration.",
                "content": "SEATTLE, Wash. — Amazon.com Inc. posted strong fourth quarter operating results. Andy Jassy noted regional fulfillment network restructuring lowered cost-to-serve while AWS annualized run rate approached $100 billion.",
                "publisher": "Wall Street Journal",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.sec.gov/edgar/searchedgar/companysearch",
                "published_at": base_time - timedelta(days=15),
                "ticker": "AMZN",
                "sector": "Consumer Cyclical",
                "industry": "Internet Retail",
                "category": "EARNINGS",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.70,
                "entities": [
                    {"entity_type": "Company", "entity_name": "Amazon.com Inc.", "confidence": 1.0},
                    {"entity_type": "Ticker", "entity_name": "AMZN", "confidence": 1.0},
                    {"entity_type": "Person", "entity_name": "Andy Jassy", "confidence": 0.95},
                ],
                "events": [
                    {"event_type": "Earnings Beat", "event_date": base_time - timedelta(days=15), "confidence": 0.90}
                ],
            },
            {
                "id": "art-006",
                "headline": "Federal Reserve Holds Benchmark Rate Steady at 5.25%-5.50%, Citing Balanced Risks to Inflation and Employment",
                "summary": "FOMC leaves target rate unchanged at 22-year high, reiterating that committee seeks greater confidence inflation is moving sustainably toward 2% before cutting.",
                "content": "WASHINGTON — The Federal Open Market Committee maintained the target range for the federal funds rate at 5.25 to 5.50 percent. Chair Jerome Powell indicated economic activity has expanded at a solid pace and job gains remain strong.",
                "publisher": "Federal Reserve Board",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.federalreserve.gov",
                "published_at": base_time - timedelta(days=18),
                "ticker": None,
                "sector": "Macroeconomic",
                "industry": "Central Banking",
                "category": "MACRO",
                "sentiment": "NEUTRAL",
                "sentiment_score": 0.05,
                "entities": [
                    {"entity_type": "Organization", "entity_name": "Federal Reserve", "confidence": 1.0},
                    {"entity_type": "Person", "entity_name": "Jerome Powell", "confidence": 0.98},
                ],
                "events": [
                    {"event_type": "Macro Event", "event_date": base_time - timedelta(days=18), "confidence": 0.99}
                ],
            },
            {
                "id": "art-007",
                "headline": "EU Antitrust Regulators Initiate Scrutiny into Big Tech AI Partnerships and Licensing Agreements",
                "summary": "European Commission issues information requests regarding multi-billion cloud partnerships and exclusive computing capacity agreements.",
                "content": "BRUSSELS — European antitrust watchdogs are evaluating whether strategic alliances between mega-cap cloud providers and leading AI frontier labs trigger merger control thresholds under EU regulations.",
                "publisher": "Financial Times",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.ft.com",
                "published_at": base_time - timedelta(days=22),
                "ticker": "MSFT",
                "sector": "Technology",
                "industry": "Software—Infrastructure",
                "category": "REGULATION",
                "sentiment": "NEGATIVE",
                "sentiment_score": -0.45,
                "entities": [
                    {"entity_type": "Organization", "entity_name": "European Commission", "confidence": 0.95},
                    {"entity_type": "Company", "entity_name": "Microsoft Corporation", "confidence": 0.85},
                ],
                "events": [
                    {"event_type": "Regulatory Action", "event_date": base_time - timedelta(days=22), "confidence": 0.88}
                ],
            },
            {
                "id": "art-008",
                "headline": "U.S. Headline Inflation Cools to 2.9% YoY as Energy and Used Vehicle Prices Moderate",
                "summary": "Bureau of Labor Statistics CPI release confirms continuing disinflationary trajectory toward Federal Reserve target, supporting soft landing thesis.",
                "content": "WASHINGTON — The Consumer Price Index for All Urban Consumers increased 2.9 percent over the last 12 months, the smallest 12-month increase since early 2021. Core CPI advanced 3.2 percent annualized.",
                "publisher": "Bureau of Labor Statistics",
                "source": "SEC_EDGAR_DEMO",
                "url": "https://www.bls.gov/cpi",
                "published_at": base_time - timedelta(days=25),
                "ticker": None,
                "sector": "Macroeconomic",
                "industry": "Economic Indicators",
                "category": "MACRO",
                "sentiment": "POSITIVE",
                "sentiment_score": 0.40,
                "entities": [
                    {"entity_type": "Organization", "entity_name": "Bureau of Labor Statistics", "confidence": 1.0},
                ],
                "events": [
                    {"event_type": "Macro Event", "event_date": base_time - timedelta(days=25), "confidence": 0.95}
                ],
            },
        ]

        self._articles: List[NormalizedArticle] = []
        for raw in raw_items:
            pub_str = raw["published_at"].isoformat()
            c_hash = _hash_content(raw["headline"], raw["publisher"], pub_str)
            self._articles.append(NormalizedArticle(
                id=raw["id"],
                headline=raw["headline"],
                summary=raw["summary"],
                content=raw["content"],
                publisher=raw["publisher"],
                source=raw["source"],
                url=raw["url"],
                published_at=raw["published_at"],
                retrieved_at=raw["published_at"] + timedelta(minutes=5),
                ticker=raw["ticker"],
                sector=raw["sector"],
                industry=raw["industry"],
                category=raw["category"],
                language="en",
                content_hash=c_hash,
                data_source="demo_historical",
                data_version="1.0",
                quality_status="AUDITED",
                is_synthetic=True,
                entities=raw["entities"],
                events=raw["events"],
                sentiment=raw["sentiment"],
                sentiment_score=raw["sentiment_score"],
            ))

    async def search_news(
        self,
        query: Optional[str] = None,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NormalizedArticle]:
        res = self._articles
        if ticker:
            res = [a for a in res if a.ticker and a.ticker.upper() == ticker.upper()]
        if sector:
            res = [a for a in res if a.sector and sector.lower() in a.sector.lower()]
        if category:
            res = [a for a in res if a.category and a.category.upper() == category.upper()]
        if query:
            q = query.lower()
            res = [a for a in res if q in a.headline.lower() or q in a.summary.lower()]

        # Sort descending by published_at
        res = sorted(res, key=lambda a: a.published_at, reverse=True)
        return res[offset : offset + limit]

    async def get_company_news(self, ticker: str, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        return await self.search_news(ticker=ticker, limit=limit, offset=offset)

    async def get_market_news(self, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        return await self.search_news(limit=limit, offset=offset)

    async def get_sector_news(self, sector: str, limit: int = 50, offset: int = 0) -> List[NormalizedArticle]:
        return await self.search_news(sector=sector, limit=limit, offset=offset)


_provider_instance: Optional[NewsProvider] = None


def get_news_provider() -> NewsProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = DemoNewsProvider()
    return _provider_instance
