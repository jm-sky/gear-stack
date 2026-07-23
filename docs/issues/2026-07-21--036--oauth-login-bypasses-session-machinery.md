# OAuth login bypasses session tracking, token-version, and 2FA machinery

**Status:** `done`
**Created:** 2026-07-21
**Severity:** Medium
**Module:** `auth` (backend — OAuth)
**Source:** [Security review — Backend](../reviews/2026-07-06-security-backend.md) (SEC-BE-02)

## Problem

Password login funnels through `AuthService._issue_login_tokens` ([`service.py:131`](../../backend/app/modules/auth/service.py)), which mints tokens with a session `jti`, the user's `tv` (token version), `emailVerified`, and 2FA claims, and registers the session in Redis via `track_user_session`.

`AuthService.login_with_oauth` ([`service.py:550`](../../backend/app/modules/auth/service.py)) instead calls the low-level builders directly:

```python
access_token = create_access_token({"sub": user.id})
refresh_token = create_refresh_token({"sub": user.id})
```

No `jti`, no `tv`, no `emailVerified`, no 2FA context, and no `track_user_session` call.

## Impact

- **Revocation gaps.** OAuth sessions are never tracked, so `TokenBlacklistService.blacklist_all_user_tokens` (used on password change / reset / account deletion) iterates the tracked JTIs and **silently misses OAuth sessions**. "Log out everywhere" does not cover OAuth logins.
- **Inconsistent token-version enforcement.** The dependency check compares `payload.get("tv", 0)` against `user.tokenVersion` ([`dependencies.py:139`](../../backend/app/modules/auth/dependencies.py)). OAuth tokens carry no `tv`, so they default to `0`. For any user whose `tokenVersion` has been incremented (after a password change/reset), a freshly minted OAuth token is **immediately rejected (401)** — OAuth login is effectively broken for those accounts. For users at `tokenVersion == 0`, the DB-fallback revocation path is bypassed.
- **Inconsistent 2FA enforcement.** OAuth tokens omit `tfaVerified`. A user with 2FA enabled gets a token that fails the `tfaVerified` gate at [`auth_utils`/`dependencies.py:177`](../../backend/app/modules/auth/dependencies.py) → locked out of OAuth; the OAuth path also never runs the 2FA challenge that password login does.

Currently lower-probability because all OAuth providers are unconfigured by default (empty client IDs/secrets in [`config.py`](../../backend/app/core/config.py) `OAuthSettings`), but GitHub OAuth login is being enabled (issue 014).

## Proposed fix

- Route OAuth login through `_issue_login_tokens(user, tfa_verified=..., tfa_method=...)` instead of calling `create_access_token`/`create_refresh_token` directly, so the session `jti`, `tv`, `emailVerified`, Redis session tracking, and 2FA handling are applied uniformly.
- Decide the 2FA policy for OAuth: either honor the user's 2FA (return the 2FA-required challenge, like password login) or document that OAuth accounts are exempt — but do not silently lock them out.

## Scope

- [x] `backend/app/modules/auth/service.py` — `login_with_oauth` reuses `_issue_login_tokens`
- [x] 2FA decision for OAuth logins (challenge vs. exempt)
- [x] Test: OAuth login after a `tokenVersion` bump still authenticates; "logout all sessions" revokes OAuth sessions

## Resolution (2026-07-22)

Decision (confirmed with the user): **OAuth honors 2FA the same as password login** — a 2FA-enabled account gets a `TwoFactorRequiredResponse` challenge from OAuth too, not silent exemption.

Implementation: split `login_with_oauth` into `_resolve_oauth_user` (lookup/link/create, no tokens) + `login_with_oauth` (calls `_resolve_oauth_user` then `_issue_login_tokens`), so the base `AuthService` path now gets `jti`/`tv`/`emailVerified`/session tracking like password login. Since `login_with_oauth` was never overridden in `AuthServiceWith2FA` (the service actually injected via `AuthServiceDep` — see `auth/dependencies.py:60`), it silently skipped 2FA entirely; added a `login_with_oauth` override there that checks `has_two_factor_enabled` and returns the same challenge `login_user` builds (extracted into a shared `_build_two_factor_challenge` helper) before falling through to `_issue_login_tokens`.

Tests: `backend/tests/test_auth_service.py::TestLoginWithOAuth` (base class: jti/tv present, survives a `tokenVersion` bump) and `backend/tests/test_oauth_2fa_login.py` (2FA-enabled OAuth user gets a challenge, not tokens).

**QA (2026-07-23):** ręczne potwierdzenie — OAuth działa poprawnie → status `done`.

## Verification

1. Enable a provider in a dev env; log in via OAuth; confirm the access token contains `jti`/`tv` and the session appears in Redis. — logic covered by unit tests; live provider not exercised this session.
2. Change password → confirm the prior OAuth session is revoked. — falls out of reusing `_issue_login_tokens`/`track_user_session`, not separately re-tested live.
3. OAuth login for a user with `tokenVersion > 0` succeeds. — covered by `test_login_with_oauth_survives_token_version_bump`.
