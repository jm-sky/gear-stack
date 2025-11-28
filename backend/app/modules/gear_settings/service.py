"""Business logic service for gear settings."""

from .db_models import GearSettingsDB
from .repository import GearSettingsRepository
from .schemas import GearSettingsResponse, GearSettingsUpdate


class GearSettingsService:
    """Service for gear settings business logic."""

    def __init__(self, repository: GearSettingsRepository):
        """Initialize service with repository.

        Args:
            repository: Gear settings repository instance
        """
        self.repository = repository

    def _map_to_response(self, settings: GearSettingsDB) -> GearSettingsResponse:
        """Map database model to response schema.

        Args:
            settings: Database settings model

        Returns:
            Settings response schema
        """
        return GearSettingsResponse(
            customCategories=settings.custom_categories,
            customContainerTypes=settings.custom_container_types,
            customBrands=settings.custom_brands,
            preferredWeightUnit=settings.preferred_weight_unit,
            defaultCurrency=settings.default_currency,
        )

    async def get_settings(self, user_id: str) -> GearSettingsResponse:
        """Get gear settings for user.

        Args:
            user_id: User ID

        Returns:
            Gear settings response
        """
        settings = await self.repository.get_or_create(user_id)
        return self._map_to_response(settings)

    async def update_settings(self, user_id: str, updates: GearSettingsUpdate) -> GearSettingsResponse:
        """Update gear settings for user.

        Args:
            user_id: User ID
            updates: Settings updates

        Returns:
            Updated gear settings response
        """
        settings = await self.repository.get_or_create(user_id)

        if updates.customCategories is not None:
            settings.custom_categories = updates.customCategories
        if updates.customContainerTypes is not None:
            settings.custom_container_types = updates.customContainerTypes
        if updates.customBrands is not None:
            settings.custom_brands = updates.customBrands
        if updates.preferredWeightUnit is not None:
            settings.preferred_weight_unit = updates.preferredWeightUnit
        if updates.defaultCurrency is not None:
            settings.default_currency = updates.defaultCurrency

        updated = await self.repository.update(settings)
        return self._map_to_response(updated)
