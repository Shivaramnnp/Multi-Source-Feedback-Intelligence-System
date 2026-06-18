"""
Feedback repository — data access layer.

Provides static async methods for CRUD operations and statistical aggregations
on the feedbacks table using SQLAlchemy 2.0 async queries.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate

logger = logging.getLogger(__name__)


class FeedbackRepository:
    """Data access layer for feedback CRUD and aggregation queries."""

    @staticmethod
    async def create(db: AsyncSession, data: FeedbackCreate) -> Feedback:
        """Create a new feedback entry."""
        feedback = Feedback(**data.model_dump())
        db.add(feedback)
        await db.flush()
        await db.refresh(feedback)
        logger.info("Created feedback id=%s", feedback.id)
        return feedback

    @staticmethod
    async def get_by_id(db: AsyncSession, feedback_id: UUID) -> Feedback | None:
        """Get a feedback entry by its UUID."""
        result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        category: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
    ) -> tuple[list[Feedback], int]:
        """Get paginated feedback with optional filters."""
        query = select(Feedback)
        count_query = select(func.count()).select_from(Feedback)

        if category:
            query = query.where(Feedback.category == category)
            count_query = count_query.where(Feedback.category == category)
        if status:
            query = query.where(Feedback.status == status)
            count_query = count_query.where(Feedback.status == status)
        if priority:
            query = query.where(Feedback.priority == priority)
            count_query = count_query.where(Feedback.priority == priority)
        if sentiment:
            query = query.where(Feedback.sentiment == sentiment)
            count_query = count_query.where(Feedback.sentiment == sentiment)

        query = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        items = list(result.scalars().all())

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return items, total

    @staticmethod
    async def update(db: AsyncSession, feedback_id: UUID, data: FeedbackUpdate) -> Feedback | None:
        """Update a feedback entry. Only updates fields that were explicitly set."""
        feedback = await FeedbackRepository.get_by_id(db, feedback_id)
        if not feedback:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)

        await db.flush()
        await db.refresh(feedback)
        logger.info("Updated feedback id=%s fields=%s", feedback_id, list(update_data.keys()))
        return feedback

    @staticmethod
    async def delete(db: AsyncSession, feedback_id: UUID) -> bool:
        """Delete a feedback entry by UUID. Returns True if deleted."""
        feedback = await FeedbackRepository.get_by_id(db, feedback_id)
        if not feedback:
            return False
        await db.delete(feedback)
        await db.flush()
        logger.info("Deleted feedback id=%s", feedback_id)
        return True

    @staticmethod
    async def get_stats(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
    ) -> dict:
        """Get aggregated statistics with filters for dashboard widgets and trends."""
        from sqlalchemy import cast, Date

        def _apply_filters(query):
            if start_date:
                query = query.where(Feedback.created_at >= start_date)
            if end_date:
                query = query.where(Feedback.created_at <= end_date)
            if category:
                query = query.where(Feedback.category == category)
            if priority:
                query = query.where(Feedback.priority == priority)
            if sentiment:
                query = query.where(Feedback.sentiment == sentiment)
            return query

        # Total count
        total_query = _apply_filters(select(func.count()).select_from(Feedback))
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0

        # Average rating
        avg_query = _apply_filters(select(func.avg(Feedback.rating)).select_from(Feedback))
        avg_result = await db.execute(avg_query)
        average_rating = round(float(avg_result.scalar() or 0), 2)

        # Distribution helper
        async def get_distribution(column) -> dict[str, int]:
            query = _apply_filters(
                select(column, func.count()).select_from(Feedback).group_by(column)
            )
            result = await db.execute(query)
            return {str(row[0]): row[1] for row in result.all()}

        sentiment_dist = await get_distribution(Feedback.sentiment)
        category_dist = await get_distribution(Feedback.category)
        priority_dist = await get_distribution(Feedback.priority)
        status_dist = await get_distribution(Feedback.status)
        rating_dist = await get_distribution(Feedback.rating)

        # Priority Heatmap: category vs priority counts
        heatmap_query = _apply_filters(
            select(Feedback.category, Feedback.priority, func.count())
            .select_from(Feedback)
            .group_by(Feedback.category, Feedback.priority)
        )
        heatmap_result = await db.execute(heatmap_query)
        priority_heatmap = {}
        for row in heatmap_result.all():
            cat, prio, count = row[0], row[1], row[2]
            if cat not in priority_heatmap:
                priority_heatmap[cat] = {}
            priority_heatmap[cat][prio] = count

        # Trends: feedback count, categories, sentiments over time grouped by day
        date_col = cast(Feedback.created_at, Date)
        trend_query = _apply_filters(
            select(date_col, Feedback.category, Feedback.sentiment, func.count())
            .select_from(Feedback)
            .group_by(date_col, Feedback.category, Feedback.sentiment)
            .order_by(date_col.asc())
        )
        trend_result = await db.execute(trend_query)
        trends_by_date = {}
        for row in trend_result.all():
            d, cat, sent, count = row[0], row[1], row[2], row[3]
            date_str = d.isoformat() if hasattr(d, 'isoformat') else str(d)
            if date_str not in trends_by_date:
                trends_by_date[date_str] = {
                    "date": date_str,
                    "count": 0,
                    "categories": {},
                    "sentiments": {}
                }
            trends_by_date[date_str]["count"] += count
            trends_by_date[date_str]["categories"][cat] = (
                trends_by_date[date_str]["categories"].get(cat, 0) + count
            )
            trends_by_date[date_str]["sentiments"][sent] = (
                trends_by_date[date_str]["sentiments"].get(sent, 0) + count
            )
        trends_list = list(trends_by_date.values())

        # Recent feedback
        recent_query = _apply_filters(
            select(Feedback).order_by(Feedback.created_at.desc()).limit(5)
        )
        recent_result = await db.execute(recent_query)
        recent = list(recent_result.scalars().all())

        return {
            "total_count": total_count,
            "average_rating": average_rating,
            "sentiment_distribution": sentiment_dist,
            "category_distribution": category_dist,
            "priority_distribution": priority_dist,
            "status_distribution": status_dist,
            "rating_distribution": rating_dist,
            "trends": trends_list,
            "priority_heatmap": priority_heatmap,
            "recent_feedback": recent,
        }
