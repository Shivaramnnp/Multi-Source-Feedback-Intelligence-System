"""
Pydantic schemas for multi-agent action logs, user corrections, and trend spikes.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AgentActionLogCreate(BaseModel):
    feedback_id: UUID
    action_type: str = Field(..., description="slack_alert, jira_ticket, support_escalation")
    status: str = Field("success", description="success or failed")
    details: str | None = Field(None, description="Details or payload of action")


class AgentActionLogResponse(BaseModel):
    id: UUID
    feedback_id: UUID
    action_type: str
    status: str
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackCorrectionCreate(BaseModel):
    feedback_id: UUID
    field_corrected: str = Field(..., description="category, sentiment, or priority")
    old_value: str
    new_value: str


class FeedbackCorrectionResponse(BaseModel):
    id: UUID
    feedback_id: UUID
    field_corrected: str
    old_value: str
    new_value: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrendSpikeCreate(BaseModel):
    metric: str = Field(..., description="volume, category_spike, negative_sentiment_spike")
    current_value: float
    threshold_value: float
    details: str | None = None


class TrendSpikeResponse(BaseModel):
    id: UUID
    metric: str
    current_value: float
    threshold_value: float
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
