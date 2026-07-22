# OAuth callback does not verify the CSRF `state` server-side

**Status:** `verification needed`
**Created:** 2026-07-21
**Severity:** Medium
**Module:** `auth` / `core.oauth` (backend — OAuth)
**Source:** [Security review — Backend](../reviews/2026-07-06-security-backend.md) (SEC-BE-03)
**Related:** open GitHub security alert — OAuth CSRF `state` stored in `localStorage` (frontend side)

## Problem

The OAuth flow generates a `state` parameter server-side (`OAuthService.generate_state` → `secrets.token_urlsafe`, [`core/oauth.py:340`](../../backend/app/core/oauth.py)) and returns it to the client from `POST /api/auth/oauth/auth-url` ([`router.py:585`](../../backend/app/modules/auth/router.py)).

But the callback handler `oauth_callback` ([`router.py:609`](../../backend/app/modules/auth/router.py)) **never verifies `state`**. It takes `OAuthCallbackRequest.code`, exchanges it, and logs the user in. The `state` value is only compared on the frontend (where it is kept in `localStorage`). The backend keeps no record of the issued `state` and does not bind it to the caller's session, so the server-side leg of the OAuth CSRF defense is missing.

## Impact

OAuth login is a classic CSRF target: without a server-verified, session-bound `state`, an attacker can attempt login-CSRF / account-linking attacks (e.g. tricking a victim's browser into completing an OAuth callback with an attacker-controlled `code`, linking the attacker's provider identity — see `login_with_oauth` account-linking-by-email at [`service.py:600`](../../backend/app/modules/auth/service.py)). The frontend-only check is bypassable by anything that can reach the callback endpoint directly, and the `localStorage` storage is itself flagged by the open Dependabot/GitHub alert.

## Proposed fix

- Persist the issued `state` server-side with a short TTL, bound to the browser session (e.g. Redis, keyed to a session/anti-CSRF cookie or the `state` value itself), when `auth-url` is requested.
- In `oauth_callback`, require `state`, look it up, verify it is unused and unexpired, and delete it (single-use) before exchanging the code. Reject on mismatch.
- Frontend: move `state` out of `localStorage` into session-scoped storage (tracked by the existing alert).

Reuse the existing challenge-store pattern (`app/modules/two_factor/challenge_store.py` / `app/core/redis.py`) rather than inventing new storage.

## Scope

- [x] `backend/app/core/oauth_state_store.py` (new) — Redis-backed, single-use, TTL'd `state` store, keyed by the state value and bound to the provider
- [x] `backend/app/modules/auth/router.py` — `get_oauth_auth_url` persists `state`; `oauth_callback` requires and consumes it (400 on missing/expired/reused/mismatched)
- [x] `backend/app/modules/auth/schemas.py` — `state` was already required on `OAuthCallbackRequest`; no change needed
- [x] Frontend — already using `sessionStorage` (not `localStorage`) for `state`, done in a prior session; no further change needed here
- [x] Test: callback with missing/forged/reused `state` → 400 (`backend/tests/test_oauth_state_store.py`)

## Resolution (2026-07-22)

Added `OAuthStateStore` (`backend/app/core/oauth_state_store.py`), modeled on the existing `WebAuthnChallengeStore` pattern (`two_factor/challenge_store.py`): Redis key per state value, 10-minute TTL, atomic get+delete via a pipeline for single-use semantics, value also carries the `provider` it was issued for so a state minted for one provider can't be replayed against another.

`POST /oauth/auth-url` now stores the state it hands back to the client; `POST /oauth/callback/{provider}` requires it, calls `consume_state(state, provider)`, and returns 400 immediately (before exchanging the code) if it's missing, expired, already used, or was issued for a different provider.

The frontend half (moving `state` out of `localStorage`) was already done in an earlier session — `useOAuth.ts`/`OAuthCallbackPage.vue` use `sessionStorage`. This closes the remaining backend-verification gap the earlier fix explicitly called out as incomplete.

Tests cover all three "Verification" scenarios below directly against `OAuthStateStore` (no live Redis in this environment; used an in-memory fake matching the real `redis.asyncio` pipeline contract). Marked `verification needed` pending a manual click-through of the real `/oauth/auth-url` → `/oauth/callback` round trip.

## Verification

1. Complete a normal OAuth login → success. — covered by `test_normal_login_state_is_valid`.
2. Replay the same `state` twice → second attempt rejected (single-use). — covered by `test_replayed_state_is_rejected`.
3. Callback with a `state` the server never issued → rejected. — covered by `test_never_issued_state_is_rejected`.
