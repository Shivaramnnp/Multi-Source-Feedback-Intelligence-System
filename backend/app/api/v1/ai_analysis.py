"""
AI Analysis API routes.

Provides endpoints for AI-powered feedback analysis with provider abstraction.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.ai_analysis import (
    AIAnalysisBatchRequest,
    AIAnalysisBatchResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIProviderInfo,
)
from app.services.ai_analysis import AIAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


@router.post(
    "/analyze",
    response_model=AIAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI analysis for feedback",
    description=(
        "Run AI analysis on a feedback entry. Returns cached results if available "
        "unless force_refresh is set. Uses the default AI provider (built-in mock "
        "engine) or a specified provider (openai, gemini, claude)."
    ),
)
async def analyze_feedback(
    request: AIAnalysisRequest,
    provider: str | None = Query(None, description="AI provider to use (mock, openai, gemini, claude)"),
    db: AsyncSession = Depends(get_db),
):
    """Generate or retrieve AI analysis for a feedback entry."""
    return await AIAnalysisService.analyze_feedback(
        db,
        feedback_id=request.feedback_id,
        force_refresh=request.force_refresh,
        provider_name=provider,
    )


@router.get(
    "/analyze/{feedback_id}",
    response_model=AIAnalysisResponse | None,
    summary="Get cached AI analysis",
    description="Retrieve the cached AI analysis for a feedback entry. Returns null if not analyzed yet.",
)
async def get_analysis(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get cached analysis for a feedback entry."""
    result = await AIAnalysisService.get_analysis(db, feedback_id)
    if result is None:
        return None
    return result


@router.post(
    "/analyze/batch",
    response_model=AIAnalysisBatchResponse,
    summary="Batch analyze multiple feedback entries",
    description="Analyze up to 50 feedback entries. Uses cache where available.",
)
async def batch_analyze(
    request: AIAnalysisBatchRequest,
    provider: str | None = Query(None, description="AI provider to use"),
    db: AsyncSession = Depends(get_db),
):
    """Analyze multiple feedback entries in batch."""
    return await AIAnalysisService.batch_analyze(
        db,
        feedback_ids=request.feedback_ids,
        force_refresh=request.force_refresh,
        provider_name=provider,
    )


@router.delete(
    "/analyze/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete cached AI analysis",
    description="Remove the cached AI analysis for a feedback entry.",
)
async def delete_analysis(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete cached analysis for a feedback entry."""
    await AIAnalysisService.delete_analysis(db, feedback_id)


@router.get(
    "/providers",
    response_model=list[AIProviderInfo],
    summary="List available AI providers",
    description="Get all registered AI providers with their configuration status.",
)
async def list_providers():
    """List all available AI providers."""
    providers = AIAnalysisService.list_providers()
    return providers
