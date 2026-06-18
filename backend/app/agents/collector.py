"""
Collector Agent node.

Cleans raw text inputs, validates fields, and initializes the feedback record in the database.
"""

import logging
from uuid import UUID

from app.database import async_session_factory
from app.agents.state import FeedbackAgentState
from app.intelligence.cleaner import TextCleaner
from app.models.feedback import Feedback

logger = logging.getLogger("app.agents.collector")


async def collector_node(state: FeedbackAgentState) -> dict:
    """Collector Node: normalizes raw inputs and creates a pending feedback record in PostgreSQL."""
    logger.info("Collector Agent starting processing...")
    
    raw_text = state.get("raw_text", "")
    rating = state.get("rating", 0)
    source = state.get("source", "web")
    
    # 1. Clean the raw text
    cleaned_text = TextCleaner.clean(raw_text)
    
    # 2. Open DB session and create pending record
    feedback_id = None
    async with async_session_factory() as db:
        try:
            # We initialize the record. Sentiment, Category, Priority will be computed next.
            feedback = Feedback(
                text=raw_text,
                rating=rating,
                category="other",      # Default placeholder
                sentiment="neutral",    # Default placeholder
                priority="low",         # Default placeholder
                source=source,
                status="new",
            )
            db.add(feedback)
            await db.commit()
            await db.refresh(feedback)
            feedback_id = str(feedback.id)
            logger.info("Created feedback entry in DB. id=%s", feedback_id)
        except Exception as e:
            await db.rollback()
            logger.error("Collector Agent DB insertion failed: %s", str(e))
            raise e

    logs = state.get("agent_logs", [])
    logs.append(f"Collector Agent: Normalized text and created DB record id={feedback_id}")

    return {
        "feedback_id": feedback_id,
        "cleaned_text": cleaned_text,
        "agent_logs": logs,
    }
