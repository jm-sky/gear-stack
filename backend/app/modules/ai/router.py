"""Main AI module router.

This router will be extended in Phase 2 with actual endpoints.
For now, it's a placeholder to allow module registration.
"""

from fastapi import APIRouter

# Create main AI router
router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/health")
async def health_check():
    """Health check endpoint for AI module.

    Returns:
        dict: Health status
    """
    return {"status": "ok", "module": "ai"}


# Sub-routers will be added in Phase 2:
# from .routers import chat, settings, history, models
# router.include_router(chat.router)
# router.include_router(settings.router)
# router.include_router(history.router)
# router.include_router(models.router)
