import pytest
from app.ai.registry import ProviderRegistry
from app.ai.providers.gemini import GeminiProvider

def test_gemini_provider_registration():
    provider = ProviderRegistry.get("gemini")
    assert provider.name == "gemini"
    assert isinstance(provider, GeminiProvider)

def test_gemini_fallback_when_unconfigured():
    provider = ProviderRegistry.get("gemini")
    # If not configured, attempting to call it raises RuntimeError
    if not provider.is_configured():
        with pytest.raises(RuntimeError):
            import asyncio
            asyncio.run(provider.analyze("text", 3, "bug", "neutral", "low", "web"))
