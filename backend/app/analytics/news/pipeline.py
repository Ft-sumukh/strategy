"""
AEGIS INVEST — News Processing & NLP Pipeline
Modular stages:
Raw Text -> Sanitization -> Language Check -> Entity Extraction ->
Category Classification -> Event Extraction -> Content Hashing.

SECURITY PRINCIPLE (§ 18):
All external news text is treated as UNTRUSTED DATA.
Content is sanitized and isolated to prevent prompt injection or control hijacking.
"""

from datetime import datetime, timezone
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel


class ExtractedEntity(BaseModel):
    entity_type: str  # Company, Ticker, Person, Organization, Sector, Product, Currency
    entity_name: str
    confidence: float = 1.0


class ExtractedEvent(BaseModel):
    event_type: str  # Earnings Beat, Earnings Miss, Guidance Change, M&A, Leadership Change, etc.
    event_date: datetime
    confidence: float = 1.0
    details: Optional[str] = None


class ProcessedArticle(BaseModel):
    cleaned_headline: str
    cleaned_summary: str
    cleaned_content: str
    language: str
    category: str
    content_hash: str
    entities: List[ExtractedEntity]
    events: List[ExtractedEvent]


class NewsProcessingPipeline:
    """Modular, deterministic financial NLP pipeline."""

    # Pre-compiled entity dictionaries for flagship assets and macro institutions
    KNOWN_ENTITIES: List[Tuple[re.Pattern, str, str]] = [
        # (Pattern, Entity Type, Normalized Name)
        (re.compile(r"\b(NVIDIA|NVDA|Nvidia Corp)\b", re.I), "Company", "NVIDIA"),
        (re.compile(r"\bNVDA\b"), "Ticker", "NVDA"),
        (re.compile(r"\b(Apple|AAPL|Apple Inc)\b", re.I), "Company", "Apple"),
        (re.compile(r"\bAAPL\b"), "Ticker", "AAPL"),
        (re.compile(r"\b(Microsoft|MSFT|Microsoft Corp)\b", re.I), "Company", "Microsoft"),
        (re.compile(r"\bMSFT\b"), "Ticker", "MSFT"),
        (re.compile(r"\b(Alphabet|Google|GOOGL|GOOG)\b", re.I), "Company", "Google"),
        (re.compile(r"\bGOOG\b"), "Ticker", "GOOG"),
        (re.compile(r"\b(Amazon|AMZN|Amazon\.com)\b", re.I), "Company", "Amazon"),
        (re.compile(r"\bAMZN\b"), "Ticker", "AMZN"),
        (re.compile(r"\b(Federal Reserve|Fed|FOMC)\b", re.I), "Organization", "Federal Reserve"),
        (re.compile(r"\b(Jerome Powell|Chair Powell)\b", re.I), "Person", "Jerome Powell"),
        (re.compile(r"\b(Satya Nadella)\b", re.I), "Person", "Satya Nadella"),
        (re.compile(r"\b(Tim Cook)\b", re.I), "Person", "Tim Cook"),
        (re.compile(r"\b(Jensen Huang)\b", re.I), "Person", "Jensen Huang"),
        (re.compile(r"\b(Andy Jassy)\b", re.I), "Person", "Andy Jassy"),
        (re.compile(r"\b(Sundar Pichai)\b", re.I), "Person", "Sundar Pichai"),
        (re.compile(r"\b(Hopper|Blackwell)\b", re.I), "Product", "NVIDIA GPU"),
        (re.compile(r"\b(Azure|Microsoft Cloud)\b", re.I), "Product", "Microsoft Azure"),
        (re.compile(r"\b(AWS|Amazon Web Services)\b", re.I), "Product", "Amazon AWS"),
        (re.compile(r"\b(Gemini|Gemini 1\.5)\b", re.I), "Product", "Google Gemini"),
        (re.compile(r"\b(iPhone|Mac|iPad|Apple Services)\b", re.I), "Product", "Apple Device/Service"),
        (re.compile(r"\b(Treasury|US Treasury)\b", re.I), "Organization", "U.S. Department of the Treasury"),
        (re.compile(r"\b(Bureau of Labor Statistics|BLS)\b", re.I), "Organization", "Bureau of Labor Statistics"),
        (re.compile(r"(\$|\bUSD\b|\bBillion\b|\bMillion\b)", re.I), "Currency", "USD"),
    ]

    # Category patterns
    CATEGORY_PATTERNS: List[Tuple[re.Pattern, str]] = [
        (re.compile(r"\b(earnings|revenue|quarterly results|q[1-4]|eps|net income|profit)\b", re.I), "EARNINGS"),
        (re.compile(r"\b(merger|acquisition|acquire|buyout|deal|takeover)\b", re.I), "M&A"),
        (re.compile(r"\b(ceo|cfo|executive|leadership|appoint|resign|board of directors)\b", re.I), "MANAGEMENT"),
        (re.compile(r"\b(antitrust|sec|ftc|investigation|probe|regulatory|subpoena|compliance)\b", re.I), "REGULATION"),
        (re.compile(r"\b(launch|unveil|release|announces|new chip|architecture|gemini|gpu)\b", re.I), "PRODUCT"),
        (re.compile(r"\b(lawsuit|court|patent|settlement|litigation|judge)\b", re.I), "LEGAL"),
        (re.compile(r"\b(rate|inflation|cpi|gdp|fomc|central bank|yield|recession)\b", re.I), "MACRO"),
        (re.compile(r"\b(supply chain|foundry|tsmc|shortage|supplier|component)\b", re.I), "SUPPLY_CHAIN"),
        (re.compile(r"\b(guidance|forecast|outlook|fiscal year|target)\b", re.I), "GUIDANCE"),
        (re.compile(r"\b(buyback|dividend|repurchase|share buyback|capital allocation)\b", re.I), "CAPITAL_ALLOCATION"),
    ]

    # Event patterns
    EVENT_PATTERNS: List[Tuple[re.Pattern, str]] = [
        (re.compile(r"\b(beat|record revenue|exceeds expectations|outperforms|beats)\b", re.I), "EARNINGS_BEAT"),
        (re.compile(r"\b(miss|below expectations|revenue drop|decline in profit)\b", re.I), "EARNINGS_MISS"),
        (re.compile(r"\b(raises guidance|cuts guidance|updates outlook)\b", re.I), "GUIDANCE_CHANGE"),
        (re.compile(r"\b(to acquire|acquisition agreement|all-cash deal)\b", re.I), "M&A"),
        (re.compile(r"\b(named ceo|steps down|resigns|appointed)\b", re.I), "LEADERSHIP_CHANGE"),
        (re.compile(r"\b(scrutiny|probe launched|antitrust review|inquiry)\b", re.I), "REGULATORY_ACTION"),
        (re.compile(r"\b(unveils|launches|introduces next-gen)\b", re.I), "PRODUCT_LAUNCH"),
        (re.compile(r"\b(authorizes buyback|declares dividend|repurchase program|boosts quarterly dividend|buyback)\b", re.I), "CAPITAL_ALLOCATION"),
        (re.compile(r"\b(fomc meeting|rate decision|cpi cools|inflation data)\b", re.I), "MACRO_EVENT"),
    ]

    def sanitize_text(self, text: Optional[str]) -> str:
        """Sanitizes text by stripping HTML tags, control codes, and potential prompt injections."""
        if not text:
            return ""
        # 1. Strip HTML tags
        clean = re.sub(r"<[^>]*>", "", text)
        # 2. Strip null bytes and non-printable control characters
        clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", clean)
        # 3. Neutralize common prompt-injection substrings
        clean = re.sub(r"(?i)ignore\s+previous\s+instructions", "[BLOCKED_INSTRUCTION]", clean)
        clean = re.sub(r"(?i)system\s+prompt", "[BLOCKED_INSTRUCTION]", clean)
        # 4. Normalize whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def detect_language(self, text: str) -> str:
        """Deterministic language checker (defaults to 'en' for latin financial corpus)."""
        if not text:
            return "en"
        # Check non-ascii character ratio
        non_ascii = len([c for c in text if ord(c) > 127])
        if non_ascii / len(text) > 0.4:
            return "other"
        return "en"

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extracts named entities using deterministic regex dictionary matching."""
        entities: List[ExtractedEntity] = []
        seen = set()

        for pattern, ent_type, ent_name in self.KNOWN_ENTITIES:
            if pattern.search(text):
                key = (ent_type, ent_name)
                if key not in seen:
                    seen.add(key)
                    entities.append(ExtractedEntity(entity_type=ent_type, entity_name=ent_name, confidence=0.98))

        return entities

    def classify_category(self, text: str) -> str:
        """Classifies the news text into a standardized financial category."""
        for pattern, cat in self.CATEGORY_PATTERNS:
            if pattern.search(text):
                return cat
        return "OTHER"

    def extract_events(self, text: str, published_at: datetime) -> List[ExtractedEvent]:
        """Identifies corporate and macroeconomic events from text."""
        events: List[ExtractedEvent] = []
        seen = set()

        for pattern, evt_type in self.EVENT_PATTERNS:
            if pattern.search(text):
                if evt_type not in seen:
                    seen.add(evt_type)
                    events.append(ExtractedEvent(
                        event_type=evt_type,
                        event_date=published_at,
                        confidence=0.95,
                        details=f"Extracted from text matching pattern for {evt_type}",
                    ))

        return events

    def compute_content_hash(self, headline: str, content: str = "") -> str:
        """Computes SHA-256 deduplication hash for headline and content."""
        raw = f"{headline.strip()}|{content.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def generate_content_hash(self, headline: str, publisher: str, published_at: datetime) -> str:
        """Computes SHA-256 deduplication hash."""
        raw = f"{headline.strip()}|{publisher.strip()}|{published_at.isoformat()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def process_raw_article(
        self,
        raw_id: str,
        headline: str,
        content: str,
        source: str = "Unknown",
        url: str = "",
        published_at: Optional[Any] = None,
        ticker_hint: Optional[str] = None,
    ) -> Any:
        """Convenience method matching test interface for processing raw articles."""
        dt = datetime.now(timezone.utc)
        if isinstance(published_at, str):
            try:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except Exception:
                pass
        elif isinstance(published_at, datetime):
            dt = published_at

        processed = self.process(headline=headline, content=content, publisher=source, published_at=dt)
        
        # Calculate heuristic sentiment
        pos_terms = ["beat", "beats", "record", "growth", "boosts", "dividend", "buyback", "exceeds"]
        neg_terms = ["miss", "misses", "decline", "drop", "probe", "antitrust", "lawsuit", "slumps"]
        score = 0.0
        txt = f"{headline} {content}".lower()
        for p in pos_terms:
            if p in txt:
                score += 0.2
        for n in neg_terms:
            if n in txt:
                score -= 0.2
        score = max(-1.0, min(1.0, score))
        sentiment = "POSITIVE" if score > 0.05 else ("NEGATIVE" if score < -0.05 else "NEUTRAL")

        class ProcessedRawResult:
            def __init__(self, p: ProcessedArticle, score: float, sent: str):
                self.category = p.category
                self.events = p.events
                self.entities = p.entities
                self.cleaned_headline = p.cleaned_headline
                self.cleaned_content = p.cleaned_content
                self.content_hash = p.content_hash
                self.sentiment_score = score
                self.sentiment = sent

        return ProcessedRawResult(processed, score, sentiment)

    def process(
        self,
        headline: str,
        summary: Optional[str] = None,
        content: Optional[str] = None,
        publisher: str = "Unknown",
        published_at: Optional[datetime] = None,
    ) -> ProcessedArticle:
        """Runs the complete modular NLP pipeline over an incoming article."""
        if published_at is None:
            published_at = datetime.now(timezone.utc)

        clean_h = self.sanitize_text(headline)
        clean_s = self.sanitize_text(summary)
        clean_c = self.sanitize_text(content)

        combined_text = f"{clean_h} {clean_s} {clean_c}"
        lang = self.detect_language(combined_text)
        entities = self.extract_entities(combined_text)
        category = self.classify_category(combined_text)
        events = self.extract_events(combined_text, published_at)
        c_hash = self.generate_content_hash(clean_h, publisher, published_at)

        return ProcessedArticle(
            cleaned_headline=clean_h,
            cleaned_summary=clean_s,
            cleaned_content=clean_c,
            language=lang,
            category=category,
            content_hash=c_hash,
            entities=entities,
            events=events,
        )
