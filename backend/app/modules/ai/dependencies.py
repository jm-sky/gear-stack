"""FastAPI dependencies for AI module."""

from fastapi import Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser

from .exceptions import AdminRequiredError


async def require_admin(current_user: CurrentUser = Depends()) -> CurrentUser:
    """Require admin user for AI endpoints.

    Args:
        current_user: Currently authenticated user from auth module

    Returns:
        CurrentUser: The admin user

    Raises:
        HTTPException: 403 Forbidden if user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are only available for admin users",
        )
    return current_user


# Type alias for clarity
AdminUser = CurrentUser
