"""
AI Provider Registry.

Manages provider registration, selection, and lifecycle.
Implements the Strategy pattern for pluggable AI backends.
"""

import logging
from typing import ClassVar

from app.ai.base import AIProviderBase

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry for AI provider management.
    
    Handles provider registration, selection, and discovery.
    Thread-safe singleton pattern.
    """

    _providers: ClassVar[dict[str, AIProviderBase]] = {}
    _default_provider: ClassVar[str] = "mock"
    _initialized: ClassVar[bool] = False

    @classmethod
    def initialize(cls) -> None:
        """Register all available providers."""
        if cls._initialized:
            return

        # Import and register providers
        from app.ai.providers.mock import MockAIProvider
        from app.ai.providers.openai import OpenAIProvider
        from app.ai.providers.gemini import GeminiProvider
        from app.ai.providers.claude import ClaudeProvider

        providers = [MockAIProvider(), OpenAIProvider(), GeminiProvider(), ClaudeProvider()]

        for provider in providers:
            cls.register(provider)

        # Set default to first configured real provider, or fall back to mock
        for provider in [OpenAIProvider(), GeminiProvider(), ClaudeProvider()]:
            if provider.is_configured():
                cls._default_provider = provider.name
                logger.info("Default AI provider set to: %s", provider.display_name)
                break
        else:
            cls._default_provider = "mock"
            logger.info("No external AI provider configured. Using built-in mock provider.")

        cls._initialized = True
        logger.info(
            "Provider registry initialized with %d providers: %s",
            len(cls._providers),
            list(cls._providers.keys()),
        )

    @classmethod
    def register(cls, provider: AIProviderBase) -> None:
        """Register a provider instance."""
        cls._providers[provider.name] = provider
        logger.debug("Registered AI provider: %s (%s)", provider.name, provider.display_name)

    @classmethod
    def get(cls, name: str | None = None) -> AIProviderBase:
        """Get a provider by name, or the default provider.
        
        Args:
            name: Provider name. If None, returns the default provider.
            
        Raises:
            ValueError: If the requested provider is not registered.
        """
        if not cls._initialized:
            cls.initialize()

        provider_name = name or cls._default_provider

        if provider_name not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(
                f"AI provider '{provider_name}' is not registered. "
                f"Available providers: {available}"
            )

        return cls._providers[provider_name]

    @classmethod
    def get_default_name(cls) -> str:
        """Get the name of the default provider."""
        if not cls._initialized:
            cls.initialize()
        return cls._default_provider

    @classmethod
    def list_providers(cls) -> list[dict]:
        """List all registered providers with their status."""
        if not cls._initialized:
            cls.initialize()

        return [
            {
                "name": provider.name,
                "display_name": provider.display_name,
                "models": provider.supported_models,
                "is_configured": provider.is_configured(),
                "is_default": provider.name == cls._default_provider,
            }
            for provider in cls._providers.values()
        ]

    @classmethod
    def set_default(cls, name: str) -> None:
        """Set the default provider."""
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' is not registered.")
        if not cls._providers[name].is_configured():
            raise ValueError(f"Provider '{name}' is not configured.")
        cls._default_provider = name
        logger.info("Default AI provider changed to: %s", name)
