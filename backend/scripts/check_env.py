#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to verify environment variables."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

print("\n" + "="*60)
print("RECAPTCHA CONFIGURATION")
print("="*60)
print(f"Enabled: {settings.recaptcha.enabled}")
print(f"Site Key: {settings.recaptcha.site_key[:20]}..." if settings.recaptcha.site_key else "Site Key: NOT SET")
print(f"Secret Key: {settings.recaptcha.secret_key[:20]}..." if settings.recaptcha.secret_key else "Secret Key: NOT SET")
print(f"Min Score: {settings.recaptcha.min_score}")

print("\nRaw Environment Variables:")
for var in ["RECAPTCHA_ENABLED", "RECAPTCHA_SITE_KEY", "RECAPTCHA_SECRET_KEY", "RECAPTCHA_MIN_SCORE"]:
    value = os.getenv(var)
    if value and "KEY" in var:
        print(f"  {var}: {value[:20]}...")
    elif value:
        print(f"  {var}: {value}")
    else:
        print(f"  {var}: NOT SET")

print("\n" + "="*60)
print("OAUTH CONFIGURATION")
print("="*60)
print(f"Client ID: {settings.oauth.google_client_id[:20]}..." if settings.oauth.google_client_id else "Client ID: NOT SET")
print(f"Client Secret: {settings.oauth.google_client_secret[:20]}..." if settings.oauth.google_client_secret else "Client Secret: NOT SET")

print("\nRaw Environment Variables:")
for var in ["GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET"]:
    value = os.getenv(var)
    if value and "SECRET" in var:
        print(f"  {var}: {value[:20]}...")
    elif value:
        print(f"  {var}: {value}")
    else:
        print(f"  {var}: NOT SET")

print("\n" + "="*60)
if settings.recaptcha.enabled and settings.recaptcha.secret_key and settings.recaptcha.site_key:
    print("OK: All reCAPTCHA variables are set correctly!")
else:
    print("ERROR: reCAPTCHA configuration is incomplete!")
print("="*60)

# Test OAuth directly
print("\n" + "="*60)
print("TESTING OAUTH DIRECTLY")
print("="*60)
try:
    from app.core.oauth import oauth_service
    print(f"OAuth service initialized: {oauth_service is not None}")
    
    # Try to get auth URL
    state = oauth_service.generate_state()
    print(f"Generated state: {state[:20]}...")
    
    try:
        auth_url = oauth_service.get_authorization_url("google", state)
        print(f"Auth URL generated successfully")
        print(f"Auth URL (first 100 chars): {auth_url[:100]}...")
    except Exception as e:
        print(f"ERROR generating auth URL: {e}")
except Exception as e:
    print(f"ERROR initializing OAuth: {e}")
    import traceback
    traceback.print_exc()
