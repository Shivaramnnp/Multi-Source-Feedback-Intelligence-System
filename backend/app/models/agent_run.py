"""
SQLAlchemy models for multi-agent runs, alerts, trend anomalies, and feedback corrections.
"""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AgentActionLog(Base):
    """Logs of mock action events triggered by the Action Agent (Slack, Jira, etc)."""

    __tablename__ = "agent_action_logs"

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
    )
    action_type = Column(String(50), nullable=False, comment="slack_alert, jira_ticket, support_escalation")
    status = Column(String(20), nullable=False, default="success")
    details = Column(Text, nullable=True, comment="JSON or text payload description")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class FeedbackCorrection(Base):
    """Historical user corrections logged when overriding category, sentiment, or priority classifications."""

    __tablename__ = "feedback_corrections"

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
    )
    field_corrected = Column(String(50), nullable=False, comment="category, sentiment, priority")
    old_value = Column(String(50), nullable=False)
    new_value = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TrendSpike(Base):
    """Logs of anomalies and volume spikes detected by the Trend Agent."""

    __tablename__ = "trend_spikes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    metric = Column(String(50), nullable=False, comment="volume, category_spike, negative_sentiment_spike")
    current_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    details = Column(Text, nullable=True, comment="Detailed JSON describing the spike context")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
