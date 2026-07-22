# Gear Stack — Security review (BACKEND ONLY)

You are doing ONE focused security review of the FastAPI backend. Budget is tight (~$25 on Claude Fable) — prioritize depth on authz/authn over exhaustive file reading. Do NOT implement fixes. Do NOT review frontend (`src/`) except when needed to confirm an API contract.

## Repo

- Path: `/home/madeyskij/projects/gear-stack`
- Scope: `backend/app/` (auth, admin, users, two_factor/WebAuthn, gear, AI, billing, media/uploads, middleware, core)
- Output file (fill this): `docs/reviews/2026-07-06-security-backend.md`
- After findings: create actionable issues under `docs/issues/` using `YYYY-MM-DD--NNN--slug.md` and add rows to `docs/issues/README.md`
- Update status in the review file + `docs/reviews/README.md` → `done` (or `verification needed` if you need human confirmation)

## Read first (baseline — do not blindly restate)

1. `docs/reviews/2026-07-06-security-backend.md` (checklist + Findings table)
2. `docs/reviews/README.md`
3. `docs/plans/SECURITY_IMPROVEMENT_PLAN.md` (roadmap context only)
4. `docs/plans/REVIEW_AND_REFACTOR_PLAN.md` §3 Security
5. `CLAUDE.md` (auth/security notes)
6. Recent security work (VERIFY still correct, do not re-open as new bugs unless broken):
   - WebAuthn authentication verification (not registration-only stub)
   - `tfaVerified` on TOTP/passkey login tokens
   - Users-router owner mutation guard (`enforce_user_mutation_permissions`)
   - Rate limiter wired via `setup_limiter`; XFF trust model
   - Dead `app/exceptions/` + broken `POST /users/` removal
   - JWT iss/aud, session blacklist / JTI / `token_version`

## Method (stay in budget)

1. Start from routers + deps: auth, admin, users, two_factor, gear ownership, AI, billing, media.
2. Trace each high-risk path end-to-end (router → service → repository). Prefer reading code over guessing.
3. For each finding: severity (Critical/High/Medium/Low/Info), exact file:line, exploit scenario, concrete fix recommendation.
4. Skip dependency CVE hunting beyond obvious floor issues already in `docs/plans/security-dependabot-remediation.md` unless you spot a clearly exploitable package misuse.
5. Do not rewrite large files. Do not run long refactors. Optional: targeted `pytest` only if needed to confirm a finding.
6. Stop when the checklist is covered OR when further reading is low-ROI — leave unchecked items noted as "not reviewed / out of budget" rather than inventing findings.
7. Hard limit: do not read more than ~40 backend files; prefer routers + auth modules.

## Checklist (must cover)

- [ ] JWT: `type` claim, blacklist, refresh rotation, `iss`/`aud`, purpose separation
- [ ] Auth deps: `CurrentUser`, `AdminUser`, rejection of `tfaPending` tokens on privileged routes
- [ ] Security headers / CSP middleware
- [ ] CORS, TrustedHost, rate limiting, reCAPTCHA
- [ ] Input validation, SQLi surfaces, mass-assignment
- [ ] Authorization: IDOR / ownership on gear, admin, AI, billing, catalogue/media
- [ ] File upload: mime, path traversal, size, S3/local adapters
- [ ] Secrets: startup assertions, `SECRET_KEY`, `.env` leakage risk
- [ ] Error responses: no stack traces/secrets in prod paths
- [ ] Residual stubs / TODOs that disable security (esp. 2FA/WebAuthn/OAuth)

## Out of scope this run

- Frontend XSS / localStorage token storage (separate review file)
- Shared-core backport to other projects (note "affects core family" if relevant, but do not switch repos)
- UX, performance, dependency bumps, code style

## Deliverables

1. Fill **Findings** table in `docs/reviews/2026-07-06-security-backend.md`
2. Tick checklist items (mark skipped explicitly)
3. Create follow-up issues for Critical/High/Medium only (group Low/Info in the review unless easy wins)
4. Short executive summary at top of Findings: top 3 risks + overall posture (1 paragraph)
5. Final message to me: count of findings by severity + list of new issue files

Language: write the review file and issues in English (match existing docs). Keep commit-ready markdown only — no code changes unless a finding is a one-line comment/doc fix you already verified.
