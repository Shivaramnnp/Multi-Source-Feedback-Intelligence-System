"""
Intelligence Engine API routes.

Provides endpoints for text analysis and smart feedback creation.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.intelligence.service import IntelligenceService
from app.schemas.feedback import FeedbackResponse
from app.schemas.intelligence import (
    AnalysisResponse,
    AnalyzeRequest,
    SmartFeedbackCreate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["Intelligence Engine"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze feedback text",
    description="Run the full intelligence pipeline (clean → sentiment → categorize → prioritize) on raw text without saving.",
)
async def analyze_text(request: AnalyzeRequest):
    """Analyze raw text through the intelligence pipeline."""
    result = IntelligenceService.analyze_text(request.text, rating=request.rating)
    return result.to_dict()


@router.post(
    "/analyze/{feedback_id}",
    response_model=AnalysisResponse,
    summary="Analyze existing feedback",
    description="Run the intelligence pipeline on an existing feedback entry and update its sentiment, category, and priority.",
)
async def analyze_existing_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Analyze an existing feedback entry and update it."""
    result = await IntelligenceService.analyze_and_update(db, feedback_id)
    return result.to_dict()


@router.post(
    "/smart-submit",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Smart feedback submission",
    description="Submit feedback with automatic sentiment analysis, categorization, and priority scoring.",
)
async def smart_submit_feedback(
    request: SmartFeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback with auto-analysis."""
    feedback, analysis = await IntelligenceService.analyze_and_create(
        db, text=request.text, rating=request.rating, source=request.source,
    )
    logger.info(
        "Smart submission: id=%s sentiment=%s category=%s priority=%s",
        feedback.id, analysis.sentiment.label,
        analysis.category.category, analysis.priority.priority,
    )
    return feedback
