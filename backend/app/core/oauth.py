"""OAuth authentication service for multiple providers."""

import secrets
from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

from app.core.config import settings


class OAuthUserInfo(BaseModel):
    """Standardized OAuth user info (camelCase for API consistency)."""

    provider: str
    providerId: str
    email: str
    name: str | None = None
    avatarUrl: str | None = None


class OAuthTokenResponse(BaseModel):
    """OAuth token exchange response."""

    accessToken: str
    tokenType: str
    scope: str | None = None
    refreshToken: str | None = None


class OAuthProvider(ABC):
    """Abstract base class for OAuth providers."""

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token."""
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information using access token."""
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider implementation."""

    def __init__(self):
        self.client_id = settings.oauth.google_client_id
        self.client_secret = settings.oauth.google_client_secret
        self.redirect_uri = settings.oauth.google_redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_api_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email profile",
            "state": state,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """Exchange Google authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(f"Google OAuth error: {data.get('error_description', data['error'])}")

            return OAuthTokenResponse(
                accessToken=data["access_token"],
                tokenType=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                refreshToken=data.get("refresh_token"),
            )

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get Google user information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            user_data = response.json()

            if not user_data.get("verified_email", False):
                raise ValueError("Google account email is not verified")

            return OAuthUserInfo(
                provider="google",
                providerId=str(user_data["id"]),
                email=user_data["email"],
                name=user_data.get("name"),
                avatarUrl=user_data.get("picture"),
            )


class OAuthService:
    """Central OAuth service for managing multiple providers."""

    def __init__(self):
        self.providers = {
            "google": GoogleOAuthProvider(),
        }

    def get_provider(self, provider_name: str) -> OAuthProvider:
        """Get OAuth provider by name."""
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported OAuth provider: {provider_name}")
        return self.providers[provider_name]

    def generate_state(self) -> str:
        """Generate a secure state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)

    def get_authorization_url(self, provider_name: str, state: str) -> str:
        """Generate authorization URL for provider."""
        provider = self.get_provider(provider_name)
        return provider.get_authorization_url(state)

    async def exchange_code_for_token(self, provider_name: str, code: str) -> OAuthTokenResponse:
        """Exchange authorization code for access token."""
        provider = self.get_provider(provider_name)
        return await provider.exchange_code_for_token(code)

    async def get_user_info(self, provider_name: str, access_token: str) -> OAuthUserInfo:
        """Get user information from provider."""
        provider = self.get_provider(provider_name)
        return await provider.get_user_info(access_token)

    async def complete_oauth_flow(self, provider_name: str, code: str) -> tuple[OAuthUserInfo, OAuthTokenResponse]:
        """Complete OAuth flow: exchange code for token and get user info."""
        token_response = await self.exchange_code_for_token(provider_name, code)
        user_info = await self.get_user_info(provider_name, token_response.accessToken)
        return user_info, token_response


# Global OAuth service instance
oauth_service = OAuthService()
