# Security review — Backend

**Status:** `done`
**Scope:** FastAPI backend (`backend/app/`)
**Run:** One dedicated AI session — 2026-07-21 (Claude Fable), per [prompt](2026-07-21--fable-security-backend-prompt.md)

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md §3](../plans/REVIEW_AND_REFACTOR_PLAN.md#3-security-review)
- [plans/SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md)
- [security-dependabot-remediation.md](../plans/security-dependabot-remediation.md)
- Shared core drift: `backend/app/core/`, `backend/app/common/` vs ops-monitor

## Executive summary

**Overall posture: STRONG.** The auth/session core is well built and the recently landed hardening holds up under tracing: WebAuthn login does full cryptographic verification bound to the user, TOTP/passkey login tokens carry `tfaVerified`, the admin **and** users routers share one `enforce_user_mutation_permissions` guard, JWTs verify `iss`/`aud` with a Redis JTI blacklist + DB `token_version` fallback, the rate limiter trusts only the last XFF hop, CSP no longer ships `'unsafe-inline'` in `script-src`, `validate_production()` fails fast on insecure prod config, the health-details token uses `secrets.compare_digest` and fails closed, the Stripe webhook verifies its signature, and image upload validates MIME by magic number with an SSRF host/IP blocklist. Gear ownership is consistently enforced at the repository layer (`WHERE user_id = ...`).

**Top 3 risks:**
1. **(High) Item-image IDOR** — the per-user item-image endpoints check a *role* (`PremiumOrHigherUser`) but never that the item/image belongs to the caller; one read endpoint has no auth at all. Any premium user can read/modify/delete other users' item images; anyone can read item images unauthenticated. → issue 035.
2. **(Medium) OAuth login bypasses the session machinery** — `login_with_oauth` mints tokens via the low-level builders instead of `_issue_login_tokens`, omitting `jti`/`tv`/`tfaVerified` and Redis session tracking, so global revocation and 2FA are inconsistent (and OAuth login breaks once `tokenVersion` is bumped). → issue 036.
3. **(Medium) OAuth callback never verifies `state`** — CSRF `state` is generated server-side but validated only on the frontend (in `localStorage`); the backend does not store or check it. → issue 037.

The two OAuth items are lower-probability today (providers unconfigured by default) but GitHub OAuth is actively being enabled (issue 014), so they should land before that goes live.

## Findings

| ID | Severity | Location | Finding | Recommendation |
|----|----------|----------|---------|----------------|
| SEC-BE-01 | **High** | `modules/gear/item_image_router.py`, `image_upload_service.py` (`delete_image`, `reorder_images`, `toggle_primary_image`, `upload_image`, `get_item_images`), `item_image_repository.py` | Broken object-level authorization (IDOR): endpoints gate on the `PremiumOrHigherUser` *role* but never verify the target item/image belongs to the caller; repository queries key on `item_id`/`image_id` with no owner join. `delete_image`'s `user_id` arg is documented "for authorization" but unused. `GET /items/{item_id}/images` has **no auth dependency**. | Enforce owner scoping in the repository (`WHERE user_id = :user_id`) / service; return 404 on mismatch; add auth to the read endpoint (or scope to public containers). → **issue 035** |
| SEC-BE-02 | **Medium** | `modules/auth/service.py:550` `login_with_oauth` | OAuth mints tokens via `create_access_token`/`create_refresh_token` directly (no `jti`/`tv`/`emailVerified`/2FA, no `track_user_session`), unlike `_issue_login_tokens`. Revocation ("logout all", password-change) misses OAuth sessions; `tv` defaults to 0 so OAuth login breaks after any `tokenVersion` bump; 2FA enforcement inconsistent. | Route OAuth through `_issue_login_tokens`; define the OAuth 2FA policy. → **issue 036** |
| SEC-BE-03 | **Medium** | `modules/auth/router.py:609` `oauth_callback`, `core/oauth.py` | OAuth CSRF `state` is generated server-side but never verified server-side — only the frontend compares it (stored in `localStorage`). Backend keeps no record of issued state. | Persist state (short TTL, session-bound, single-use) and verify+consume it in the callback. → **issue 037** |
| SEC-BE-04 | Low | `modules/auth/dependencies.py:187-190` | The 2FA-enabled verification block is wrapped in a broad `except Exception` that logs and **proceeds** ("might want to be more strict"). A transient error in `has_two_factor_enabled` fails **open** — the request is served without enforcing `tfaVerified` for that call. | Fail closed (deny) on unexpected errors in the 2FA check, at least in production. |
| SEC-BE-05 | Low | `modules/gear/image_upload_service.py:86` `_validate_url_for_ssrf` | SSRF validation resolves the hostname, then `httpx` re-resolves at fetch time (check-then-fetch / DNS-rebinding gap). Mitigated by `httpx` not following redirects by default and a 15s timeout, but a rebinding host could still be reached. | Resolve once and connect to the validated IP (pin), or re-validate the socket peer address; keep redirects disabled. |
| SEC-BE-06 | Low | `modules/auth/service.py` `reset_password` / `verify_email` | `verify_token(token)` is called without the available `expected_type` argument; token-purpose separation currently relies on the DB-stored token matching. Defense-in-depth gap if that storage path ever changes. | Pass `expected_type="password_reset"` / `"email_verification"` to `verify_token` in these flows. |
| SEC-BE-07 | Info | `modules/ai/dependencies.py`, `modules/ai/routers/*` | `AdminUser` alias actually resolves to `require_ai_access` (premium-or-own-token) and several endpoints are documented "admin only" though they are premium-accessible. No live vuln (AI history is user-scoped via `current_user.id`), but the naming invites future authz mistakes. | Rename the alias (e.g. `AiAccessUser`) and correct the docstrings. |
| SEC-BE-08 | Info | `modules/auth/router.py:158`, `service.py` | Login logs the email and auth-service type at INFO on every attempt; password-reset token is logged only in `development`. Acceptable, but the INFO email logging is avoidable PII in prod logs. | Drop email from the INFO login log (or lower to DEBUG). |

### Verified still-correct (re-checked, not re-opened)

WebAuthn login = full `verify_authentication` (signature/challenge/origin/RP-ID/counter) bound to the challenge's user (`webauthn_service.complete_authentication`); `tfaVerified` enforced on privileged routes and set on login tokens; `tfaPending` tokens rejected by `_verify_user_token`; admin + users owner-mutation guard shared via `enforce_user_mutation_permissions`; rate limiter last-hop XFF trust; JWT `iss`/`aud` verified + JTI blacklist + `token_version`; CSP `script-src` without `'unsafe-inline'`; `validate_production()` wired in `lifespan`; docs/redoc/openapi disabled outside development; prod error handler hides stack traces; health-details token `compare_digest` + fail-closed; Stripe webhook signature verification; gear container/item ownership filtering; SSRF host/IP blocklist; MIME magic-number validation and per-role upload size limits.

## Checklist

- [x] JWT: `type` claim, blacklist, refresh rotation, `iss`/`aud`, per-purpose keys — verified; single shared key separated by `type`+`iss`/`aud` (per-purpose keys not implemented, acceptable — see SEC-BE-06 for the decode-time `expected_type` gap). Refresh issues new access **and** refresh tokens (rotation present); old refresh token is not blacklisted on rotation (noted, low risk given `token_version`).
- [x] Auth dependencies: `CurrentUser`, `AdminUser`, 2FA-pending rejection — verified; see SEC-BE-04 for the fail-open edge.
- [x] CSP and security headers (`app/core/security_headers.py`) — verified; `'unsafe-inline'` removed from `script-src`, HSTS prod-only.
- [x] CORS, `TrustedHost`, rate limiting, reCAPTCHA — verified; TrustedHost prod-only, `validate_production()` rejects `*` origins, reCAPTCHA verifies action+score, limiter trusts last XFF hop.
- [x] Input validation (Pydantic), SQL injection surfaces, mass-assignment — verified; only one `text()` query, parameterized via `bindparams`; admin/user updates constrained by the mutation guard.
- [x] Authorization on all gear/admin/AI endpoints (IDOR, ownership) — gear + admin + AI verified clean; **item images fail (SEC-BE-01)**.
- [x] File upload: mime validation, path traversal, size limits, S3/local adapters — MIME by magic number, per-role size caps, storage keys are server-generated UUID paths (no user-controlled path). Local/S3 adapters not read line-by-line (budget) — no traversal surface observed via the router; see "not reviewed".
- [x] Secrets: `SECRET_KEY` strength, production startup assertions, `.env` handling — verified; strength validator + `validate_production()`.
- [x] Error responses: no stack traces / secrets in production — verified in `app_factory.register_exception_handlers`.
- [~] Shared-core files that differ from ops-monitor — **not compared this run** (out of scope: "affects core family" noted). SEC-BE-01/02/03 touch auth + gear which are partly shared core; flag for backport review if fixed here.

### Not reviewed / out of budget

- Storage adapters line-by-line (`core/storage/local_adapter.py`, `s3_adapter.py`, `image_processor.py`) — only their use from the upload service was traced.
- `modules/logs`, `modules/stats`, `modules/tenants`, `modules/gear_settings`, `modules/settings` routers beyond confirming they require `CurrentUser`.
- `two_factor` TOTP secret/backup-code crypto internals (`crypto_utils`, `totp_service`) — only the login/verify flow and rate limiting were checked.
- AI token Fernet encryption internals (`ai/utils/encryption.py`).
- Shared-core drift vs ops-monitor (explicitly out of scope for this run).

## Follow-ups

- [035 — Item image IDOR](../issues/2026-07-21--035--item-image-idor.md) (High)
- [036 — OAuth login bypasses session machinery](../issues/2026-07-21--036--oauth-login-bypasses-session-machinery.md) (Medium)
- [037 — OAuth callback state not verified](../issues/2026-07-21--037--oauth-callback-state-not-verified.md) (Medium)
- SEC-BE-04/05/06 (Low) and SEC-BE-07/08 (Info) are recorded above; fold into a hardening pass rather than separate issues.
