"""Pydantic schemas for settings endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


SupportedLocale = Literal["en", "pl"]


class SettingsResponse(BaseModel):
    darkMode: bool = Field(default=False)
    locale: SupportedLocale = Field(default="en")


class UpdateSettingsRequest(BaseModel):
    darkMode: bool | None = Field(default=None)
    locale: SupportedLocale | None = Field(default=None)
