# Refactor Progress

Tracking implementation of [REVIEW_AND_REFACTOR_PLAN.md](REVIEW_AND_REFACTOR_PLAN.md).

> Started: 2026-07-03

## Scope of this pass

Focus on the **concrete, safe, verifiable backend items** from Phase 0, Phase 1,
Phase 3 (DRY), and the Quick-wins checklist. The large multi-week efforts
(god-file splits, V1→V2 completion, package extraction) are **out of scope**
for the previous pass and remain tracked in the plan.

**Deferred for later:**
- ⏭️ Split gear **god files** (§4.1) — `service.py` / `repository.py` / `router.py` too large; strangler split by subdomain

## Status legend
- ✅ done
- 🚧 in progress
- 🔜 next (queued to start)
- ⏭️ deferred (too large / out of scope this pass)

## Phase 0 — Guardrails
- ✅ `settings.validate_production()` + call on startup (§3.4, §3.5)
      — `config.py`: asserts `DEBUG=false`, non-empty non-`*` `ALLOWED_HOSTS`
      and `CORS_ORIGINS`; called from `app_factory.lifespan` (no-op outside prod).
- ✅ Remove `script-src 'unsafe-inline'` from CSP (§3.2) — `security_headers.py`;
      kept on `style-src` (Vue/shadcn inline styles).
- ✅ Document shared-core "mirror changes" rule (§7) — already in plan/CLAUDE.md;
      see Shared-core note below for files touched this pass.

## Phase 1 — Security hardening
- ✅ Add `iss`/`aud` to JWTs and verify (§3.3) — `auth_utils.py` stamps
      `iss`/`aud` from new `SECURITY.jwt_issuer`/`jwt_audience` settings and
      `verify_token` verifies them. `verify_token(expected_type=...)` lets flows
      assert token purpose at decode time.
- ✅ Extract `is_expected_error()` shared by both Sentry paths (§3.6) —
      `app_factory.py`: `is_expected_auth_error` / `is_expected_image_error` /
      `is_expected_error`, used by both `before_send` and the global handler.
- ✅ Move refresh token to HttpOnly cookie (§3.1, 2026-07-24) — frontend+backend.
      Backend: `auth/cookies.py` sets/clears an httpOnly+secure+samesite=strict
      `refresh_token` cookie scoped to `path=/api/auth` from login/oauth/2FA-verify/
      refresh; `/auth/refresh` reads the cookie instead of a body; `refreshToken`
      dropped from all JSON responses (`response_model_exclude`); logout clears the
      cookie, and `refresh_access_token` now checks the JTI blacklist so a revoked
      session's refresh token stops working immediately (previously logout only
      blacklisted the access token — closed gap). Frontend: access token is
      in-memory only in `useAuthStore` (no localStorage); `apiClient` sends
      `withCredentials: true`; `error.interceptor.ts` always attempts refresh on
      401 (can no longer see whether the cookie exists); new
      `useAuthBootstrap.ts` does a silent refresh restoring the session after a
      hard reload — memoized and awaited inside `authGuard` itself (awaiting it
      only before `app.mount()` is not sufficient, since Vue Router's initial
      navigation guards run as soon as `app.use(router)` is called, independent
      of mount). Verified end-to-end via curl against the real backend and a
      Playwright-driven browser session (login/reload/protected-route/logout).

## Phase 3 — DRY extractions
- ✅ Extract shared JWT `_encode_token(claims, *, token_type, expires_delta)` (§5)
      — all four `create_*_token` builders now delegate to it.
- ✅ Extract shared bool-parsing validator (§5) — `helpers.parse_bool_value`;
      the four duplicated `parse_enabled`/`parse_bool_field` validators now call it.
- ⏭️ Split gear god files (§4.1) — deferred (large, strangler)

