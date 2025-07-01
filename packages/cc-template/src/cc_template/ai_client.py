"""AI client integration for content generation."""

import os
import logging
from typing import Optional, Dict, Any

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)


class AIClient:
    """Unified AI client for content generation."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize AI client with specified provider."""
        self.provider = provider or self._detect_provider()
        self.client = self._initialize_client()

    def _detect_provider(self) -> str:
        """Auto-detect which AI provider to use based on available API keys."""
        if os.getenv("OPENAI_API_KEY") and OPENAI_AVAILABLE:
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
            return "anthropic"
        else:
            raise ValueError(
                "No AI provider configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable "
                "and ensure the corresponding package is installed."
            )

    def _initialize_client(self):
        """Initialize the appropriate AI client."""
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                )
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            return openai.OpenAI(api_key=api_key)

        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError(
                    "Anthropic package not installed. Run: pip install anthropic"
                )
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            return anthropic.Anthropic(api_key=api_key)

        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the configured AI provider."""
        if self.provider == "openai":
            return self._generate_openai(prompt, **kwargs)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _generate_openai(self, prompt: str, **kwargs) -> str:
        """Generate content using OpenAI."""
        model = kwargs.get("model", "gpt-4")
        max_tokens = kwargs.get("max_tokens", 4000)
        temperature = kwargs.get("temperature", 0.7)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _generate_anthropic(self, prompt: str, **kwargs) -> str:
        """Generate content using Anthropic Claude."""
        model = kwargs.get("model", "claude-3-sonnet-20240229")
        max_tokens = kwargs.get("max_tokens", 4000)
        temperature = kwargs.get("temperature", 0.7)

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            "provider": self.provider,
            "available_providers": {
                "openai": OPENAI_AVAILABLE and bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": ANTHROPIC_AVAILABLE
                and bool(os.getenv("ANTHROPIC_API_KEY")),
            },
        }


def create_ai_client(provider: Optional[str] = None) -> AIClient:
    """Factory function to create an AI client."""
    return AIClient(provider)
