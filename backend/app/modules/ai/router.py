"""Main AI module router."""

from fastapi import APIRouter

from app.modules.ai.dependencies import require_admin

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health", dependencies=[])
async def health_check() -> dict[str, str]:
    """Health check endpoint for AI module.

    Returns:
        Status message
    """
    return {"status": "ok", "module": "ai"}


@router.get("/status")
async def get_ai_status() -> dict[str, bool]:
    """Get AI module status.

    Requires admin access.

    Returns:
        Dict with AI module status
    """
    from app.core.config import settings

    return {"enabled": settings.ai.enabled, "cache_enabled": settings.ai.cache_enabled}


# Sub-routers will be added in Phase 2:
# - router.include_router(chat_router, prefix="/chat")
# - router.include_router(settings_router, prefix="/settings")
# - router.include_router(history_router, prefix="/history")
