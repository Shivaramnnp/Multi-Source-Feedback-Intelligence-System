"""
Feedback SQLAlchemy model.

Defines the `feedbacks` table with all fields for storing user feedback,
including category, sentiment, priority, source, and status tracking.
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Feedback(Base):
    """ORM model representing a single feedback entry."""

    __tablename__ = "feedbacks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    text = Column(Text, nullable=False)
    rating = Column(
        Integer,
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_feedback_rating_range"),
        nullable=False,
    )
    category = Column(
        String(50),
        nullable=False,
        comment="One of: bug, feature, improvement, complaint, praise, other",
    )
    sentiment = Column(
        String(50),
        nullable=False,
        comment="One of: positive, negative, neutral, mixed",
    )
    priority = Column(
        String(50),
        nullable=False,
        comment="One of: low, medium, high, critical",
    )
    source = Column(
        String(50),
        nullable=False,
        comment="One of: web, email, api, social, support",
    )
    status = Column(
        String(50),
        nullable=False,
        default="new",
        server_default="new",
        comment="One of: new, in_review, addressed, dismissed",
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

    def __repr__(self) -> str:
        return (
            f"<Feedback(id={self.id}, category={self.category}, "
            f"sentiment={self.sentiment}, priority={self.priority}, "
            f"status={self.status})>"
        )
