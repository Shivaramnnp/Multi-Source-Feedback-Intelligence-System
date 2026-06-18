"""
Pydantic schemas for the AI Analysis Service.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIAnalysisRequest(BaseModel):
    """Request to generate AI analysis for a feedback entry."""
    feedback_id: UUID = Field(..., description="UUID of the feedback to analyze.")
    force_refresh: bool = Field(
        False,
        description="If true, bypass cache and regenerate analysis.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "feedback_id": "550e8400-e29b-41d4-a716-446655440000",
                "force_refresh": False,
            }
        }
    )


class AIAnalysisResult(BaseModel):
    """Core AI analysis output fields."""
    summary: str = Field(..., description="Brief summary of the feedback.")
    root_cause: str = Field(..., description="Identified root cause or underlying issue.")
    business_impact: str = Field(..., description="Potential business impact assessment.")
    recommended_action: str = Field(..., description="Recommended action to address the feedback.")
    priority_reason: str = Field(..., description="Reasoning behind the assigned priority.")


class AIAnalysisResponse(BaseModel):
    """Full AI analysis response including metadata."""
    id: UUID
    feedback_id: UUID
    provider: str
    model_name: str
    summary: str
    root_cause: str
    business_impact: str
    recommended_action: str
    priority_reason: str
    confidence_score: float
    prompt_tokens: str | None = None
    completion_tokens: str | None = None
    processing_time_ms: float | None = None
    cached: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIAnalysisBatchRequest(BaseModel):
    """Request to analyze multiple feedback entries."""
    feedback_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of feedback UUIDs to analyze (max 50).",
    )
    force_refresh: bool = Field(False)


class AIAnalysisBatchResponse(BaseModel):
    """Response for batch analysis."""
    results: list[AIAnalysisResponse]
    total_processed: int
    total_cached: int
    total_generated: int


class AIProviderInfo(BaseModel):
    """Information about an available AI provider."""
    name: str
    display_name: str
    models: list[str]
    is_configured: bool
    is_default: bool
