# Security review — Frontend

**Status:** `planned`  
**Scope:** Vue 3 frontend (`src/`)  
**Run:** One dedicated AI session

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md §3](../REVIEW_AND_REFACTOR_PLAN.md#3-security-review) (§3.1–3.2 especially)
- [plans/SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md)
- [security-dependabot-remediation.md](../security-dependabot-remediation.md) (pnpm overrides)

## Checklist

- [ ] Token storage: `localStorage` vs in-memory / HttpOnly cookie strategy
- [ ] Auth interceptor and refresh flow (`auth.interceptor.ts`, token refresh store)
- [ ] XSS surfaces: `v-html`, markdown rendering, user-generated content
- [ ] CSP compatibility (inline scripts, third-party: Sentry, reCAPTCHA)
- [ ] WebAuthn / passkeys implementation
- [ ] API client: credentials, error handling, no secrets in client bundle
- [ ] Route guards: auth, admin, edge cases (expired session)
- [ ] Sensitive data in localStorage (gear, settings, AI history)
- [ ] Dependency audit (direct + transitive via `pnpm.overrides`)

## Cross-check

- [issues/README.md](../issues/README.md) (V1/V2 cache — stale UI, not direct security, but mutation paths)

## Findings

_(Record after run)_

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
