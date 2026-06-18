"""
Anthropic Claude provider stub.

Ready to be activated by providing CLAUDE_API_KEY in environment variables.
"""

import json
import logging
import time

from app.ai.base import AIProviderBase, AIResponse
from app.ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from app.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProviderBase):
    """Anthropic Claude provider for feedback analysis.
    
    Requires CLAUDE_API_KEY to be set in environment variables.
    Supports: claude-sonnet-4-20250514, claude-3-5-haiku-20241022
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key: str = getattr(settings, "CLAUDE_API_KEY", "")
        self.default_model: str = getattr(settings, "CLAUDE_MODEL", "claude-sonnet-4-20250514")

    @property
    def name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Anthropic Claude"

    @property
    def supported_models(self) -> list[str]:
        return ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"]

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        logger.info("Claude health check: API key present but live check not implemented.")
        return True

    async def analyze(
        self,
        feedback_text: str,
        rating: int,
        category: str,
        sentiment: str,
        priority: str,
        source: str,
    ) -> AIResponse:
        """Generate analysis using Anthropic Claude.
        
        To activate, install anthropic and uncomment below.
        """
        if not self.is_configured():
            raise RuntimeError("Claude provider is not configured. Set CLAUDE_API_KEY.")

        start_time = time.perf_counter()
        prompt = build_analysis_prompt(feedback_text, rating, category, sentiment, priority, source)

        # ----------------------------------------------------------------
        # UNCOMMENT TO ACTIVATE:
        #
        # import anthropic
        # client = anthropic.AsyncAnthropic(api_key=self.api_key)
        # response = await client.messages.create(
        #     model=self.default_model,
        #     max_tokens=500,
        #     system=SYSTEM_PROMPT,
        #     messages=[{"role": "user", "content": prompt}],
        # )
        # content = response.content[0].text
        # parsed = json.loads(content)
        # processing_time = (time.perf_counter() - start_time) * 1000
        #
        # return AIResponse(
        #     summary=parsed.get("summary", ""),
        #     root_cause=parsed.get("root_cause", ""),
        #     business_impact=parsed.get("business_impact", ""),
        #     recommended_action=parsed.get("recommended_action", ""),
        #     priority_reason=parsed.get("priority_reason", ""),
        #     confidence_score=0.85,
        #     provider=self.name,
        #     model_name=self.default_model,
        #     prompt_tokens=str(response.usage.input_tokens),
        #     completion_tokens=str(response.usage.output_tokens),
        #     processing_time_ms=round(processing_time, 2),
        # )
        # ----------------------------------------------------------------

        raise NotImplementedError(
            "Claude provider is configured but implementation is commented out. "
            "Install 'anthropic' and uncomment the code in providers/claude.py."
        )
