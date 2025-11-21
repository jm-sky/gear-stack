"""FastAPI router for authentication endpoints.

This module provides authentication endpoints with security features:
- Rate limiting (ENABLED by default - essential security)
- reCAPTCHA protection (decorators present, DISABLED by default)

To enable reCAPTCHA (optional but recommended):
1. Set RECAPTCHA_ENABLED=true in .env
2. Configure RECAPTCHA_SECRET_KEY and RECAPTCHA_SITE_KEY
3. Decorators are already applied - they become active when enabled

To disable rate limiting (NOT recommended):
- Comment out @rate_limit decorators
- Set RATE_LIMIT_ENABLED=false in .env
"""

from typing import TYPE_CHECKING, Annotated, Any, TypeAlias, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

if TYPE_CHECKING:
    from app.modules.two_factor.schemas import (
        DisableTotpRequest,
        InitiatePasskeyRegistrationRequest,
        CompletePasskeyRegistrationRequest,
        CompletePasskeyAuthenticationRequest,
        UpdatePreferredMethodRequest,
        VerifyTotpSetupRequest,
    )
    from app.modules.auth.types.repository import UserRepositoryInterface

from .decorators import rate_limit, recaptcha_protected
from .dependencies import AuthServiceDep, CurrentUser
from .exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from .schemas import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    EmailVerificationRequest,
    ForgotPasswordRequest,
    LoginResponse,
    MessageResponse,
    ResendEmailVerificationRequest,
    ResetPasswordRequest,
    TokenRefresh,
    UserLogin,
    UserRegister,
    UserResponse,
)

# Import 2FA response type if available for union type
try:
    from app.modules.two_factor.schemas import TwoFactorRequiredResponse

    LoginResponseType: TypeAlias = Union[LoginResponse, TwoFactorRequiredResponse]
except ImportError:
    LoginResponseType: TypeAlias = LoginResponse  # type: ignore[misc, no-redef]

# Create router
router = APIRouter()


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account and send email verification link",
    tags=["Authentication"],
)
@rate_limit("5/minute")  # Prevent registration abuse
@recaptcha_protected("register")  # Disabled by default, enable via RECAPTCHA_ENABLED=true
async def register(user_data: UserRegister, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    """
    Register a new user.

    Security features:
    - ✅ Rate limiting: 5 requests/minute (enabled)
    - ⚪ reCAPTCHA: Disabled by default (enable via RECAPTCHA_ENABLED=true)
    - 💡 Recommendation: Add email verification in production
    """
    try:
        await auth_service.register_user(email=user_data.email, password=user_data.password, name=user_data.name)
        return MessageResponse(message="Registration successful. Please check your email to verify your account.")
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")


@router.post("/login", summary="Login user", description="Authenticate user and return JWT tokens or 2FA challenge", tags=["Authentication"])
@rate_limit("10/minute")  # CRITICAL: Prevent brute force attacks
@recaptcha_protected("login")  # Disabled by default, enable via RECAPTCHA_ENABLED=true
async def login(credentials: UserLogin, auth_service: AuthServiceDep, request: Request) -> LoginResponseType:
    """
    Login user and return tokens or 2FA challenge.

    If user has 2FA enabled, returns TwoFactorRequiredResponse.
    Otherwise, returns LoginResponse with tokens.

    Security features:
    - ✅ Rate limiting: 10 requests/minute (enabled - CRITICAL)
    - ⚪ reCAPTCHA: Disabled by default (enable via RECAPTCHA_ENABLED=true)
    - 💡 Recommendation: Implement account lockout after N failed attempts
    """
    try:
        # Debug: Log what type of auth service we're using
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Login attempt for {credentials.email}, auth_service type: {type(auth_service).__name__}")

        result = await auth_service.login_user(email=credentials.email, password=credentials.password)

        # Debug: Log what we're returning
        if hasattr(result, "requiresTwoFactor"):
            logger.info(f"Login response: TwoFactorRequiredResponse (2FA required)")
        elif hasattr(result, "accessToken"):
            logger.info(f"Login response: LoginResponse (normal login, no 2FA)")
        else:
            logger.warning(f"Login response: Unknown type: {type(result)}")

        return result
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=dict, summary="Refresh access token", description="Get new access token using refresh token", tags=["Authentication"])
@rate_limit("20/minute")  # Prevent token refresh abuse
async def refresh_token(token_data: TokenRefresh, auth_service: AuthServiceDep, request: Request) -> dict:
    """
    Refresh access token.

    Security features:
    - ✅ Rate limiting: 20 requests/minute (enabled)
    - 💡 Recommendation: Consider implementing refresh token rotation
    """
    try:
        return await auth_service.refresh_access_token(token_data.refreshToken)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", response_model=MessageResponse, summary="Logout user", description="Logout current user", tags=["Authentication"])
