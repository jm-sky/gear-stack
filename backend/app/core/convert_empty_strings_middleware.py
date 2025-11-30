"""Middleware to convert empty strings to None in request body.

This middleware automatically converts empty strings ('') to None (null in JSON)
before Pydantic validation, ensuring consistent handling of optional fields.

Similar to Laravel's ConvertEmptyStringsToNull middleware.

Uses pure ASGI middleware pattern for reliable body modification.
"""

import json
from collections.abc import Awaitable, Callable
from typing import Any


def _convert_empty_strings_to_none(obj: Any) -> Any:
    """Recursively convert empty strings to None."""
    if isinstance(obj, dict):
        return {k: _convert_empty_strings_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_empty_strings_to_none(item) for item in obj]
    elif isinstance(obj, str) and obj == "":
        return None
    return obj


class ConvertEmptyStringsToNoneMiddleware:
    """
    Convert empty strings to None in request body.

    This middleware automatically converts empty strings ('') to None (null in JSON)
    before Pydantic validation, ensuring consistent handling of optional fields.

    Only processes POST, PUT, PATCH requests with JSON content type.
    Recursively processes nested objects and arrays.

    Example:
        Input:  {"name": "John", "email": "", "age": 25}
        Output: {"name": "John", "email": None, "age": 25}
    """

    def __init__(self, app: Callable[[dict[str, Any], Callable, Callable], Awaitable[None]]) -> None:
        """Initialize middleware with ASGI app."""
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Callable[[], Awaitable[dict[str, Any]]], send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        """
        Process ASGI request and convert empty strings to None.

        Args:
            scope: ASGI connection scope
            receive: Receive callable
            send: Send callable
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        if method not in ("POST", "PUT", "PATCH"):
            await self.app(scope, receive, send)
            return

        # Check content-type header
        headers = dict(scope.get("headers", []))
        content_type = headers.get(b"content-type", b"").decode()

        if not content_type.startswith("application/json"):
            await self.app(scope, receive, send)
            return

        # Modify body
        async def modify_body() -> dict[str, Any]:
            message = await receive()
            assert message["type"] == "http.request"

            body_bytes = message.get("body", b"")

            if not body_bytes:
                return message

            try:
                data = json.loads(body_bytes.decode())
                # Convert empty strings to None
                data = _convert_empty_strings_to_none(data)
                # Update message with modified body
                message["body"] = json.dumps(data).encode()
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, let Pydantic handle it
                pass

            return message

        await self.app(scope, modify_body, send)
