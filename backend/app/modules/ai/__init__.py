"""AI module for OpenRouter integration.

This module provides AI-powered features for Gear Stack including:
- Chat interface with structured output
- Automatic data updates from AI responses
- History tracking
- Cost and token usage monitoring

Currently restricted to admin users only.
"""

from .router import router

__all__ = ["router"]
