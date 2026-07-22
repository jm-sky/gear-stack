"""Shared FastAPI dependencies for the gear module.

Extracted from router.py so item_image_router.py (included by router.py) can
depend on optional authentication without causing a circular import.
"""

from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.models import User
from app.modules.auth.repositories import get_user_repository
from app.modules.auth.types.repository import UserRepositoryInterface

# Optional authentication for public endpoints
optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Security(optional_security),
    user_repository: Annotated[UserRepositoryInterface | None, Depends(get_user_repository)] = None,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        from app.core.auth.token_blacklist import TokenBlacklistService
        from app.core.config import settings
        from app.core.redis import get_redis_client
        from app.modules.auth.dependencies import _verify_user_token

        token = credentials.credentials
        if user_repository is None:
            return None

        # Get blacklist service
        redis_client = await get_redis_client()
        blacklist_service = TokenBlacklistService(redis_client=redis_client, key_prefix=settings.redis.token_blacklist_prefix)

        return await _verify_user_token(token, user_repository, blacklist_service, None)
    except Exception:
        # If authentication fails, return None (endpoint is public)
        return None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]
