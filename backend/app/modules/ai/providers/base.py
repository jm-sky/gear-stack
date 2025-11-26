"""Abstract base provider for AI integrations."""

from abc import ABC, abstractmethod

from .types import ChatResponse, Message


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str,
        max_tokens: int | None = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> ChatResponse:
        """Send chat completion request.

        Args:
            messages: List of messages in the conversation
            model: Model identifier
            max_tokens: Maximum tokens to generate (None = model default)
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResponse: Response from the AI model
        """
        pass

    @abstractmethod
    async def validate_token(self, api_key: str) -> bool:
        """Validate API token.

        Args:
            api_key: API key to validate

        Returns:
            bool: True if token is valid
        """
        pass
