"""
Pydantic schemas for the intelligence engine API.
"""

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    """Request schema for standalone text analysis."""
    text: str = Field(..., min_length=1, description="Raw feedback text to analyze.")
    rating: int | None = Field(None, ge=1, le=5, description="Optional rating (1-5) for priority scoring.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "The payment system is broken and I lost my data!",
                "rating": 1,
            }
        }
    )


class SentimentResponse(BaseModel):
    """Sentiment analysis result."""
    label: str = Field(..., description="positive, neutral, or negative")
    score: float = Field(..., description="Score from -1.0 to 1.0")
    confidence: float = Field(..., description="Confidence from 0.0 to 1.0")
    positive_words: list[str] = Field(default_factory=list)
    negative_words: list[str] = Field(default_factory=list)


class CategoryResponse(BaseModel):
    """Category classification result."""
    category: str = Field(..., description="bug, feature_request, praise, complaint, or support")
    confidence: float
    matched_keywords: list[str] = Field(default_factory=list)


class PriorityResponse(BaseModel):
    """Priority scoring result."""
    priority: str = Field(..., description="low, medium, high, or critical")
    score: float
    reasons: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Full analysis response from the intelligence engine."""
    cleaned_text: str
    sentiment: SentimentResponse
    category: CategoryResponse
    priority: PriorityResponse
    processing_steps: list[str]


class SmartFeedbackCreate(BaseModel):
    """Request schema for creating feedback with auto-analysis."""
    text: str = Field(..., min_length=1, description="Raw feedback text.")
    rating: int = Field(..., ge=1, le=5, description="User rating (1-5).")
    source: str = Field(default="web", description="Feedback source.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "The new dashboard feature is amazing! Really love the analytics.",
                "rating": 5,
                "source": "web",
            }
        }
    )
