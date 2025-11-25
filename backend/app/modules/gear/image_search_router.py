"""API router for image search functionality."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import AdminUser
from app.modules.gear.image_search_schemas import (
    DownloadAndAddImageRequest,
    ImageSearchRequest,
    ImageSearchResponse,
)
from app.modules.gear.image_search_service import ImageSearchService

router = APIRouter(prefix="/image-search", tags=["image-search"])


@router.post("/search", response_model=ImageSearchResponse)
async def search_images(
    request: ImageSearchRequest,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> ImageSearchResponse:
    """
    Search for images for an item (admin only).

    Args:
        request: Search request with item_id and optional query/engine_ids
        db: Database session

    Returns:
        List of image search results
    """
    service = ImageSearchService(db)

    try:
        results = await service.search_images(
            item_id=request.item_id,
            query=request.search_query,
            engine_ids=request.engine_ids,
        )

        return ImageSearchResponse(results=results, total=len(results))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search images: {str(e)}",
        )


@router.post("/download-and-add", response_model=dict)
async def download_and_add_image(
    request: DownloadAndAddImageRequest,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Download image from URL and add it to item gallery (admin only).

    Args:
        request: Download request with image_url and source info
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Image metadata
    """
    service = ImageSearchService(db)

    try:
        result = await service.download_and_add_image(
            item_id=request.item_id,
            user_id=current_user.id,
            image_url=request.image_url,
            source_url=request.source_url,
            source_name=request.source_name,
            search_engine_id=request.search_engine_id,
            is_primary=request.is_primary,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download and add image: {str(e)}",
        )
