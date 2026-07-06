# Security review — Backend

**Status:** `planned`  
**Scope:** FastAPI backend (`backend/app/`)  
**Run:** One dedicated AI session

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md §3](../REVIEW_AND_REFACTOR_PLAN.md#3-security-review)
- [plans/SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md)
- [security-dependabot-remediation.md](../security-dependabot-remediation.md)
- Shared core drift: `backend/app/core/`, `backend/app/common/` vs ops-monitor

## Checklist

- [ ] JWT: `type` claim, blacklist, refresh rotation, `iss`/`aud`, per-purpose keys
- [ ] Auth dependencies: `CurrentUser`, `AdminUser`, 2FA-pending rejection
- [ ] CSP and security headers (`app/core/security_headers.py`)
- [ ] CORS, `TrustedHost`, rate limiting, reCAPTCHA
- [ ] Input validation (Pydantic), SQL injection surfaces, mass-assignment
- [ ] Authorization on all gear/admin/AI endpoints (IDOR, ownership checks)
- [ ] File upload: mime validation, path traversal, size limits, S3/local adapters
- [ ] Secrets: `SECRET_KEY` strength, production startup assertions, `.env` handling
- [ ] Error responses: no stack traces / secrets in production
- [ ] Shared-core files that differ from ops-monitor

## Cross-check

- [issues/README.md](../issues/README.md)
- [issues/2026-07-05--009--catalogue-images.md](../issues/2026-07-05--009--catalogue-images.md)

## Findings

_(Record after run: severity · file · description · recommendation)_

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
