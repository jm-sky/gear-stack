# Gear Stack — Code Review & Refactor Plan

> Review date: 2026-07-03
> Scope: architecture, best practices, security, SOLID/DRY across FastAPI backend and Vue 3 frontend.
> Related: shared "core" is also used by **ops-monitor** — see [ops-monitor `docs/SHARED_CORE.md`](../../ops-monitor/docs/SHARED_CORE.md) and the [Shared Core](#7-shared-core-with-ops-monitor) section below.

## 1. Executive summary

Gear Stack is a well-structured, feature-rich Vue 3 + FastAPI application. The
architecture is deliberate: modular backend (`app/modules/*`), modular frontend
(`src/modules/*`), adapter patterns for email/storage, a repository layer with
interfaces, Pydantic-settings config, and a real security posture (JWT type
enforcement, token blacklist, security headers, rate limiting, reCAPTCHA, secret
strength validation).

The main risks are **not** missing features — they are **accumulated size and
duplication**:

1. **A copied "core" that has drifted** between `gear-stack` and `ops-monitor`.
   Security-relevant files (`config.py`, `security_headers.py`, storage adapters,
   `migrations.py`) differ between the two repos, so a fix in one is not
   guaranteed to reach the other.
2. **God files** in the gear module (`service.py` 88 KB, `repository.py` 51 KB,
   `router.py` 49 KB) that violate SRP and are hard to test/maintain.
3. **Frontend V1/V2 gear duplication** — two parallel data layers running at once.
4. **Auth tokens in `localStorage`** combined with a CSP that allows
   `script-src 'unsafe-inline'` — an XSS-hardening gap.
5. **Thin automated test coverage** relative to code volume.

None of these are emergencies. The plan in [section 8](#8-prioritized-refactor-plan)
sequences them by risk/effort.

### Severity legend
- 🔴 **High** — security or correctness risk, or a multiplier of future bugs.
- 🟡 **Medium** — maintainability / SOLID / DRY debt that slows the team.
- 🟢 **Low** — polish, consistency, nice-to-have.

---

## 2. What's already good (keep doing this)

- **Modular boundaries** on both ends (`app/modules/*`, `src/modules/*`) with
  per-module routes, schemas, services, repositories, i18n.
- **Repository pattern with interfaces** (`types/repository.py`) — enables
  testing and swapping persistence.
- **Adapter/factory patterns** for email (`file`/`smtp`/`audit`/`retry`) and
  storage (`local`/`s3`) — textbook OCP/DIP.
- **Config as typed Pydantic settings**, grouped by concern, validated
  (port range, JWT secret strength, score ranges, mime types).
- **Security baseline is present**: JWT `type` claim is enforced at the auth
  dependency (`_verify_user_token`), token blacklist on logout/delete, 2FA-pending
  rejection, security-headers middleware, `TrustedHost` in production, rate limits
  per auth action, `send_default_pii=False` in Sentry, secret-key default rejected.
- **`.env` is git-ignored and not tracked**; `.env.example` documents required vars.
- **Docs discipline**: `CLAUDE.md`, `BUGS.md`, migration docs, security remediation
  doc — this is unusually good and worth preserving.

---

## 3. Security review

### 3.1 🔴 Auth tokens stored in `localStorage`
`src/modules/auth/store/useAuthStore.ts` and `src/shared/services/auth.interceptor.ts`
keep the access token, refresh token, and 2FA token in `localStorage`. Any XSS
gives an attacker all three. This is a deliberate SPA trade-off, but it is the
single highest-leverage hardening target.

**Options (in order of strength):**
- Move refresh token to an **HttpOnly, Secure, SameSite=Strict cookie** issued by
  the backend; keep only the short-lived access token in memory (not `localStorage`).
- If cookies are infeasible, at minimum keep the access token **in memory only**
  and reduce its lifetime (already 30 min — good), relying on refresh.
- Pair with the CSP tightening below.

### 3.2 🔴 CSP allows `script-src 'unsafe-inline'`
`app/core/security_headers.py` sets
`script-src 'self' 'unsafe-inline' blob: ...`. `'unsafe-inline'` largely defeats
CSP's XSS protection. reCAPTCHA/Sentry do not require inline **script**; they need
allow-listed hosts (already present).

**Fix:** remove `'unsafe-inline'` from `script-src` (keep it on `style-src` only if
Vue/shadcn truly needs it), and validate the app still boots. If inline bootstrap
scripts are needed, move to nonce/hash-based CSP.

### 3.3 🟡 JWT has no `iss`/`aud` and relies on shared `secret_key` for all token types
`auth_utils.verify_token` decodes with `algorithms=[HS256]` but does not verify
issuer/audience. All token types (`access`, `refresh`, `password_reset`,
`email_verification`) are signed with the same key and separated only by a `type`
claim checked downstream. This works, but:
- Add `iss`/`aud` claims and verify them, so a token minted for one deployment
  can't be replayed against another sharing the key family.
- Consider per-purpose signing keys (or at least assert `type` inside
  `verify_token` for reset/verification flows, not only in the access dependency).

### 3.4 🟡 CORS defaults are permissive if misconfigured
`cors_methods` and `cors_headers` default to `["*"]` with `cors_credentials=True`.
Browsers reject `*` + credentials, but a future `CORS_ORIGINS` wildcard would be a
real hole. Document that `CORS_ORIGINS` must be an explicit allow-list in
production and add a startup assertion that rejects `*` origins when
`is_production()`.

### 3.5 🟢 Verify production env invariants at startup
`SECRET_KEY` strength is validated, but `DEBUG`, `docs_url` exposure, `ALLOWED_HOSTS`
non-empty, and `CORS_ORIGINS` non-wildcard are not asserted for production. Add a
single `settings.validate_production()` called on startup when `is_production()`.

### 3.6 🟢 Sentry error-filter logic is duplicated
`app_factory.init_sentry.before_send` and `general_exception_handler` re-implement
the same "is this an expected auth/image error" logic twice. Duplicated security/
observability logic drifts. Extract one `is_expected_error(exc)` helper.

---

## 4. SOLID / architecture

### 4.1 🔴 God files in the gear module (SRP)
| File | Size |
|------|------|
| `app/modules/gear/service.py` | ~88 KB |
| `app/modules/gear/repository.py` | ~51 KB |
| `app/modules/gear/router.py` | ~49 KB |
| `app/modules/gear/image_upload_service.py` | ~30 KB |

A single 88 KB service class almost certainly mixes containers, items,
categories, weight calculation, import/export, and catalogue promotion. This is
the biggest maintainability liability.

**Refactor:** split by sub-domain into cohesive services
(`ContainerService`, `ItemService`, `CategoryService`, `WeightCalculator`,
`ImportExportService`, `CataloguePromotionService`) behind the existing router.
Do the same slicing for the repository and router. Keep public method signatures
stable and migrate incrementally (strangler pattern).

### 4.2 🟡 `get_auth_service` has environment branching and inline imports
`app/modules/auth/dependencies.py` toggles a 2FA-enabled service via a module-level
`HAS_2FA` try/except and `Depends(lambda: None)`. It also logs at `INFO` on every
request (`"Created auth service..."`). This couples wiring, logging, and feature
detection.

**Fix:** resolve 2FA availability once at composition time (a provider function
registered in the app factory), drop per-request `INFO` logs to `DEBUG`, and avoid
`except (ImportError, Exception)` (that catches everything — mask nothing broader
than `ImportError`).

### 4.3 🟡 Global settings singleton
`settings = get_settings()` at import time (module global) plus `@lru_cache` makes
config a hidden global dependency, complicating tests and per-request overrides.
Prefer injecting `Settings` via FastAPI `Depends(get_settings)` in new code; keep
the global only for legacy call sites during migration.

### 4.4 🟢 `Union[AuthService, Any]` return types
The 2FA branch returns `Any`, erasing type safety across the auth layer. Define a
shared `AuthServiceProtocol` both implementations satisfy and type against it.

---

## 5. DRY / best practices

- 🟡 **Repeated boolean parsing** — `parse_enabled` / `parse_bool_field` is copy-
  pasted across `RecaptchaSettings`, `SentrySettings`, `AISettings`, `StripeSettings`,
  etc. Extract one reusable validator (e.g. a `BoolFromStr` annotated type or a
  shared `_parse_bool` function) and apply it once.
- 🟡 **Repeated JWT builders** — `create_access_token`, `create_refresh_token`,
  `create_password_reset_token`, `create_email_verification_token` all rebuild the
  same encode/exp/iat boilerplate. Extract a private `_encode(payload, ttl, type)`.
- 🟢 **Inline `import logging` inside functions** across `app_factory.py` — hoist to
  module level; it's both cleaner and marginally faster.
- 🟢 **Commented-out code** in `lifespan` (DB auto-init block) — delete or move to
  docs; commented code rots.

---

## 6. Frontend review

- 🔴 **V1/V2 gear duplication** — per `CLAUDE.md`, `useGear` (V1) and `useGearV2`
  run in parallel, and mutations must manually invalidate the V2 query cache or the
  UI shows stale data. This is a recurring bug source (`BUGS.md`). Finish the
  V1→V2 migration (`docs/migration-v1-to-v2.md`) and delete the V1 layer; the dual
  model is the frontend's biggest structural debt.
- 🟡 **Token handling** — see 3.1. Centralize token read/write in the auth store so
  the storage backend can be swapped in one place.
- 🟢 **Test coverage** — 26 unit test files against ~723 `.ts/.vue` files. Prioritize
  tests for services (business logic) and the auth/token-refresh flow.
- 🟢 **Consistency conventions are strong** (ESLint perfectionist, action-icon
  registry, Vue 3.5 `defineModel`) — keep enforcing in CI.

---

## 7. Shared core with ops-monitor

`gear-stack` and `ops-monitor` are built on the **same core skeleton**, copied
rather than shared as a package. Confirmed shared areas:

**Backend**
- `backend/app/core/*` — config, middleware, security headers, auth/token
  blacklist, email (adapters + service + i18n + audit), storage (local/s3 +
  processor), redis, limiter, recaptcha, oauth, logging, migrations runner.
- `backend/app/common/*` — pagination, search, id/repository utils, email audit
  repository & model.
- `backend/cli/*` — Django-style CLI (`db`, `users`, `test` command groups).
- The **migration runner + `schema_migrations`** convention.

**Frontend**
- `src/shared/*` — apiClient, auth/error interceptors, sentry, i18n infra,
  token-refresh store, shared types/utils/config.
- `src/components/ui/*` — the shadcn-vue component set.
- Build/tooling: `eslint.config.ts`, `pwa.config.ts`, `vite.config.ts`,
  `tsconfig*`, `playwright.config.ts`.

### 🔴 The core has already drifted
A `diff -rq` of the two `backend/app/core` trees shows these files **differ**:
`app_factory.py`, `auth/token_blacklist.py`, `config.py`,
`convert_empty_strings_middleware.py`, `email/audit_adapter.py`, `email/service.py`,
`migrations.py`, `security_headers.py`, `static.py`, `storage/local_adapter.py`,
`storage/s3_adapter.py`; plus `common/pagination.py` and
`common/repositories/email_audit_repository.py`.

Some drift is legitimate (CSP `connect-src` domain, WebAuthn RP name, branding).
Some is **accidental divergence of security-sensitive code** — exactly the class of
duplication that lets a fix land in one repo and silently miss the other.

**Recommendation** (details in `ops-monitor/docs/SHARED_CORE.md`):
1. **Short term** — treat these paths as "shared, do not fork casually"; any change
   to a shared-core file must be mirrored to the sibling repo in the same PR, and
   domain/brand-specific values must move to **config/env**, not code.
2. **Medium term** — extract the stable core into a versioned internal package
   (`pip`-installable backend core + a private npm package for `src/shared` + `ui`),
   consumed by both apps. This turns "remember to copy" into "bump a version".

---

## 8. Prioritized refactor plan

### Phase 0 — Guardrails (days)
- [ ] Add `settings.validate_production()` (assert non-default secret, no `*` CORS,
      non-empty `ALLOWED_HOSTS`, `DEBUG=false`) called on startup. *(§3.4, §3.5)*
- [ ] Remove `script-src 'unsafe-inline'` from CSP and verify boot. *(§3.2)*
- [ ] Document shared-core paths + "mirror changes" rule in both repos. *(§7)*

### Phase 1 — Security hardening (1–2 weeks)
- [ ] Move refresh token to HttpOnly cookie; access token in memory. *(§3.1)*
- [ ] Add `iss`/`aud` to JWTs and verify; assert `type` in reset/verify flows. *(§3.3)*
- [ ] Extract `is_expected_error()` used by both Sentry filter paths. *(§3.6)*

### Phase 2 — De-duplicate the shared core (2–4 weeks)
- [ ] Reconcile the drifted core files; move brand/domain values to config. *(§7)*
- [ ] Extract backend `app/core` + `app/common` into an internal package.
- [ ] Extract `src/shared` + `src/components/ui` into a private npm package.

### Phase 3 — Break up the god files (ongoing, strangler)
- [ ] Split `gear/service.py` into cohesive services. *(§4.1)*
- [ ] Split `gear/repository.py` and `gear/router.py` by sub-domain. *(§4.1)*
- [ ] Extract shared JWT `_encode` and the bool-parsing validator. *(§5)*

### Phase 4 — Finish V1→V2 & raise test floor (ongoing)
- [ ] Complete V1→V2 gear migration; delete V1. *(§6)*
- [ ] Add service-layer + auth-flow tests; wire coverage threshold into CI. *(§4, §6)*

---

## 9. Quick wins checklist (low effort, do anytime)
- [ ] Hoist `import logging` to module scope in `app_factory.py`. *(§5)*
- [ ] Delete commented-out DB-init block in `lifespan`. *(§5)*
- [ ] Drop per-request `INFO` auth-service log to `DEBUG`. *(§4.2)*
- [ ] Narrow `except (ImportError, Exception)` to `except ImportError`. *(§4.2)*
- [ ] Replace `Union[AuthService, Any]` with an `AuthServiceProtocol`. *(§4.4)*
