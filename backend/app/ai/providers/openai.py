"""
OpenAI provider stub.

Ready to be activated by providing OPENAI_API_KEY in environment variables.
Uses the structured prompt templates from app.ai.prompts.
"""

import json
import logging
import time

from app.ai.base import AIProviderBase, AIResponse
from app.ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from app.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProviderBase):
    """OpenAI GPT provider for feedback analysis.
    
    Requires OPENAI_API_KEY to be set in environment variables.
    Supports: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key: str = getattr(settings, "OPENAI_API_KEY", "")
        self.default_model: str = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI GPT"

    @property
    def supported_models(self) -> list[str]:
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        try:
            # Would call OpenAI API to verify connectivity
            # import openai
            # client = openai.AsyncOpenAI(api_key=self.api_key)
            # await client.models.list()
            logger.info("OpenAI health check: API key present but live check not implemented.")
            return True
        except Exception as e:
            logger.error("OpenAI health check failed: %s", e)
            return False

    async def analyze(
        self,
        feedback_text: str,
        rating: int,
        category: str,
        sentiment: str,
        priority: str,
        source: str,
    ) -> AIResponse:
        """Generate analysis using OpenAI GPT.
        
        To activate, install openai package and uncomment the implementation below.
        """
        if not self.is_configured():
            raise RuntimeError("OpenAI provider is not configured. Set OPENAI_API_KEY.")

        start_time = time.perf_counter()
        prompt = build_analysis_prompt(feedback_text, rating, category, sentiment, priority, source)

        # ----------------------------------------------------------------
        # UNCOMMENT TO ACTIVATE:
        # 
        # import openai
        # client = openai.AsyncOpenAI(api_key=self.api_key)
        # response = await client.chat.completions.create(
        #     model=self.default_model,
        #     messages=[
        #         {"role": "system", "content": SYSTEM_PROMPT},
        #         {"role": "user", "content": prompt},
        #     ],
        #     response_format={"type": "json_object"},
        #     temperature=0.3,
        #     max_tokens=500,
        # )
        # content = response.choices[0].message.content
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
        #     prompt_tokens=str(response.usage.prompt_tokens),
        #     completion_tokens=str(response.usage.completion_tokens),
        #     processing_time_ms=round(processing_time, 2),
        #     raw_response={"id": response.id},
        # )
        # ----------------------------------------------------------------

        raise NotImplementedError(
            "OpenAI provider is configured but the implementation is commented out. "
            "Install 'openai' package and uncomment the code in providers/openai.py."
        )
