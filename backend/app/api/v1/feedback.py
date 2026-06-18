"""
Feedback CRUD API routes.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStats,
    FeedbackUpdate,
)
from app.services.feedback import FeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.get(
    "/stats/summary",
    response_model=FeedbackStats,
    summary="Get feedback statistics",
)
async def get_stats(
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    category: str | None = Query(None, description="Filter by category"),
    priority: str | None = Query(None, description="Filter by priority"),
    sentiment: str | None = Query(None, description="Filter by sentiment"),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated statistics for the dashboard with optional query filters."""
    from datetime import datetime, time
    
    start_dt = None
    if start_date:
        try:
            start_dt = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d").date(), time.min)
        except ValueError:
            pass
            
    end_dt = None
    if end_date:
        try:
            end_dt = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d").date(), time.max)
        except ValueError:
            pass

    return await FeedbackService.get_feedback_stats(
        db,
        start_date=start_dt,
        end_date=end_dt,
        category=category,
        priority=priority,
        sentiment=sentiment,
    )


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create feedback",
)
async def create_feedback(
    data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new feedback entry."""
    return await FeedbackService.create_feedback(db, data)


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="List feedback",
)
async def list_feedback(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    sentiment: str | None = Query(None, description="Filter by sentiment"),
    db: AsyncSession = Depends(get_db),
):
    """Get a paginated list of feedback with optional filters."""
    return await FeedbackService.get_feedbacks(
        db, page=page, size=size,
        category=category, status=status_filter,
        priority=priority, sentiment=sentiment,
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Get feedback by ID",
)
async def get_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single feedback entry by its UUID."""
    return await FeedbackService.get_feedback(db, feedback_id)


@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Update feedback",
)
async def update_feedback(
    feedback_id: UUID,
    data: FeedbackUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing feedback entry. Only provided fields are updated."""
    return await FeedbackService.update_feedback(db, feedback_id, data)


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete feedback",
)
async def delete_feedback(
    feedback_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a feedback entry by its UUID."""
    await FeedbackService.delete_feedback(db, feedback_id)
