"""
Google Gemini provider stub.

Ready to be activated by providing GEMINI_API_KEY in environment variables.
"""

import json
import logging
import time

from app.ai.base import AIProviderBase, AIResponse
from app.ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProviderBase):
    """Google Gemini provider for feedback analysis.
    
    Requires GEMINI_API_KEY to be set in environment variables.
    Supports: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key: str = getattr(settings, "GEMINI_API_KEY", "")
        self.default_model: str = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini"

    @property
    def supported_models(self) -> list[str]:
        return ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        try:
            import asyncio
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Test connectivity and API key validity asynchronously
            await asyncio.to_thread(genai.list_models)
            logger.info("Gemini health check passed successfully.")
            return True
        except Exception as e:
            logger.error("Gemini health check failed: %s", str(e))
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
        """Generate analysis using Google Gemini API."""
        if not self.is_configured():
            raise RuntimeError("Gemini provider is not configured. Set GEMINI_API_KEY.")

        start_time = time.perf_counter()
        prompt = build_analysis_prompt(feedback_text, rating, category, sentiment, priority, source)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.default_model,
                system_instruction=SYSTEM_PROMPT,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    max_output_tokens=500,
                ),
            )
            response = await model.generate_content_async(prompt)
            parsed = json.loads(response.text)
            processing_time = (time.perf_counter() - start_time) * 1000

            prompt_tokens = None
            completion_tokens = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                prompt_tokens = str(response.usage_metadata.prompt_token_count)
                completion_tokens = str(response.usage_metadata.candidates_token_count)

            return AIResponse(
                summary=parsed.get("summary", ""),
                root_cause=parsed.get("root_cause", ""),
                business_impact=parsed.get("business_impact", ""),
                recommended_action=parsed.get("recommended_action", ""),
                priority_reason=parsed.get("priority_reason", ""),
                confidence_score=0.90,
                provider=self.name,
                model_name=self.default_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                processing_time_ms=round(processing_time, 2),
                raw_response={"model": self.default_model},
            )
        except Exception as e:
            logger.error("Gemini API analysis failed: %s. Re-raising to allow registry fallback.", str(e))
            raise e
