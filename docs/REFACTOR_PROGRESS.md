# Refactor Progress

Tracking implementation of [REVIEW_AND_REFACTOR_PLAN.md](REVIEW_AND_REFACTOR_PLAN.md).

> Started: 2026-07-03

## Scope of this pass

Focus on the **concrete, safe, verifiable backend items** from Phase 0, Phase 1,
Phase 3 (DRY), and the Quick-wins checklist. The large multi-week efforts
(refresh-token-to-cookie, god-file splits, V1→V2 completion, package extraction)
are **out of scope** for this pass and remain tracked in the plan.

## Status legend
- ✅ done
- 🚧 in progress
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
- ⏭️ Move refresh token to HttpOnly cookie (§3.1) — deferred (frontend+backend, large)

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
</content>
</invoke>
