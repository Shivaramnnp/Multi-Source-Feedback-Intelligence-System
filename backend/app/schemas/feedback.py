"""
Feedback Pydantic schemas.

Defines request/response models and enums for the feedback domain,
including create, update, response, list, and statistics schemas.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CategoryEnum(str, Enum):
    """Valid feedback categories."""

    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    OTHER = "other"


class SentimentEnum(str, Enum):
    """Valid sentiment classifications."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class PriorityEnum(str, Enum):
    """Valid priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceEnum(str, Enum):
    """Valid feedback sources."""

    WEB = "web"
    EMAIL = "email"
    API = "api"
    SOCIAL = "social"
    SUPPORT = "support"


class StatusEnum(str, Enum):
    """Valid feedback statuses."""

    NEW = "new"
    IN_REVIEW = "in_review"
    ADDRESSED = "addressed"
    DISMISSED = "dismissed"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    """Schema for creating a new feedback entry."""

    text: str = Field(..., min_length=1, description="The feedback text content.")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5.")
    category: CategoryEnum = Field(..., description="Feedback category.")
    sentiment: SentimentEnum = Field(..., description="Sentiment classification.")
    priority: PriorityEnum = Field(..., description="Priority level.")
    source: SourceEnum = Field(..., description="Source of the feedback.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "The new dashboard is really intuitive and fast!",
                "rating": 5,
                "category": "praise",
                "sentiment": "positive",
                "priority": "low",
                "source": "web",
            }
        }
    )


class FeedbackUpdate(BaseModel):
    """Schema for updating an existing feedback entry. All fields are optional."""

    text: str | None = Field(None, min_length=1, description="The feedback text content.")
    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1 to 5.")
    category: CategoryEnum | None = Field(None, description="Feedback category.")
    sentiment: SentimentEnum | None = Field(None, description="Sentiment classification.")
    priority: PriorityEnum | None = Field(None, description="Priority level.")
    source: SourceEnum | None = Field(None, description="Source of the feedback.")
    status: StatusEnum | None = Field(None, description="Feedback status.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_review",
                "priority": "high",
            }
        }
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FeedbackResponse(BaseModel):
    """Schema for a single feedback response."""

    id: UUID
    text: str
    rating: int
    category: CategoryEnum
    sentiment: SentimentEnum
    priority: PriorityEnum
    source: SourceEnum
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    """Paginated list response for feedback entries."""

    items: list[FeedbackResponse]
    total: int
    page: int
    size: int


class FeedbackStats(BaseModel):
    """Aggregated statistics for all feedback entries."""

    total_count: int
    average_rating: float
    sentiment_distribution: dict[str, int]
    category_distribution: dict[str, int]
    priority_distribution: dict[str, int]
    status_distribution: dict[str, int]
    rating_distribution: dict[str, int]
    trends: list[dict]
    priority_heatmap: dict[str, dict[str, int]]
    recent_feedback: list[FeedbackResponse]
