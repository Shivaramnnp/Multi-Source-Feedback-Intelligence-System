"""
AI Analysis service — business logic layer.

Orchestrates AI provider calls, caching, and database storage.
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.registry import ProviderRegistry
from app.exceptions.handlers import FeedbackNotFoundError
from app.models.ai_analysis import AIAnalysis
from app.repositories.ai_analysis import AIAnalysisRepository
from app.repositories.feedback import FeedbackRepository
from app.schemas.ai_analysis import (
    AIAnalysisBatchResponse,
    AIAnalysisResponse,
)

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for generating, caching, and retrieving AI analyses."""

    @staticmethod
    async def analyze_feedback(
        db: AsyncSession,
        feedback_id: UUID,
        force_refresh: bool = False,
        provider_name: str | None = None,
    ) -> AIAnalysisResponse:
        """Generate AI analysis for a feedback entry.
        
        Checks cache first. If cached and not force_refresh, returns cached result.
        Otherwise, runs analysis through the AI provider and stores the result.
        
        Args:
            db: Database session.
            feedback_id: UUID of the feedback to analyze.
            force_refresh: If True, bypass cache and regenerate.
            provider_name: Specific provider to use (default: auto-select).
            
        Returns:
            AIAnalysisResponse with the analysis results.
        """
        # Verify feedback exists
        feedback = await FeedbackRepository.get_by_id(db, feedback_id)
        if not feedback:
            raise FeedbackNotFoundError(str(feedback_id))

        # Check cache
        if not force_refresh:
            existing = await AIAnalysisRepository.get_by_feedback_id(db, feedback_id)
            if existing:
                logger.info("Cache hit for feedback %s — returning cached analysis.", feedback_id)
                # Mark as cached in response
                return AIAnalysisResponse.model_validate(existing)

        # Get provider
        provider = ProviderRegistry.get(provider_name)
        logger.info(
            "Generating AI analysis for feedback %s using provider '%s'",
            feedback_id, provider.name,
        )

        # Run analysis
        ai_response = await provider.analyze(
            feedback_text=feedback.text,
            rating=feedback.rating,
            category=feedback.category,
            sentiment=feedback.sentiment,
            priority=feedback.priority,
            source=feedback.source,
        )

        # Prepare DB record
        analysis_data = {
            "feedback_id": feedback_id,
            "provider": ai_response.provider,
            "model_name": ai_response.model_name,
            "summary": ai_response.summary,
            "root_cause": ai_response.root_cause,
            "business_impact": ai_response.business_impact,
            "recommended_action": ai_response.recommended_action,
            "priority_reason": ai_response.priority_reason,
            "confidence_score": ai_response.confidence_score,
            "prompt_tokens": ai_response.prompt_tokens,
            "completion_tokens": ai_response.completion_tokens,
            "processing_time_ms": ai_response.processing_time_ms,
            "cached": "false",
        }

        # Upsert: update if exists, create if not
        existing = await AIAnalysisRepository.get_by_feedback_id(db, feedback_id)
        if existing:
            analysis = await AIAnalysisRepository.update(db, feedback_id, analysis_data)
        else:
            analysis = await AIAnalysisRepository.create(db, analysis_data)

        logger.info(
            "AI analysis stored: feedback=%s provider=%s confidence=%.2f time=%.1fms",
            feedback_id, ai_response.provider,
            ai_response.confidence_score,
            ai_response.processing_time_ms or 0,
        )

        return AIAnalysisResponse.model_validate(analysis)

    @staticmethod
    async def get_analysis(
        db: AsyncSession,
        feedback_id: UUID,
    ) -> AIAnalysisResponse | None:
        """Get cached analysis for a feedback entry."""
        analysis = await AIAnalysisRepository.get_by_feedback_id(db, feedback_id)
        if analysis:
            return AIAnalysisResponse.model_validate(analysis)
        return None

    @staticmethod
    async def batch_analyze(
        db: AsyncSession,
        feedback_ids: list[UUID],
        force_refresh: bool = False,
        provider_name: str | None = None,
    ) -> AIAnalysisBatchResponse:
        """Analyze multiple feedback entries.
        
        Processes each feedback, using cache where available.
        """
        results: list[AIAnalysisResponse] = []
        cached_count = 0
        generated_count = 0

        for fid in feedback_ids:
            try:
                # Check cache first
                if not force_refresh:
                    existing = await AIAnalysisRepository.get_by_feedback_id(db, fid)
                    if existing:
                        results.append(AIAnalysisResponse.model_validate(existing))
                        cached_count += 1
                        continue

                result = await AIAnalysisService.analyze_feedback(
                    db, fid, force_refresh=force_refresh, provider_name=provider_name,
                )
                results.append(result)
                generated_count += 1

            except FeedbackNotFoundError:
                logger.warning("Skipping feedback %s — not found.", fid)
            except Exception as e:
                logger.error("Failed to analyze feedback %s: %s", fid, str(e))

        logger.info(
            "Batch analysis complete: %d processed, %d cached, %d generated",
            len(results), cached_count, generated_count,
        )

        return AIAnalysisBatchResponse(
            results=results,
            total_processed=len(results),
            total_cached=cached_count,
            total_generated=generated_count,
        )

    @staticmethod
    async def delete_analysis(db: AsyncSession, feedback_id: UUID) -> bool:
        """Delete cached analysis for a feedback entry."""
        return await AIAnalysisRepository.delete_by_feedback_id(db, feedback_id)

    @staticmethod
    def list_providers() -> list[dict]:
        """List all available AI providers."""
        return ProviderRegistry.list_providers()
