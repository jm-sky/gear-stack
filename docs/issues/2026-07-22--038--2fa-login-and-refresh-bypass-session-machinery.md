# 2FA login (TOTP/passkey) and token refresh bypass session tracking / token-version

**Status:** `done`
**Created:** 2026-07-22
**Severity:** High
**Module:** `auth` / `two_factor` (backend)
**Source:** User report — TOTP login rejected, and passkey login logs the user back out shortly after a successful login on navigation.

## Problem

Same class of bug as [#036](2026-07-21--036--oauth-login-bypasses-session-machinery.md), found in two more places that were never fixed alongside it:

1. `TwoFactorService.verify_totp_login` and `TwoFactorService.complete_passkey_authentication` ([`service.py`](../../backend/app/modules/two_factor/service.py)) minted tokens via the low-level `create_access_token`/`create_refresh_token` builders directly, instead of `AuthService._issue_login_tokens`. Tokens carried `tfaVerified=True` (fixed previously) but no `tv` (token version) or `jti`.
2. `AuthService.refresh_access_token` ([`service.py:177`](../../backend/app/modules/auth/service.py)) had the identical gap — it preserved `tfaVerified`/`tfaMethod` from the old refresh token but never re-added `tv`/`jti` to the newly minted tokens, even for sessions that started out with them (password/OAuth login).

## Impact

`_verify_user_token`'s check `payload.get("tv", 0) != user.tokenVersion` ([`dependencies.py:128`](../../backend/app/modules/auth/dependencies.py)) rejects any token missing `tv` with 401 "Token has been revoked", for every user whose `tokenVersion` isn't `0` (i.e. anyone who ever went through a password reset/change, or any future "log out everywhere" action):

- TOTP/passkey verification returns 200 (code accepted) but the very next authenticated request 401s — looked like "TOTP doesn't work" / "logged in, then instantly logged out."
- Because the frontend's axios error interceptor retries once through `POST /auth/refresh` on a 401, and `refresh_access_token` had the same gap, the retry also failed — surfacing as "unauthorized" on the next page navigation even for sessions that logged in successfully via password/OAuth, once their access token needed a refresh.

## Fix

- `TwoFactorService` now accepts `user_repository`/`token_blacklist_service` and both login-completion methods delegate to a new `_issue_login_tokens` helper that calls `AuthService._issue_login_tokens` (same helper password/OAuth login use) — full `tv`/`jti`/`email`/`emailVerified` claims + Redis session tracking.
- `AuthService.refresh_access_token` now calls `self._issue_login_tokens(user, tfa_verified=..., tfa_method=...)` instead of building tokens by hand, so refreshed tokens always carry a fresh `tv`/`jti`.
- `two_factor/router.py`'s `get_service` dependency now injects `user_repo`/`blacklist_service` into `TwoFactorService`.

## Scope

- [x] `backend/app/modules/two_factor/service.py` — `verify_totp_login` / `complete_passkey_authentication` reuse `_issue_login_tokens`
- [x] `backend/app/modules/two_factor/router.py` — `get_service` wires `user_repository`/`token_blacklist_service`
- [x] `backend/app/modules/auth/service.py` — `refresh_access_token` reuses `_issue_login_tokens`
- [x] Tests: `backend/tests/test_two_factor_login.py` (tv/jti present, `tokenVersion=3` fixture) and `backend/tests/test_auth_service.py::test_refresh_access_token_preserves_tv_and_jti`

## Verification

All 30 tests in `test_two_factor_login.py` / `test_auth_service.py` / `test_oauth_2fa_login.py` pass. Live end-to-end TOTP + passkey login (with a `tokenVersion > 0` account) not re-tested against a running deployment this session — recommended before closing as fully verified in production.
