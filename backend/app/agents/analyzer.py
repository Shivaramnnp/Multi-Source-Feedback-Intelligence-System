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

    # 1. Run intelligence analysis
    analysis = IntelligenceService.analyze_text(cleaned_text, rating=rating)
    
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
