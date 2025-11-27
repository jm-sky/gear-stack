"""FastAPI dependencies for AI module."""

from app.modules.auth.dependencies import PremiumOrHigherUser

# AI features are available for Premium users, Administrators, and Owners
# Regular User role does not have access
AdminUser = PremiumOrHigherUser
