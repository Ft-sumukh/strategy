"""
AEGIS INVEST — AI Decision Intelligence & Audit Models
Defines persistent entities for AI conversations, structured tool calls,
extracted evidence, and immutable audit logs.
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utc_now


class AIConversation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Container for multi-turn research assistant sessions."""
    __tablename__ = "ai_conversations"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="Investment Research Session")
    subject_ticker: Mapped[str] = mapped_column(String(20), nullable=True, index=True)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False, default="research_v1")
    model_name: Mapped[str] = mapped_column(String(50), nullable=False, default="aegis-institutional-v1")
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    messages: Mapped[list["AIMessage"]] = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin"
    )


class AIMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Single turn message in an AI research conversation."""
    __tablename__ = "ai_messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, tool, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # Structured evidence citations
    uncertainty_statement: Mapped[str] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    conversation: Mapped[AIConversation] = relationship("AIConversation", back_populates="messages")
    tool_calls: Mapped[list["AIToolCall"]] = relationship(
        "AIToolCall", back_populates="message", cascade="all, delete-orphan", lazy="selectin"
    )


class AIToolCall(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Record of a controlled deterministic analytical tool invoked by the AI layer."""
    __tablename__ = "ai_tool_calls"

    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ai_messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_summary: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SUCCESS")  # SUCCESS, FAILED, TIMEOUT
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    message: Mapped[AIMessage] = relationship("AIMessage", back_populates="tool_calls")


class AIEvidence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Traceable, normalized piece of financial evidence linked to citations."""
    __tablename__ = "ai_evidence"

    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # FINANCIAL_STATEMENT, VALUATION, TECHNICALS, FACTOR, NEWS, MACRO, REGIME, RISK, BACKTEST
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    metric: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="FACT")  # FACT, CALCULATION, MODEL_OUTPUT, INTERPRETATION, SCENARIO, ASSUMPTION, UNCERTAINTY
    provenance_hash: Mapped[str] = mapped_column(String(64), nullable=True)


class AIAuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable audit trail of AI generation requests and security verifications."""
    __tablename__ = "ai_audit_logs"

    request_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, default="default_user", index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(30), nullable=False)
    tools_invoked: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    security_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PASSED")
