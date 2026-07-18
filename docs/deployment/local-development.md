# Local development (WSL)

Development on your machine — no `deploy.sh`, no Caddy, no `/var/www`.

## Stack

| Component | Command | URL |
|-----------|---------|-----|
| Frontend | `pnpm dev` | `http://localhost:5176` (or `VITE_PORT`) |
| Backend | `docker compose up -d` (repo root) | `http://localhost:8000` |
| API proxy | Vite proxies `/api` → backend | configured in `vite.config.ts` |

## Prerequisites

1. Node.js `^20.19.0` or `>=22.12.0`, **pnpm**
2. Docker (Compose V2)
3. **RustFS** (optional, for `STORAGE_TYPE=s3`):
   - RustFS runs outside this repo
   - External Docker network `rustfs-network` must exist: `docker network ls | grep rustfs-network`
   - Set S3 endpoints in `backend/.env` (see `backend/.env.example`)

## Quick start

```bash
# Terminal 1 — backend (from repo root)
cp backend/.env.example backend/.env   # first time only; edit as needed
docker compose up -d

# Terminal 2 — frontend
pnpm install
pnpm dev
```

Backend uses root [`compose.yaml`](../../compose.yaml) → [`docker-compose.dev.yml`](../../docker-compose.dev.yml) with **volume mounts** (`./backend/app`, `./backend/migrations`, etc.) so Python changes are visible without rebuilding the image.

## What is different from production

| | Local (WSL) | Production VPS |
|--|-------------|----------------|
| Frontend | Vite dev server | `pnpm build` → Caddy serves `/var/www/gear-stack` |
| Backend changes | Hot reload via mounts | Same mounts on VPS; `deploy.sh` rebuilds `app` container |
| Deploy script | Not used | `bash scripts/deploy.sh` |

## Related

- [CLAUDE.md](../../CLAUDE.md) — project commands
- [backend/README.md](../../backend/README.md) — backend env vars
- [production-manual.md](production-manual.md) — VPS deployment
