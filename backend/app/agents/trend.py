"""
Trend Agent node.

Analyzes historical database records to detect spikes, identify recurring issues,
and evaluate user churn risks. Logs anomalies to the trend_spikes table.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import func, select

from app.database import async_session_factory
from app.agents.state import FeedbackAgentState
from app.models.feedback import Feedback
from app.models.agent_run import TrendSpike

logger = logging.getLogger("app.agents.trend")


async def trend_node(state: FeedbackAgentState) -> dict:
    """Trend Node: checks historical feedback metrics to flag spikes, recurring trends, and churn risks."""
    logger.info("Trend Agent analyzing pattern trends...")

    raw_text = state.get("raw_text", "").lower()
    sentiment = state.get("sentiment", "neutral")
    
    is_spike = False
    is_churn_risk = False
    recurring_pattern = None

    # 1. Churn Risk Detection
    churn_keywords = ["cancel", "refund", "leaving", "close account", "unsubscribe", "stop billing", "overpriced"]
    if sentiment == "negative" and any(keyword in raw_text for keyword in churn_keywords):
        is_churn_risk = True
        logger.warning("Churn risk detected in feedback!")

    # 2. Daily volume spike detection & recurring pattern analysis
    async with async_session_factory() as db:
        try:
            now = datetime.utcnow()
            last_24h = now - timedelta(days=1)
            last_7d = now - timedelta(days=7)

            # A. Count in last 24h
            result_24h = await db.execute(
                select(func.count()).select_from(Feedback).where(Feedback.created_at >= last_24h)
            )
            count_24h = result_24h.scalar() or 0

            # B. Daily average count (based on last 7 days)
            result_7d = await db.execute(
                select(func.count()).select_from(Feedback).where(Feedback.created_at >= last_7d)
            )
            count_7d = result_7d.scalar() or 0
            daily_average = max(count_7d / 7.0, 1.0)  # Avoid division by zero, default to min 1

            # C. Check if 24h volume exceeds daily average by 50%
            # Only trigger spike if volume is significant (e.g. >= 5 items in 24h)
            if count_24h >= 5 and count_24h > daily_average * 1.5:
                is_spike = True
                logger.info("Volume spike detected: 24h=%d, average=%.2f", count_24h, daily_average)
                
                # Log spike to Database
                spike = TrendSpike(
                    metric="volume_spike",
                    current_value=float(count_24h),
                    threshold_value=float(daily_average * 1.5),
                    details=f"24h volume ({count_24h}) exceeded 7-day daily average ({daily_average:.2f}) by 50%+",
                )
                db.add(spike)
                await db.commit()

            # D. Identify recurring category patterns in last 24h
            pattern_result = await db.execute(
                select(Feedback.category, func.count())
                .where(Feedback.created_at >= last_24h)
                .group_by(Feedback.category)
                .having(func.count() >= 3)  # At least 3 of the same category
            )
            patterns = pattern_result.all()
            if patterns:
                recurring_pattern = ", ".join([f"{row[0]} ({row[1]} entries)" for row in patterns])
                logger.info("Recurring pattern detected: %s", recurring_pattern)

        except Exception as e:
            await db.rollback()
            logger.error("Trend Agent aggregation failed: %s", str(e))

    logs = state.get("agent_logs", [])
    logs.append(
        f"Trend Agent: Checked volume anomalies (spike={is_spike}, churn_risk={is_churn_risk}, patterns={recurring_pattern})"
    )

    return {
        "is_spike": is_spike,
        "is_churn_risk": is_churn_risk,
        "recurring_pattern": recurring_pattern,
        "agent_logs": logs,
    }
