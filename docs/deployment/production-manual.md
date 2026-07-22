# Production deployment (manual)

Current production setup on OVH VPS — deploy as your main user (e.g. `madeyskij`).

## Paths

| Purpose | Path |
|---------|------|
| Git repository | `/home/madeyskij/projects/gear-stack` |
| Frontend (Caddy) | `/var/www/gear-stack` |
| Backend | Docker Compose at repo root (`compose.yaml`) |

## Deploy

```bash
cd /home/madeyskij/projects/gear-stack
bash scripts/deploy.sh
```

The script asks for **sudo** once (needed to copy frontend build into `/var/www/gear-stack`).

### What `deploy.sh` does

1. **`git pull`**
2. **`scripts/frontend_build_deploy.sh`**
   - `pnpm install --frozen-lockfile`
   - `pnpm build` → `dist/`
   - `sudo rm` / `sudo cp` / `sudo chown` → `/var/www/gear-stack`
3. **`scripts/backend_restart_migrate.sh`**
   - `docker compose build app`
   - `docker compose up -d --force-recreate app`
   - `docker compose exec app python cli.py db migrate`

## Docker Compose on VPS

Production uses the same root [`compose.yaml`](../../compose.yaml) / [`docker-compose.dev.yml`](../../docker-compose.dev.yml) as local WSL, including **source volume mounts** so backend file changes are visible without a full image rebuild. The deploy script still rebuilds and recreates the `app` container when you run a full deploy.

```bash
# From repo root
docker compose ps
docker compose logs -f app
```

## Initial server setup (permissions)

Replace `madeyskij` with your username if different.

```bash
PROJECT_USER="madeyskij"
PROJECT_DIR="/home/$PROJECT_USER/projects/gear-stack"
DEPLOY_DIR="/var/www/gear-stack"

sudo groupadd -f deploy
sudo usermod -a -G docker,caddy,deploy "$PROJECT_USER"

sudo chown -R "$PROJECT_USER":deploy "$PROJECT_DIR"
sudo chmod -R g+rwX "$PROJECT_DIR"
sudo chmod g+s "$PROJECT_DIR"

sudo mkdir -p "$DEPLOY_DIR"
sudo chown -R caddy:deploy "$DEPLOY_DIR"
sudo chmod -R 775 "$DEPLOY_DIR"
sudo chmod g+s "$DEPLOY_DIR"
```

Log out and back in after group changes. Verify: `groups` should include `docker`, `caddy`, `deploy`.

## Troubleshooting

| Problem | Check |
|---------|--------|
| Permission denied on deploy | Group setup above; re-login |
| Frontend not updating | `ls -la /var/www/gear-stack/`; hard refresh browser |
| Docker fails | `groups` includes `docker`; `docker compose ps` from repo root |
| Backend not healthy | `docker compose logs -f app` |

## Related

- [CADDY_DEPLOYMENT.md](CADDY_DEPLOYMENT.md) — Caddy config
- [production-github-actions.md](production-github-actions.md) — future CI deploy
- [local-development.md](local-development.md) — WSL dev
