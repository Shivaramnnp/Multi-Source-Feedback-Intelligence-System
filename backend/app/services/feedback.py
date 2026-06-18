"""
Feedback service — business logic layer.

Orchestrates repository calls and applies domain rules.
"""

from datetime import datetime
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.handlers import FeedbackNotFoundError
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStats,
    FeedbackUpdate,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    """Business logic layer for feedback operations."""

    @staticmethod
    async def create_feedback(db: AsyncSession, data: FeedbackCreate) -> FeedbackResponse:
        """Create a new feedback entry."""
        feedback = await FeedbackRepository.create(db, data)
        return FeedbackResponse.model_validate(feedback)

    @staticmethod
    async def get_feedback(db: AsyncSession, feedback_id: UUID) -> FeedbackResponse:
        """Get a single feedback by ID. Raises FeedbackNotFoundError if not found."""
        feedback = await FeedbackRepository.get_by_id(db, feedback_id)
        if not feedback:
            raise FeedbackNotFoundError(str(feedback_id))
        return FeedbackResponse.model_validate(feedback)

    @staticmethod
    async def get_feedbacks(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        category: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
    ) -> FeedbackListResponse:
        """Get paginated feedback list with optional filters."""
        skip = (page - 1) * size
        items, total = await FeedbackRepository.get_all(
            db, skip=skip, limit=size,
            category=category, status=status,
            priority=priority, sentiment=sentiment,
        )
        return FeedbackListResponse(
            items=[FeedbackResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
        )

    @staticmethod
    async def update_feedback(
        db: AsyncSession, feedback_id: UUID, data: FeedbackUpdate
    ) -> FeedbackResponse:
        """Update a feedback entry. Raises FeedbackNotFoundError if not found."""
        feedback = await FeedbackRepository.update(db, feedback_id, data)
        if not feedback:
            raise FeedbackNotFoundError(str(feedback_id))
        return FeedbackResponse.model_validate(feedback)

    @staticmethod
    async def delete_feedback(db: AsyncSession, feedback_id: UUID) -> None:
        """Delete a feedback entry. Raises FeedbackNotFoundError if not found."""
        deleted = await FeedbackRepository.delete(db, feedback_id)
        if not deleted:
            raise FeedbackNotFoundError(str(feedback_id))

    @staticmethod
    async def get_feedback_stats(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
    ) -> FeedbackStats:
        """Get aggregated feedback statistics for the dashboard."""
        stats = await FeedbackRepository.get_stats(
            db,
            start_date=start_date,
            end_date=end_date,
            category=category,
            priority=priority,
            sentiment=sentiment,
        )
        stats["recent_feedback"] = [
            FeedbackResponse.model_validate(f) for f in stats["recent_feedback"]
        ]
        return FeedbackStats(**stats)