## Quick wins (§9)
- ✅ Hoist `import logging` to module scope in `app_factory.py` (+ `dependencies.py`)
- ✅ Delete commented-out DB-init block in `lifespan`
- ✅ Drop per-request `INFO` auth-service log to `DEBUG`
- ✅ Narrow `except (ImportError, Exception)` to `except ImportError`
- ✅ Replace `Union[AuthService, Any]` return with `AuthService`
      (`AuthServiceWith2FA` is a subclass — no separate Protocol needed)

## Verification
- `black`: all changed files formatted.
- `mypy`: no new errors in changed files (pre-existing errors in
  `service.py` jti/tv, `image_upload_service.py`, `billing`, `s3_adapter`,
  `token_blacklist` remain, untouched).
- `pytest tests/ -k "auth or token or jwt or config or security"`: **58 passed**.
- Full suite: 248 passed, 7 pre-existing failures (billing mocks, empty-strings
  middleware JSON handling, `test_main` sqlalchemy CompileError) — all in modules
  untouched by this pass, confirmed unrelated.
- Smoke tests: token round-trip carries/verifies `iss`+`aud`; `verify_token`
  rejects wrong `expected_type`; `validate_production()` raises on insecure prod
  config and is a no-op otherwise; app imports clean.

## Behavioural note (deploy)
Adding+verifying `iss`/`aud` means JWTs minted **before** this change (which lack
those claims) are rejected on decode → users re-login once after deploy. New
tokens are unaffected. 2FA-flow tokens (`2fa_verification`, `2fa_setup`,
`passkey_registration`) intentionally keep their own encode/decode without
`iss`/`aud` and are unchanged.

## Shared-core note (mirror to ops-monitor — §7)
These changed files are part of the shared core and should be mirrored:
`app/core/config.py`, `app/core/helpers.py`, `app/core/security_headers.py`,
`app/core/app_factory.py`. Brand/domain-specific defaults are already in config
(`jwt_issuer`/`jwt_audience` default `"gear-stack"` — set per-repo via env).

**2026-07-24 addendum (§3.1 pass):** `src/shared/services/apiClient.ts`,
`auth.interceptor.ts`, and `error.interceptor.ts` are also shared-core
(`src/shared/*`) and were changed for the HttpOnly-cookie migration —
**not yet mirrored to ops-monitor**, tracked as a follow-up. `backend/app/modules/auth/*`
and `backend/app/modules/two_factor/*` are app-specific modules, not shared-core,
so no mirroring needed there.

## Verification (2026-07-24 — §3.1 pass)
- `pytest tests/ -k "auth or refresh or token or logout or two_factor"`: 96 passed
  (15 pre-existing errors elsewhere are PostgreSQL test-DB connectivity issues in
  unrelated `integration/gear/*` tests).
- Full backend suite: same 7 pre-existing failures/5 errors as the baseline above
  (billing mocks, empty-strings middleware, `test_main` CompileError, `admin_stats_v2`
  DB connectivity) — no new regressions.
- `black` / `mypy`: no new errors in changed files.
- `pnpm type-check` / `pnpm lint`: clean.
- End-to-end smoke test against the real running stack (not mocks):
  - `curl` against the live backend: login sets `Set-Cookie: refresh_token=...;
    HttpOnly; Secure; SameSite=strict; Path=/api/auth`, body has no `refreshToken`;
    `/auth/refresh` rotates the cookie and 401s without one; `/auth/logout` clears
    the cookie and revokes the shared session `jti`, so the pre-logout refresh
    token immediately stops working (`"Session has been revoked"`).
  - Playwright-driven headless Chromium against `pnpm dev`: after login,
    `localStorage` has no access/refresh-token keys and the `refresh_token` cookie
    is httpOnly; a hard reload silently restores the session (confirmed by
    successfully navigating to a `requiresAuth`-gated route, not just URL
    inspection); logout clears the cookie.
  - Caught and fixed a real bug this way: gating `app.mount()` on the bootstrap
    promise doesn't work, because Vue Router's initial navigation guards fire as
    soon as `app.use(router)` runs, independent of `.mount()` — the fix moved the
    `await` into `authGuard` itself (memoized promise, no duplicate network call).
</content>
</invoke>
