"""
Abstract base class for AI providers.

All AI providers must implement this interface to be pluggable into
the analysis service.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    summary: str
    root_cause: str
    business_impact: str
    recommended_action: str
    priority_reason: str
    confidence_score: float = 0.0
    provider: str = ""
    model_name: str = ""
    prompt_tokens: str | None = None
    completion_tokens: str | None = None
    processing_time_ms: float | None = None
    raw_response: dict = field(default_factory=dict)


class AIProviderBase(ABC):
    """Abstract base class that all AI providers must implement.
    
    To add a new provider:
    1. Create a new class extending AIProviderBase
    2. Implement all abstract methods
    3. Register it in the ProviderRegistry
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider (e.g., 'openai', 'gemini', 'claude')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for this provider."""
        ...

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        """List of model identifiers this provider supports."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if this provider has all required configuration (API keys, etc.)."""
        ...

    @abstractmethod
    async def analyze(
        self,
        feedback_text: str,
        rating: int,
        category: str,
        sentiment: str,
        priority: str,
        source: str,
    ) -> AIResponse:
        """Generate AI analysis for a feedback entry.
        
        Args:
            feedback_text: The raw feedback text.
            rating: User rating (1-5).
            category: Feedback category.
            sentiment: Detected sentiment.
            priority: Detected priority.
            source: Feedback source.
            
        Returns:
            AIResponse with structured analysis fields.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify the provider connection is healthy."""
        ...