async def logout(current_user: CurrentUser) -> MessageResponse:
    """
    Logout current user.

    Security features:
    - ✅ Authentication required (JWT token via CurrentUser)
    - TODO: Invalidate token
    """
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse, summary="Request password reset", description="Request a password reset email (development: token is printed to console)", tags=["Authentication"])
@rate_limit("3/minute")  # CRITICAL: Prevent email enumeration and spam
@recaptcha_protected("forgot_password")  # Disabled by default, enable via RECAPTCHA_ENABLED=true
async def forgot_password(request_data: ForgotPasswordRequest, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    """
    Request password reset.

    Security features:
    - ✅ Rate limiting: 3 requests/minute (enabled - CRITICAL)
    - ⚪ reCAPTCHA: Disabled by default, RECOMMENDED (enable via RECAPTCHA_ENABLED=true)
    - ✅ Generic response message (prevents email enumeration)
    """
    # Always return success message to prevent email enumeration
    await auth_service.request_password_reset(request_data.email)
    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse, summary="Reset password", description="Reset password using reset token", tags=["Authentication"])
@rate_limit("5/minute")  # Prevent token brute force
async def reset_password(request_data: ResetPasswordRequest, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    """
    Reset password with token.

    Security features:
    - ✅ Rate limiting: 5 requests/minute (enabled)
    - ✅ Token is single-use and short-lived (1 hour)
    """
    try:
        await auth_service.reset_password(request_data.token, request_data.newPassword)
        return MessageResponse(message="Password has been reset successfully")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")


@router.post("/change-password", response_model=MessageResponse, summary="Change password", description="Change password for authenticated user", tags=["Authentication"])
@rate_limit("3/minute")  # Prevent password change abuse
async def change_password(request_data: ChangePasswordRequest, current_user: CurrentUser, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    """
    Change password for authenticated user.

    Security features:
    - ✅ Rate limiting: 3 requests/minute (enabled)
    - ✅ Authentication required (JWT token)
    - ✅ Current password verification required
    """
    try:
        # Get client IP address for security notification
        client_ip = request.client.host if request.client else None
        await auth_service.change_password(user_id=current_user.id, current_password=request_data.currentPassword, new_password=request_data.newPassword, ip_address=client_ip)
        return MessageResponse(message="Password changed successfully")
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/me", response_model=UserResponse, summary="Get current user", description="Get currently authenticated user information", tags=["Authentication"])
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """
    Get current user information.

    Security features:
    - ✅ Authentication required (JWT token via CurrentUser)
    - ⚪ Rate limiting: Not needed (read-only, already auth-protected)
    """
    return UserResponse(**current_user.to_response())


@router.post(
    "/email/verify",
    response_model=MessageResponse,
    summary="Verify email address",
    description="Confirm email using verification token sent after registration",
    tags=["Authentication"],
)
async def verify_email(request_data: EmailVerificationRequest, auth_service: AuthServiceDep) -> MessageResponse:
    try:
        await auth_service.verify_email(request_data.token)
        return MessageResponse(message="Email address verified successfully.")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")


@router.post(
    "/email/resend",
    response_model=MessageResponse,
    summary="Resend email verification link",
    description="Resend verification link to the provided email address",
    tags=["Authentication"],
)
@rate_limit("3/hour")
async def resend_email_verification(request_data: ResendEmailVerificationRequest, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    await auth_service.resend_email_verification(request_data.email)
    return MessageResponse(message="If the email exists, a new verification link has been sent.")


@router.delete("/account", response_model=MessageResponse, summary="Delete account", description="Delete current user's account (soft delete by default)", tags=["Authentication"])
@rate_limit("1/day")  # Prevent abuse - only allow one deletion per day
async def delete_account(request_data: DeleteAccountRequest, current_user: CurrentUser, auth_service: AuthServiceDep, request: Request) -> MessageResponse:
    """
    Delete current user's account.

    Security features:
    - ✅ Rate limiting: 1 request/day (enabled - CRITICAL)
    - ✅ Authentication required (JWT token)
    - ✅ Password verification (optional but recommended)
    - ✅ Confirmation phrase required
    - ✅ Soft delete by default (GDPR compliant with data anonymization)
    """
    try:
        await auth_service.delete_account(user_id=current_user.id, password=request_data.password, confirmation=request_data.confirmation, soft_delete=True)
        return MessageResponse(message="Account has been deleted successfully")
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
