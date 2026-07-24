# Deployment

Runbooks and configuration for Gear Stack environments.

## Scenarios

| Scenario | Doc | Status |
|----------|-----|--------|
| Local development (WSL) | [local-development.md](local-development.md) | Active |
| Production VPS (manual) | [production-manual.md](production-manual.md) | Active |
| Production VPS (GitHub Actions) | [production-github-actions.md](production-github-actions.md) | Planned |

Entry point from repo root: [DEPLOYMENT.md](../../DEPLOYMENT.md).

## Runbooks

| File | Summary |
|------|---------|
| [ssh-troubleshooting.md](ssh-troubleshooting.md) | SSH / GitHub Actions debugging |
| [Caddyfile.example](Caddyfile.example) | Example Caddy cache headers |
| [gear-stack.caddy](gear-stack.caddy) | Project Caddy site config |
| [CADDY_DEPLOYMENT.md](CADDY_DEPLOYMENT.md) | Caddy deployment |
| [CADDY_ADVANCED_SECURITY.md](CADDY_ADVANCED_SECURITY.md) | Advanced Caddy security |
| [SECURITY_FIX.md](SECURITY_FIX.md) | Docker/DB hardening (PostgreSQL, Redis) |
| [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md) | Postgres (+ optional S3/media) backup & safe restore |
| [SECRETS_ROTATION.md](SECRETS_ROTATION.md) | Rotate JWT, OAuth, DB, Redis, S3 secrets |
| [production-manual.md](production-manual.md#database-backups-local-dumps) | VPS manual deploy + short dump pointer |

## Phase 6 (billing / Stripe checklist)

Separate from day-to-day deploy:

| File | Summary |
|------|---------|
| [phase-6-production-deployment-guide.md](phase-6-production-deployment-guide.md) | Full phase 6 guide |
| [PHASE-6-QUICK-START.md](PHASE-6-QUICK-START.md) | Quick checklist |
| [PHASE-6-COMPLETION.md](PHASE-6-COMPLETION.md) | Completion summary |

## Related

- [plans/SECURITY_IMPROVEMENT_PLAN.md](../plans/SECURITY_IMPROVEMENT_PLAN.md) — production security roadmap
