"""
AI Analysis database model.

Stores AI-generated analysis results for feedback entries with caching support.
"""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AIAnalysis(Base):
    """ORM model for AI-generated feedback analysis results."""

    __tablename__ = "ai_analyses"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    feedback_id = Column(
        UUID(as_uuid=True),
        ForeignKey("feedbacks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    provider = Column(
        String(50),
        nullable=False,
        comment="AI provider used: mock, openai, gemini, claude",
    )
    model_name = Column(
        String(100),
        nullable=False,
        comment="Specific model name used for analysis",
    )
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    business_impact = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    priority_reason = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    prompt_tokens = Column(String(20), nullable=True, comment="Token count for the prompt")
    completion_tokens = Column(String(20), nullable=True, comment="Token count for the completion")
    processing_time_ms = Column(Float, nullable=True, comment="Processing time in milliseconds")
    cached = Column(
        String(10),
        nullable=False,
        default="false",
        server_default="false",
        comment="Whether this result was served from cache",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship
    feedback = relationship("Feedback", backref="ai_analysis", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<AIAnalysis(id={self.id}, feedback_id={self.feedback_id}, "
            f"provider={self.provider}, model={self.model_name})>"
        )
