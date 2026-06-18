"""
FastAPI endpoints for multi-agent feedback pipeline and learning overrides.
"""

import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.agents.graph import get_graph
from app.redis import get_redis_client
from app.schemas.feedback import FeedbackResponse
from app.schemas.intelligence import SmartFeedbackCreate
from app.schemas.agent_run import FeedbackCorrectionCreate, FeedbackCorrectionResponse
from app.models.agent_run import FeedbackCorrection
from app.repositories.feedback import FeedbackRepository

logger = logging.getLogger("app.api.v1.agents")

router = APIRouter(prefix="/agents", tags=["Multi-Agent Pipeline"])


@router.post(
    "/process",
    status_code=status.HTTP_200_OK,
    summary="Process feedback synchronously through LangGraph",
)
async def process_feedback_sync(request: SmartFeedbackCreate):
    """Run the multi-agent graph synchronously on raw feedback input. Returns the completed state."""
    logger.info("Sync agent processing requested.")
    
    graph = get_graph()
    initial_state = {
        "raw_text": request.text,
        "rating": request.rating,
        "source": request.source,
        "actions_triggered": [],
        "agent_logs": [],
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        # Convert state into a response payload
        return {
            "status": "completed",
            "feedback_id": final_state.get("feedback_id"),
            "cleaned_text": final_state.get("cleaned_text"),
            "category": final_state.get("category"),
            "sentiment": final_state.get("sentiment"),
            "priority": final_state.get("priority"),
            "is_spike": final_state.get("is_spike"),
            "is_churn_risk": final_state.get("is_churn_risk"),
            "recurring_pattern": final_state.get("recurring_pattern"),
            "actions_triggered": final_state.get("actions_triggered"),
            "slack_alert_sent": final_state.get("slack_alert_sent"),
            "jira_ticket_key": final_state.get("jira_ticket_key"),
            "learning_notes": final_state.get("learning_notes"),
            "agent_logs": final_state.get("agent_logs"),
        }
    except Exception as e:
        logger.error("Error executing graph: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LangGraph execution failed: {str(e)}",
        )


async def _run_graph_in_background(thread_id: str, initial_state: dict):
    """Background runner for LangGraph, saving state results to Redis."""
    graph = get_graph()
    redis = get_redis_client()
    try:
        # Mark thread status as processing
        await redis.set(f"feedback_agent:status:{thread_id}", "processing", ex=3600)
        
        final_state = await graph.ainvoke(initial_state)
        
        # Save completed state to Redis for query retrieval
        await redis.set(f"feedback_agent:status:{thread_id}", "completed", ex=3600)
        await redis.set(f"feedback_agent:result:{thread_id}", json_dumps_payload(final_state), ex=86400)
        logger.info("Background thread %s completed successfully.", thread_id)
    except Exception as e:
        logger.error("Background thread %s failed: %s", thread_id, str(e))
        await redis.set(f"feedback_agent:status:{thread_id}", "failed", ex=3600)
        await redis.set(f"feedback_agent:error:{thread_id}", str(e), ex=3600)


def json_dumps_payload(state: dict) -> str:
    import json
    # Extract only serializable elements from final state
    serializable = {k: v for k, v in state.items()}
    return json.dumps(serializable)


@router.post(
    "/process-async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process feedback asynchronously",
)
async def process_feedback_async(request: SmartFeedbackCreate, background_tasks: BackgroundTasks):
    """Ingest feedback asynchronously, returning a run thread ID immediately. Processing runs in background."""
    thread_id = str(uuid.uuid4())
    logger.info("Async agent processing requested. Thread ID: %s", thread_id)

    initial_state = {
        "raw_text": request.text,
        "rating": request.rating,
        "source": request.source,
        "actions_triggered": [],
        "agent_logs": [],
    }

    # Queue background task
    background_tasks.add_task(_run_graph_in_background, thread_id, initial_state)
    
    return {
        "status": "queued",
        "thread_id": thread_id,
        "check_status_url": f"/api/v1/agents/state/{thread_id}",
    }


@router.get(
    "/state/{thread_id}",
    summary="Get async processing state and execution logs",
)
async def get_agent_state(thread_id: str):
    """Retrieve async execution status, error logging, and agent state results cached in Redis."""
    redis = get_redis_client()
    status_val = await redis.get(f"feedback_agent:status:{thread_id}")
    
    if not status_val:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread ID not found or expired.",
        )

    if status_val == "processing":
        return {"thread_id": thread_id, "status": "processing"}
        
    if status_val == "failed":
        err = await redis.get(f"feedback_agent:error:{thread_id}")
        return {"thread_id": thread_id, "status": "failed", "error": err}

    # Retrieve completed results
    result_str = await redis.get(f"feedback_agent:result:{thread_id}")
    if not result_str:
        return {"thread_id": thread_id, "status": "completed", "message": "State data expired."}

    import json
    return {
        "thread_id": thread_id,
        "status": "completed",
        "state": json.loads(result_str),
    }


@router.post(
    "/learning/correct",
    response_model=FeedbackCorrectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback override correction for learning loop",
)
async def submit_feedback_correction(
    request: FeedbackCorrectionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit a category/sentiment/priority correction. Feeds data to the Learning Agent on subsequent runs."""
    logger.info("Submitting feedback correction for ID: %s", request.feedback_id)
    
    # 1. Fetch current feedback record to extract old values
    feedback = await FeedbackRepository.get_by_id(db, request.feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail=f"Feedback ID {request.feedback_id} not found.")

    # Determine old value based on field
    old_value = None
    if request.field_corrected == "category":
        old_value = feedback.category
    elif request.field_corrected == "sentiment":
        old_value = feedback.sentiment
    elif request.field_corrected == "priority":
        old_value = feedback.priority
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="field_corrected must be one of: category, sentiment, priority",
        )

    # 2. Record override details
    correction = FeedbackCorrection(
        feedback_id=request.feedback_id,
        field_corrected=request.field_corrected,
        old_value=old_value,
        new_value=request.new_value,
    )
    db.add(correction)

    # 3. Apply override correction directly to the feedback record
    if request.field_corrected == "category":
        feedback.category = request.new_value
    elif request.field_corrected == "sentiment":
        feedback.sentiment = request.new_value
    elif request.field_corrected == "priority":
        feedback.priority = request.new_value

    await db.commit()
    await db.refresh(correction)
    logger.info("Override correction saved and applied. correction_id=%s", correction.id)
    return correction
