"""
Intelligence service — bridges the pipeline with the feedback service.

Provides async methods for analyzing feedback and storing results.
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.pipeline import AnalysisResult, get_pipeline
from app.models.feedback import Feedback
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import FeedbackUpdate

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Service for running intelligence analysis on feedback entries."""

    @staticmethod
    def analyze_text(text: str, rating: int | None = None) -> AnalysisResult:
        """Run the intelligence pipeline on raw text."""
        pipeline = get_pipeline()
        return pipeline.process(text, rating=rating)

    @staticmethod
    async def analyze_and_update(
        db: AsyncSession,
        feedback_id: UUID,
    ) -> AnalysisResult:
        """Run analysis on an existing feedback entry and update it in the database."""
        feedback = await FeedbackRepository.get_by_id(db, feedback_id)
        if not feedback:
            from app.exceptions.handlers import FeedbackNotFoundError
            raise FeedbackNotFoundError(str(feedback_id))

        result = IntelligenceService.analyze_text(feedback.text, rating=feedback.rating)

        # Map the pipeline category to schema-compatible value
        category_map = {
            "bug": "bug",
            "feature_request": "feature",
            "praise": "praise",
            "complaint": "complaint",
            "support": "other",
        }
        mapped_category = category_map.get(result.category.category, "other")

        update_data = FeedbackUpdate(
            sentiment=result.sentiment.label,
            category=mapped_category,
            priority=result.priority.priority,
        )
        await FeedbackRepository.update(db, feedback_id, update_data)
        logger.info(
            "Updated feedback %s with analysis: sentiment=%s category=%s priority=%s",
            feedback_id, result.sentiment.label, mapped_category, result.priority.priority,
        )
        return result

    @staticmethod
    async def analyze_and_create(
        db: AsyncSession,
        text: str,
        rating: int,
        source: str,
    ) -> tuple[Feedback, AnalysisResult]:
        """Analyze text and create a new feedback entry with auto-filled fields."""
        result = IntelligenceService.analyze_text(text, rating=rating)

        category_map = {
            "bug": "bug",
            "feature_request": "feature",
            "praise": "praise",
            "complaint": "complaint",
            "support": "other",
        }
        mapped_category = category_map.get(result.category.category, "other")

        from app.schemas.feedback import FeedbackCreate
        create_data = FeedbackCreate(
            text=text,
            rating=rating,
            category=mapped_category,
            sentiment=result.sentiment.label,
            priority=result.priority.priority,
            source=source,
        )
        feedback = await FeedbackRepository.create(db, create_data)
        logger.info("Created feedback %s with auto-analysis.", feedback.id)
        return feedback, result
