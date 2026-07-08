# Deployment

Gear Stack has three deployment contexts. Full documentation lives in [`docs/deployment/`](docs/deployment/README.md).

## Scenarios

| Environment | How | Documentation |
|-------------|-----|---------------|
| **Local (WSL)** | `pnpm dev` + `docker compose -f backend/docker-compose.yml up` | [local-development.md](docs/deployment/local-development.md) |
| **Production VPS (manual)** | `bash scripts/deploy.sh` as main user | [production-manual.md](docs/deployment/production-manual.md) |
| **Production VPS (CI)** | GitHub Actions → SSH → same `deploy.sh` | [production-github-actions.md](docs/deployment/production-github-actions.md) (planned) |

## Production paths (OVH)

- **Repository:** `/home/madeyskij/projects/gear-stack`
- **Frontend (Caddy):** `/var/www/gear-stack`
- **Backend:** `backend/docker-compose.yml` (volume mounts for hot reload on WSL and VPS)

## Quick manual deploy

```bash
cd /home/madeyskij/projects/gear-stack
bash scripts/deploy.sh
```

## More

- [docs/deployment/README.md](docs/deployment/README.md) — index (Caddy, security, SSH troubleshooting)
- [CLAUDE.md](CLAUDE.md) — development commands
