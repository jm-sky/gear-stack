"""Custom exceptions for AI module."""


class AIError(Exception):
    """Base exception for AI module."""

    pass


class TokenValidationError(AIError):
    """Raised when API token validation fails."""

    pass


class OpenRouterError(AIError):
    """Raised when OpenRouter API call fails."""

    pass


class CacheError(AIError):
    """Raised when cache operation fails."""

    pass


class StructuredOutputParsingError(AIError):
    """Raised when structured output parsing fails."""

    pass


class ModelNotAvailableError(AIError):
    """Raised when requested model is not available."""

    pass


class AdminRequiredError(AIError):
    """Raised when non-admin user attempts to access AI features."""

    pass
