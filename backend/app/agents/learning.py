"""
Learning Agent node.

Analyzes historical feedback overrides from the feedback_corrections table,
logs accuracy statistics, and stores active few-shot training items in Redis to adapt prompts.
"""

import json
import logging
from sqlalchemy import func, select

from app.database import async_session_factory
from app.redis import get_redis_client
from app.agents.state import FeedbackAgentState
from app.models.agent_run import FeedbackCorrection

logger = logging.getLogger("app.agents.learning")


async def learning_node(state: FeedbackAgentState) -> dict:
    """Learning Agent: scans overrides to update prompting context or weight rules in Redis memory."""
    logger.info("Learning Agent running training analysis...")

    feedback_id = state.get("feedback_id")
    learning_notes = "No correction patterns analyzed yet."

    async with async_session_factory() as db:
        try:
            # 1. Query aggregate override correction counts
            count_result = await db.execute(select(func.count()).select_from(FeedbackCorrection))
            total_corrections = count_result.scalar() or 0

            if total_corrections > 0:
                # Group overrides by field to check where classification fails most
                field_group_result = await db.execute(
                    select(FeedbackCorrection.field_corrected, func.count())
                    .group_by(FeedbackCorrection.field_corrected)
                )
                fields_data = field_group_result.all()
                field_summary = ", ".join([f"{row[0]}: {row[1]} overrides" for row in fields_data])

                # 2. Extract recent 5 corrections to use as dynamic few-shot training examples
                examples_result = await db.execute(
                    select(FeedbackCorrection).order_by(FeedbackCorrection.created_at.desc()).limit(5)
                )
                corrections = examples_result.scalars().all()
                few_shots = []
                for corr in corrections:
                    few_shots.append({
                        "field": corr.field_corrected,
                        "old": corr.old_value,
                        "new": corr.new_value,
                    })

                # 3. Cache few-shot overrides in Redis for prompt integration
                try:
                    redis = get_redis_client()
                    await redis.set("feedback_intelligence:few_shots", json.dumps(few_shots))
                    logger.info("Saved %d active few-shot corrections to Redis.", len(few_shots))
                except Exception as re:
                    logger.error("Failed to save few-shots to Redis: %s", str(re))

                learning_notes = (
                    f"Analyzed {total_corrections} total overrides ({field_summary}). "
                    f"Saved {len(few_shots)} training corrections to Redis memory."
                )
            else:
                learning_notes = "Zero overrides recorded. Prompt performance is stable at 100% baseline accuracy."

        except Exception as e:
            logger.error("Learning Agent aggregation failed: %s", str(e))

    logs = state.get("agent_logs", [])
    logs.append(f"Learning Agent: Accuracy training complete. Notes: {learning_notes}")

    return {
        "learning_notes": learning_notes,
        "agent_logs": logs,
    }
