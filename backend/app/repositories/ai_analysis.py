"""
AI Analysis repository — data access layer.

Provides async CRUD operations for AI analysis results with caching support.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analysis import AIAnalysis

logger = logging.getLogger(__name__)


class AIAnalysisRepository:
    """Data access layer for AI analysis results."""

    @staticmethod
    async def get_by_feedback_id(db: AsyncSession, feedback_id: UUID) -> AIAnalysis | None:
        """Get cached analysis for a feedback entry."""
        result = await db.execute(
            select(AIAnalysis).where(AIAnalysis.feedback_id == feedback_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, analysis_id: UUID) -> AIAnalysis | None:
        """Get analysis by its own ID."""
        result = await db.execute(
            select(AIAnalysis).where(AIAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> AIAnalysis:
        """Create a new AI analysis entry."""
        analysis = AIAnalysis(**data)
        db.add(analysis)
        await db.flush()
        await db.refresh(analysis)
        logger.info("Created AI analysis id=%s for feedback=%s", analysis.id, analysis.feedback_id)
        return analysis

    @staticmethod
    async def update(db: AsyncSession, feedback_id: UUID, data: dict) -> AIAnalysis | None:
        """Update an existing analysis (for cache refresh)."""
        analysis = await AIAnalysisRepository.get_by_feedback_id(db, feedback_id)
        if not analysis:
            return None

        for field, value in data.items():
            setattr(analysis, field, value)

        await db.flush()
        await db.refresh(analysis)
        logger.info("Updated AI analysis for feedback=%s", feedback_id)
        return analysis

    @staticmethod
    async def delete_by_feedback_id(db: AsyncSession, feedback_id: UUID) -> bool:
        """Delete analysis for a feedback entry."""
        analysis = await AIAnalysisRepository.get_by_feedback_id(db, feedback_id)
        if not analysis:
            return False
        await db.delete(analysis)
        await db.flush()
        logger.info("Deleted AI analysis for feedback=%s", feedback_id)
        return True

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[AIAnalysis]:
        """Get all analyses with pagination."""
        result = await db.execute(
            select(AIAnalysis)
            .order_by(AIAnalysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
