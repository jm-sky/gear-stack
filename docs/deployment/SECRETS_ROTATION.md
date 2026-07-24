# Secrets Rotation

**Status:** Documented runbook (2026-07-24)  
**Scope:** JWT signing key, OAuth client secrets, PostgreSQL / Redis passwords, S3 keys (and related `.env` secrets)  
**Related:** [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md), [SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md), `backend/.env.example`

> **Rules:** Never commit real secrets. Never paste production values into tickets, chat, or docs. Generate values with `openssl` / cloud consoles; update `backend/.env` (or your secret store); restart only the services that read the changed vars.  
> **Docker safety:** Do not run `docker` / `docker compose` if the project directory name starts with `_`.

Compose from **repo root**. App container: `gear-stack-app`. DB: `gear-stack-db`. Redis: `gear-stack-redis`.

---

## Schedule (suggested)

| Secret | Env vars (examples) | Cadence | Impact on rotate |
|--------|---------------------|---------|------------------|
| JWT signing key | `SECRET_KEY` | ~180 days or after suspicion of leak | **All sessions invalid** — users must re-login |
| PostgreSQL password | `POSTGRES_PASSWORD` (+ `DATABASE_URL` if set explicitly) | ~90 days | App cannot talk to DB until `.env` + restart match |
| Redis password | `REDIS_PASSWORD` (+ `REDIS_URL` if set) | ~90 days | Blacklist / short-lived caches reset |
| S3 access keys | `STORAGE_S3_ACCESS_KEY`, `STORAGE_S3_SECRET_KEY` | ~90 days | Uploads/downloads fail until updated |
| OAuth client secrets | `GOOGLE_OAUTH_CLIENT_SECRET`, `GITHUB_OAUTH_CLIENT_SECRET`, `FACEBOOK_OAUTH_CLIENT_SECRET` | ~180 days or on provider alert | Provider login fails until updated |
| Stripe / reCAPTCHA / Sentry | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `RECAPTCHA_SECRET_KEY`, `SENTRY_DSN` (and related) | Per vendor policy / on leak | Feature-specific outage |

Prefer calendar reminders over memory. After any production incident involving credentials, rotate **immediately** (do not wait for the cadence).

---

## General procedure

1. Generate or create the new secret (openssl / cloud IAM / OAuth console).  
2. Store it in a secure place first (password manager / vault).  
3. Update the **runtime** source of truth (`backend/.env` on the host, or CI secrets).  
4. Apply the change on the dependency side if needed (DB `ALTER USER`, IAM activate new key, OAuth console save).  
5. Restart the consuming service(s).  
6. Verify (health, login, upload, OAuth).  
7. Retire the old secret (deactivate IAM key, revoke OAuth secret, etc.).  
8. Shred local temp files (`shred -u` / delete from clipboard history).

Take a DB dump before rotating DB credentials if you are unsure about rollback ([BACKUP_RECOVERY.md](BACKUP_RECOVERY.md)).

---

## JWT — `SECRET_KEY`

Rotating invalidates **all** access and refresh tokens (users logged out).

```bash
openssl rand -base64 64
# Set SECRET_KEY=... in backend/.env (min length enforced by settings)
# From repo root (directory must not start with _):
docker compose restart app
```

Smoke: login, refresh (`/api/auth/refresh` via SPA), logout.

Optional hardening later: dual-key verification during a transition window (not implemented today — treat rotate as a hard cutover).

---

## PostgreSQL — `POSTGRES_PASSWORD`

1. Generate: `openssl rand -base64 32`  
2. Inside Postgres (as a superuser / owner capable of `ALTER USER`):

```bash
docker exec -it gear-stack-db psql -U backend -d postgres
# ALTER USER backend WITH PASSWORD '<new-password>';
# \q
```

3. Update `POSTGRES_PASSWORD` in `backend/.env`. If you maintain a full `DATABASE_URL`, update the password embedded there too.  
4. Restart app (and any other clients): `docker compose restart app`  
5. Verify: `docker compose logs app --tail 100` (no DB auth errors); hit a simple authenticated API.  
6. Confirm old password no longer works.

Compose also passes password into the `db` service on **first** volume init; changing only `ALTER USER` + app `.env` is the live rotation path for an existing data volume.

---

## Redis — `REDIS_PASSWORD`

1. Generate a new password.  
2. Update `REDIS_PASSWORD` in `backend/.env` (and `REDIS_URL` if used).  
3. Recreate or restart Redis so `--requirepass` picks up the new value, then restart app:

```bash
docker compose up -d redis
docker compose restart app
```

4. Verify app starts; perform login/logout (blacklist path). Expect existing blacklist entries to be gone after Redis recreate — acceptable.

---

## S3 — `STORAGE_S3_*`

Only when `STORAGE_TYPE=s3`.

1. In the provider console, **create** a new access key (keep the old key active).  
2. Put the new key/secret into `backend/.env` (`STORAGE_S3_ACCESS_KEY`, `STORAGE_S3_SECRET_KEY`; review endpoint/region/bucket).  
3. `docker compose restart app`  
4. Verify upload + public/read URL for an item image.  
5. Deactivate the old key; after a soak period (e.g. 7 days), delete it.

If keys leaked: deactivate old keys first (accept brief outage), then deploy new keys.

---

## OAuth client secrets

For each provider you use (Google / GitHub / Facebook):

1. In the provider developer console, rotate/create a new **client secret** (keep client ID unless you are replacing the whole app).  
2. Update the matching `*_OAUTH_CLIENT_SECRET` (and redirect URI if it changed) in `backend/.env`.  
3. `docker compose restart app`  
4. Smoke: “Login with …” for that provider (OAuth `state` CSRF remains separate and unchanged).  
5. Remove/disable the old secret in the provider console.

---

## Stripe / reCAPTCHA / other

Follow the vendor’s rotate flow, update `.env`, restart `app`, then:

- Stripe: test webhook signature (`/api/billing/webhook`) with Stripe CLI or dashboard resend.  
- reCAPTCHA: submit a protected form once with the new keys.

---

## Rollback

| Secret | Rollback |
|--------|----------|
| `SECRET_KEY` | Restore previous `SECRET_KEY` and restart app (only if you still have the old value); sessions minted with the new key die again |
| DB password | `ALTER USER` back to previous password **or** forward-fix to a known-good password; keep `.env` in sync |
| S3 / OAuth | Re-activate previous key/secret in the console; point `.env` back; restart |

If rollback is unclear, restore app config from your encrypted secret backup — not from git history (secrets must not be in git).

---

## Checklist

- [ ] Rotation calendar entries exist for JWT / DB / Redis / S3 / OAuth  
- [ ] Procedure tested once on non-prod (or VPS worktree that is **not** `_`-prefixed production confusion)  
- [ ] Post-rotate smoke: password login, refresh cookie, OAuth (if enabled), media upload (if S3)  
- [ ] Old credentials revoked  
- [ ] No secrets written into markdown, issues, or commits  

---

## Related

- `backend/.env.example` — variable names (placeholders only)  
- [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md) — dump before risky DB changes  
- [SECURITY_FIX.md](SECURITY_FIX.md) — DB/Redis exposure hardening  
