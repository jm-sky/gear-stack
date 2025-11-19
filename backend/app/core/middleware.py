"""Middleware configuration for the application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings


def setup_middleware(app: FastAPI) -> None:
    """
    Configure middleware for the FastAPI application.

    Security middleware is configured based on environment:
    - CORS: Always enabled with configurable origins (CORS_ORIGINS env var)
    - Trusted Host: Enabled in production with configurable hosts (ALLOWED_HOSTS env var)

    Args:
        app: FastAPI application instance
    """
    # CORS Middleware - always enabled
    # Configure via CORS_ORIGINS environment variable
    # Example: CORS_ORIGINS='["https://example.com","https://app.example.com"]'
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=settings.server.cors_credentials,
        allow_methods=settings.server.cors_methods,
        allow_headers=settings.server.cors_headers,
    )

    # Trusted Host Middleware - production security
    # Prevents HTTP Host header attacks
    # Configure via ALLOWED_HOSTS environment variable
    # Example: ALLOWED_HOSTS='["example.com","*.example.com","api.example.com"]'
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.server.allowed_hosts,
        )

    # Add custom middleware here
    # Example: Request logging, rate limiting, etc.
