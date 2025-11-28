"""Middleware to convert empty strings to None in request body.

This middleware automatically converts empty strings ('') to None (null in JSON)
before Pydantic validation, ensuring consistent handling of optional fields.

Similar to Laravel's ConvertEmptyStringsToNull middleware.
"""

import json
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ConvertEmptyStringsToNoneMiddleware(BaseHTTPMiddleware):
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

    async def dispatch(self, request: Request, call_next):
        """
        Process request and convert empty strings to None.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler
            
        Returns:
            Response from next handler
        """
        # Only process POST, PUT, PATCH requests with JSON body
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        data = self._convert_empty_strings_to_none(data)
                        # Reconstruct request with modified body
                        async def receive():
                            return {"type": "http.request", "body": json.dumps(data).encode()}
                        request._receive = receive
                    except (json.JSONDecodeError, ValueError):
                        # If JSON parsing fails, let Pydantic handle it
                        pass

        response = await call_next(request)
        return response

    def _convert_empty_strings_to_none(self, obj: Any) -> Any:
        """
        Recursively convert empty strings to None.
        
        Args:
            obj: Object to process (dict, list, or any other type)
            
        Returns:
            Object with empty strings converted to None
        """
        if isinstance(obj, dict):
            return {k: self._convert_empty_strings_to_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_empty_strings_to_none(item) for item in obj]
        elif isinstance(obj, str) and obj == "":
            return None
        return obj

