"""OpenRouter AI provider using OpenAI SDK.

OpenRouter officially recommends using the OpenAI library with a custom base URL.
This approach ensures compatibility and receives upstream updates automatically.

References:
- https://openrouter.ai/docs/quickstart
- https://github.com/openai/openai-python
"""

import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings

from ..exceptions import OpenRouterError
from .base import AIProvider
from .types import ChatResponse, CostInfo, Message, TokenUsage

logger = logging.getLogger(__name__)


class OpenRouterProvider(AIProvider):
    """OpenRouter provider using OpenAI SDK."""

    def __init__(self, api_key: str | None = None):
        """Initialize OpenRouter provider.

        Args:
            api_key: API key (defaults to system key from settings)
        """
        self.api_key = api_key or settings.ai.openrouter_api_key
        self.base_url = settings.ai.openrouter_base_url

        if not self.api_key:
            raise OpenRouterError("OpenRouter API key not configured")

        # Initialize OpenAI client with OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def chat(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int | None = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> ChatResponse:
        """Send chat completion request via OpenAI SDK.

        Args:
            messages: List of messages
            model: Model identifier (e.g., 'anthropic/claude-3.5-sonnet')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            ChatResponse: Response from OpenRouter

        Raises:
            OpenRouterError: If API request fails
        """
        try:
            # Prepare request parameters
            params: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            # Add additional parameters
            params.update(kwargs)

            # Make request using OpenAI SDK
            response = await self.client.chat.completions.create(**params)

            # Extract response data
            content = response.choices[0].message.content or ""
            usage_data = response.usage

            tokens: TokenUsage = {
                "input": usage_data.prompt_tokens if usage_data else 0,
                "output": usage_data.completion_tokens if usage_data else 0,
                "total": usage_data.total_tokens if usage_data else 0,
            }

            # OpenRouter may provide cost info in response metadata
            # (check response._raw_response if available)
            cost_info: CostInfo | None = None

            # Extract provider from model string (e.g., "anthropic/claude-3.5-sonnet" -> "anthropic")
            provider = model.split("/")[0] if "/" in model else "unknown"

            return ChatResponse(
                content=content,
                model=response.model,
                provider=provider,
                tokens=tokens,
                cost=cost_info,
                raw_response=response.model_dump(),
            )

        except OpenAIError as e:
            logger.error(f"OpenRouter API error (via OpenAI SDK): {e}")
            raise OpenRouterError(f"OpenRouter API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenRouter provider: {e}")
            raise OpenRouterError(f"Unexpected error: {str(e)}")

    async def validate_token(self, api_key: str) -> bool:
        """Validate OpenRouter API token.

        Args:
            api_key: API key to validate

        Returns:
            bool: True if valid

        Raises:
            OpenRouterError: If validation fails
        """
        try:
            # Create temporary client with provided key
            test_client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.base_url,
            )

            # Make minimal test request
            await test_client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )

            return True

        except OpenAIError as e:
            # Check if it's authentication error
            if "401" in str(e) or "authentication" in str(e).lower():
                return False
            logger.error(f"Token validation error: {e}")
            raise OpenRouterError(f"Failed to validate token: {str(e)}")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise OpenRouterError(f"Failed to validate token: {str(e)}")
