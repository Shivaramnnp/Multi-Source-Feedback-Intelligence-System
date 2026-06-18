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
        return ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def health_check(self) -> bool:
        if not self.is_configured():
            return False
        logger.info("Gemini health check: API key present but live check not implemented.")
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
        """Generate analysis using Google Gemini.
        
        To activate, install google-generativeai and uncomment below.
        """
        if not self.is_configured():
            raise RuntimeError("Gemini provider is not configured. Set GEMINI_API_KEY.")

        start_time = time.perf_counter()
        prompt = build_analysis_prompt(feedback_text, rating, category, sentiment, priority, source)

        # ----------------------------------------------------------------
        # UNCOMMENT TO ACTIVATE:
        #
        # import google.generativeai as genai
        # genai.configure(api_key=self.api_key)
        # model = genai.GenerativeModel(
        #     model_name=self.default_model,
        #     system_instruction=SYSTEM_PROMPT,
        #     generation_config=genai.GenerationConfig(
        #         response_mime_type="application/json",
        #         temperature=0.3,
        #         max_output_tokens=500,
        #     ),
        # )
        # response = await model.generate_content_async(prompt)
        # parsed = json.loads(response.text)
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
        #     prompt_tokens=str(response.usage_metadata.prompt_token_count),
        #     completion_tokens=str(response.usage_metadata.candidates_token_count),
        #     processing_time_ms=round(processing_time, 2),
        # )
        # ----------------------------------------------------------------

        raise NotImplementedError(
            "Gemini provider is configured but implementation is commented out. "
            "Install 'google-generativeai' and uncomment the code in providers/gemini.py."
        )
