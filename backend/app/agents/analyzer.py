"""
Analyzer Agent node.

Executes sentiment analysis, categorization, and priority scoring on the cleaned text.
Updates the database feedback record with the findings.
"""

import logging
from uuid import UUID

from app.database import async_session_factory
from app.agents.state import FeedbackAgentState
from app.intelligence.service import IntelligenceService
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import FeedbackUpdate

logger = logging.getLogger("app.agents.analyzer")


async def analyzer_node(state: FeedbackAgentState) -> dict:
    """Analyzer Node: performs sentiment, categorization, and priority analysis, then updates DB."""
    logger.info("Analyzer Agent running analysis...")
    
    feedback_id = state.get("feedback_id")
    cleaned_text = state.get("cleaned_text", "")
    rating = state.get("rating", 0)
    
    if not feedback_id:
        logger.error("No feedback_id found in agent state.")
        return {}

    # 1. Load latest 20 category overrides for learning loop feedback
    corrections = []
    async with async_session_factory() as db:
        try:
            from sqlalchemy import select
            from app.models.agent_run import FeedbackCorrection
            from app.models.feedback import Feedback

            stmt = (
                select(FeedbackCorrection, Feedback.text)
                .join(Feedback, FeedbackCorrection.feedback_id == Feedback.id)
                .where(FeedbackCorrection.field_corrected == "category")
                .order_by(FeedbackCorrection.created_at.desc())
                .limit(20)
            )
            res = await db.execute(stmt)
            corrections = res.all()
            logger.info("Loaded %d category corrections for learning loop adaptation.", len(corrections))
        except Exception as e:
            logger.error("Learning Loop: Failed to load corrections: %s", str(e))

    # 2. Run intelligence analysis with corrections list
    analysis = IntelligenceService.analyze_text(cleaned_text, rating=rating, corrections=corrections)

    
    sentiment = analysis.sentiment.label
    
    # Map the pipeline category to schema-compatible value
    category_map = {
        "bug": "bug",
        "feature_request": "feature",
        "praise": "praise",
        "complaint": "complaint",
        "support": "other",
    }
    category = category_map.get(analysis.category.category, "other")
    priority = analysis.priority.priority

    # 2. Update PostgreSQL database
    async with async_session_factory() as db:
        try:
            update_data = FeedbackUpdate(
                sentiment=sentiment,
                category=category,
                priority=priority,
            )
            await FeedbackRepository.update(db, UUID(feedback_id), update_data)
            await db.commit()
            logger.info("Analyzer Agent updated database record %s.", feedback_id)
        except Exception as e:
            await db.rollback()
            logger.error("Analyzer Agent DB update failed: %s", str(e))
            raise e

    logs = state.get("agent_logs", [])
    logs.append(
        f"Analyzer Agent: Classified feedback (sentiment={sentiment}, category={category}, priority={priority})"
    )

    return {
        "category": category,
        "sentiment": sentiment,
        "priority": priority,
        "agent_logs": logs,
    }
