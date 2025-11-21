"""Email service for sending various types of emails."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import EmailSettings, settings

if TYPE_CHECKING:
    from .adapter import EmailAdapter

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending templated emails."""

    adapter: "EmailAdapter"
    templates_dir: Path
    jinja_env: Environment

    def __init__(self, adapter: "EmailAdapter"):
        """Initialize email service with adapter.

        Args:
            adapter: Email adapter (FileEmailAdapter or SMTPEmailAdapter)
        """
        self.adapter = adapter
        self.templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)), autoescape=select_autoescape(["html", "xml"]))
        # Primary color from frontend: oklch(0.646 0.222 41.116) converted to hex for email compatibility
        self.primary_color = "#D97757"

    async def send_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: dict,
        from_email: str | None = None,
        user_id: str | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> bool:
        """Send email using template.

        Args:
            to: Recipient email address
            subject: Email subject
            template_name: Name of template file (without .html)
            context: Template context variables
            from_email: Sender email address (optional)
            user_id: Related user ID for audit logging (optional)
            related_entity_type: Type of related entity (optional)
            related_entity_id: ID of related entity (optional)

        Returns:
            True if email sent successfully
        """
        try:
            # Add common context variables (app_name, primary_color, frontend_url)
            context_with_defaults = {
                "app_name": settings.app.display_name,
                "primary_color": self.primary_color,
                "frontend_url": settings.frontend_url,
                **context,  # User-provided context overrides defaults
            }

            # Load and render template
            template = self.jinja_env.get_template(f"{template_name}.html")
            html_body = template.render(**context_with_defaults)

            # Generate text version (simple strip of HTML tags)
            text_body = self._html_to_text(html_body)

            # Check if adapter supports audit parameters
            # (AuditEmailAdapter has these params, standard adapters don't)
            send_params = {
                "to": to,
                "subject": subject,
                "html_body": html_body,
                "text_body": text_body,
                "from_email": from_email,
            }

            # Add audit parameters if adapter supports them
            if hasattr(self.adapter, "repository"):
                # This is an AuditEmailAdapter
                send_params["template_name"] = template_name
                send_params["template_context"] = context
                send_params["user_id"] = user_id
                send_params["related_entity_type"] = related_entity_type
                send_params["related_entity_id"] = related_entity_id

            # Send via adapter
            return await self.adapter.send_email(**send_params)

        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (simple implementation).

        Args:
            html: HTML string

        Returns:
            Plain text version
        """
        # Simple HTML to text conversion
        import re

        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    async def send_welcome_email(self, to: str, name: str, user_id: str | None = None) -> bool:
        """Send welcome email to new user.

        Args:
            to: Recipient email address
            name: User name
            user_id: User ID for audit logging (optional)

        Returns:
            True if email sent successfully
        """
        return await self.send_email(
            to=to,
            subject=f"Welcome to {settings.app.display_name}!",
            template_name="welcome",
            context={"name": name, "email": to},
            user_id=user_id,
            related_entity_type="user" if user_id else None,
            related_entity_id=user_id,
        )

    async def send_email_verification_email(self, to: str, name: str, verification_token: str, user_id: str | None = None) -> bool:
        """Send email verification message.

        Args:
            to: Recipient email address
            name: User name
            verification_token: Email verification token
            user_id: User ID for audit logging (optional)

        Returns:
            True if email sent successfully
        """
        verification_link = f"{settings.frontend_url}/auth/verify-email?token={verification_token}"
        return await self.send_email(
            to=to,
            subject=f"Verify your email address - {settings.app.display_name}",
            template_name="email_verification",
            context={
                "name": name,
                "email": to,
                "verification_link": verification_link,
                "token": verification_token,
                "expires_hours": settings.security.email_verification_token_expires_hours,
            },
            user_id=user_id,
            related_entity_type="user" if user_id else None,
            related_entity_id=user_id,
        )

    async def send_password_reset_email(self, to: str, name: str, reset_token: str, user_id: str | None = None) -> bool:
        """Send password reset email.

        Args:
            to: Recipient email address
            name: User name
            reset_token: Password reset token
            user_id: User ID for audit logging (optional)

        Returns:
            True if email sent successfully
        """
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
        return await self.send_email(
            to=to,
            subject=f"Password Reset Request - {settings.app.display_name}",
            template_name="password_reset",
            context={
                "name": name,
                "email": to,
                "reset_link": reset_link,
                "token": reset_token,
                "expires_hours": settings.security.password_reset_token_expires_hours,
            },
            user_id=user_id,
            related_entity_type="user" if user_id else None,
            related_entity_id=user_id,
        )

    async def send_password_changed_email(
        self,
        to: str,
        name: str,
        ip_address: str | None = None,
        user_id: str | None = None,
    ) -> bool:
        """Send password changed notification email.

        Args:
            to: Recipient email address
            name: User name
            ip_address: IP address where change occurred (optional)
            user_id: User ID for audit logging (optional)

        Returns:
            True if email sent successfully
        """
        return await self.send_email(
            to=to,
            subject=f"Password Changed - {settings.app.display_name}",
            template_name="password_changed",
            context={
                "name": name,
                "email": to,
                "ip_address": ip_address or "Unknown",
            },
            user_id=user_id,
            related_entity_type="user" if user_id else None,
            related_entity_id=user_id,
        )

    async def send_account_deleted_email(self, to: str, name: str, user_id: str | None = None) -> bool:
        """Send account deletion confirmation email.

        Args:
            to: Recipient email address
            name: User name
            user_id: User ID for audit logging (optional)

        Returns:
            True if email sent successfully
        """
        return await self.send_email(
            to=to,
            subject=f"Account Deleted - {settings.app.display_name}",
            template_name="account_deleted",
            context={"name": name, "email": to},
            user_id=user_id,
            related_entity_type="user" if user_id else None,
            related_entity_id=user_id,
        )


def get_email_service() -> EmailService:
    """Get email service instance with configured adapter.

    Automatically wraps adapters with:
    - RetrySMTPAdapter: If enable_retry=True (for SMTP only)
    - AuditEmailAdapter: If enable_audit=True

    Returns:
        EmailService instance
    """
    from .adapter import EmailAdapter
    from .file_adapter import FileEmailAdapter
    from .smtp_adapter import SMTPEmailAdapter
    from .retry_smtp_adapter import RetrySMTPAdapter
    from .audit_adapter import AuditEmailAdapter
    from app.core.database import get_db

    # Get email settings from config
    email_settings: EmailSettings | None = getattr(settings, "email", None)

    adapter: EmailAdapter
    if not email_settings or not email_settings.enabled:
        # Email disabled, use file adapter as fallback
        logger.warning("Email service is disabled, using file adapter")
        adapter = FileEmailAdapter(file_path="./emails")
        return EmailService(adapter)

    # Choose base adapter based on configuration
    if email_settings.adapter == "smtp":
        # Use retry SMTP if enabled
        if email_settings.enable_retry:
            adapter = RetrySMTPAdapter(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password,
                from_email=email_settings.smtp_from,
                use_tls=email_settings.smtp_use_tls,
                max_retries=email_settings.max_retries,
            )
            logger.info(f"Using RetrySMTPAdapter with {email_settings.max_retries} " f"max retries")
        else:
            adapter = SMTPEmailAdapter(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password,
                from_email=email_settings.smtp_from,
                use_tls=email_settings.smtp_use_tls,
            )
    else:
        # Default to file adapter
        adapter = FileEmailAdapter(file_path=email_settings.file_path)

    return EmailService(adapter)


def get_email_service_with_audit(
    db: "AsyncSession",
) -> EmailService:
    """Get email service with audit logging enabled.

    This is a request-scoped dependency that wraps the email adapter
    with AuditEmailAdapter when audit logging is enabled in settings.

    Use this as a FastAPI dependency:
        @router.post("/send-email")
        async def send_email(
            email_service: EmailService = Depends(get_email_service_with_audit)
        ):
            await email_service.send_welcome_email(...)

    Args:
        db: Database session (FastAPI dependency)

    Returns:
        EmailService instance with audit support if enabled
    """
    from .adapter import EmailAdapter
    from .file_adapter import FileEmailAdapter
    from .smtp_adapter import SMTPEmailAdapter
    from .retry_smtp_adapter import RetrySMTPAdapter
    from .audit_adapter import AuditEmailAdapter
    from sqlalchemy.ext.asyncio import AsyncSession

    # Get email settings from config
    email_settings: EmailSettings | None = getattr(settings, "email", None)

    adapter: EmailAdapter
    if not email_settings or not email_settings.enabled:
        # Email disabled, use file adapter as fallback
        adapter = FileEmailAdapter(file_path="./emails")
        return EmailService(adapter)

    # Choose base adapter based on configuration
    if email_settings.adapter == "smtp":
        # Use retry SMTP if enabled
        if email_settings.enable_retry:
            adapter = RetrySMTPAdapter(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password,
                from_email=email_settings.smtp_from,
                use_tls=email_settings.smtp_use_tls,
                max_retries=email_settings.max_retries,
            )
        else:
            adapter = SMTPEmailAdapter(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password,
                from_email=email_settings.smtp_from,
                use_tls=email_settings.smtp_use_tls,
            )
    else:
        # Default to file adapter
        adapter = FileEmailAdapter(file_path=email_settings.file_path)

    # Wrap with audit adapter if enabled
    if email_settings.enable_audit:
        adapter = AuditEmailAdapter(
            wrapped_adapter=adapter,
            db=db,
            store_body=True,  # Store full email body for audit trail
        )
        logger.debug("Email service created with audit logging enabled")

    return EmailService(adapter)
