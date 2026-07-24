# Backup and Recovery

**Status:** Documented runbook (2026-07-24)  
**Scope:** PostgreSQL (primary) + optional S3/media objects  
**Related:** [production-manual.md](production-manual.md) (short dump snippet), [SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md)

> **Docker safety:** Never run `docker` / `docker compose` if the project directory name starts with `_` (e.g. `_gear-stack-dev` on the VPS). That prefix marks a non-production worktree that can collide with live containers.

Compose project name: `gear-stack`. Typical containers: `gear-stack-db`, `gear-stack-app`, `gear-stack-redis`. Run Compose from the **repo root** (`compose.yaml` → `docker-compose.dev.yml`).

---

## What to back up

| Asset | Criticality | Notes |
|-------|-------------|--------|
| PostgreSQL (`POSTGRES_DB`, default `backend`) | **Required** | Users, auth sessions metadata, gear V2, billing, etc. |
| Object storage (S3 / MinIO) when `STORAGE_TYPE=s3` | High if used | Item images and other media; DB alone is not enough |
| Local media volume (if `STORAGE_TYPE=local`) | High if used | Path depends on compose/volume mounts — include in host backup if applicable |
| `backend/.env` | Ops only | **Never** store in the same public dump bucket without encryption; prefer a secrets manager / encrypted vault |
| Redis | Low | Token blacklist / short-lived state — rebuilds on use; usually skip |

Canonical on-host dump directory: **`.backups/`** at the repo root (gitignored). Do **not** use a top-level `backups/` directory.

Naming: `gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz`.

Default credentials come from `backend/.env` (`POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`). Examples below use `backend` / `backend` as in `.env.example`.

---

## Create a PostgreSQL dump

```bash
cd /path/to/gear-stack   # must NOT start with _
mkdir -p .backups
docker exec gear-stack-db pg_dump -U backend backend \
  | gzip > ".backups/gear-stack-postgres-$(date +%Y%m%d-%H%M%S).sql.gz"
ls -lh .backups/gear-stack-postgres-*.sql.gz | tail -3
```

Verify the archive is non-empty and gzip-valid:

```bash
gzip -t .backups/gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz
zcat .backups/gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz | head -n 20
```

### Optional: cron (daily)

Example (adjust path and user):

```bash
# crontab -e
0 2 * * * cd /path/to/gear-stack && mkdir -p .backups && docker exec gear-stack-db pg_dump -U backend backend | gzip > ".backups/gear-stack-postgres-$(date +\%Y\%m\%d-\%H\%M\%S).sql.gz" && find .backups -name 'gear-stack-postgres-*.sql.gz' -mtime +30 -delete
```

### Optional: off-site copy

Copy dumps to a **dedicated backup** bucket (not the live media bucket), with lifecycle retention:

```bash
# Example with AWS CLI — use your real bucket/profile; do not commit keys
aws s3 cp .backups/gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz \
  s3://YOUR_BACKUP_BUCKET/gear-stack/postgres/
```

---

## Media / S3 (when used)

If `STORAGE_TYPE=s3` in `backend/.env`:

| Variable | Purpose |
|----------|---------|
| `STORAGE_S3_BUCKET` | Live uploads bucket |
| `STORAGE_S3_ENDPOINT_URL` | Optional (MinIO / S3-compatible) |
| `STORAGE_S3_ACCESS_KEY` / `STORAGE_S3_SECRET_KEY` | Credentials |

Backup the **object store** separately from Postgres (versioning + periodic sync to a backup bucket, or provider snapshot). Example sync (read-only source → backup destination):

```bash
aws s3 sync s3://YOUR_LIVE_MEDIA_BUCKET s3://YOUR_BACKUP_BUCKET/gear-stack/media/ --delete
```

If `STORAGE_TYPE=local`, include the mounted uploads directory in host/filesystem backups.

---

## Safe restore checklist (do **not** destroy prod)

Goal: prove a dump restores **without** overwriting the live database.

### A) Preferred — restore into a throwaway database

1. Confirm you are on the intended host and directory name does **not** start with `_`.
2. Note live DB name (`POSTGRES_DB`, usually `backend`). **Do not drop it.**
3. Create a temporary database inside the running Postgres container:

```bash
docker exec -i gear-stack-db psql -U backend -d postgres -c \
  "CREATE DATABASE backend_restore_test OWNER backend;"
```

4. Load the dump into the **test** database only:

```bash
gunzip -c .backups/gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz \
  | docker exec -i gear-stack-db psql -U backend -d backend_restore_test
```

5. Spot-check (tables / row counts):

```bash
docker exec -i gear-stack-db psql -U backend -d backend_restore_test -c '\dt'
docker exec -i gear-stack-db psql -U backend -d backend_restore_test -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

6. Drop the throwaway DB when done:

```bash
docker exec -i gear-stack-db psql -U backend -d postgres -c \
  "DROP DATABASE backend_restore_test;"
```

### B) Staging / clone host

Restore the dump on a non-production Compose stack (different `COMPOSE_PROJECT_NAME` / host). Point a temporary app at that DB and smoke-test login + gear list.

### C) Production cutover (destructive — only with explicit ops approval)

Use only after A or B succeeded and you have a **fresh** pre-cutover dump.

1. Put the app in maintenance / stop write traffic (`docker compose stop app` from repo root).
2. Take one last dump of the live DB into `.backups/`.
3. Restore into the live DB (this **replaces** data):

```bash
gunzip -c .backups/gear-stack-postgres-YYYYMMDD-HHMMSS.sql.gz \
  | docker exec -i gear-stack-db psql -U backend backend
```

4. Restore media from the matching S3/local backup if needed.
5. Start the app (`docker compose start app` or `up -d`) and verify health + login.
6. Keep the pre-cutover dump until the next verified backup cycle.

---

## Recovery RPO / RTO (targets)

| Metric | Target (ops judgment) |
|--------|------------------------|
| RPO | ≤ 24h with daily dumps; tighten with more frequent cron / WAL if needed |
| RTO | Hours: restore DB + media + config; practice quarterly via checklist A |

---

## Quarterly drill

- [ ] Create a fresh dump; `gzip -t` passes  
- [ ] Restore into `backend_restore_test` (checklist A)  
- [ ] Confirm table list / sample counts look sane  
- [ ] Drop `backend_restore_test`  
- [ ] If S3 media is in use: confirm backup bucket / sync still works  
- [ ] Record date and operator in your ops log (or Ops Monitor notes)

---

## Related

- [production-manual.md](production-manual.md) — VPS deploy + short dump pointer  
- [SECURITY_FIX.md](SECURITY_FIX.md) — DB/Redis Docker hardening  
- [SECRETS_ROTATION.md](SECRETS_ROTATION.md) — rotating DB/S3 credentials after incident  
- [ROADMAP.md](../ROADMAP.md) — Security Hardening section  
