# Production deployment (GitHub Actions)

**Status: planned** — workflow exists; manual deploy is used today. Enable when secrets and `deploy` user sudoers are configured.

## Workflow

[`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml):

1. **Lint and type-check** on GitHub runner (`pnpm lint`, `pnpm type-check`)
2. **SSH deploy** — connects as `VPS_USER`, runs `bash scripts/deploy.sh` in `VPS_PROJECT_PATH`

Push to `main` or manual `workflow_dispatch` triggers the workflow.

## Required GitHub Secrets

| Secret | Example |
|--------|---------|
| `VPS_HOST` | Server IP or hostname |
| `VPS_USER` | `deploy` |
| `VPS_SSH_KEY` | Full private key (with trailing newline) |
| `VPS_PORT` | Optional, default `22` |
| `VPS_PROJECT_PATH` | `/home/madeyskij/projects/gear-stack` |

Do **not** use legacy names `DEPLOY_HOST` / `DEPLOY_SSH_KEY` — the workflow expects `VPS_*`.

## `deploy` user requirements

The `deploy` user exists on the VPS for CI. It must be able to run the same [`scripts/deploy.sh`](../../scripts/deploy.sh) as manual deploy, but **without an interactive sudo password**.

### Groups

```bash
sudo usermod -a -G docker,caddy,deploy deploy
```

### Project directory access

Repo lives under the main user (`/home/madeyskij/projects/gear-stack`). The `deploy` group must have read/write on that tree (see [production-manual.md](production-manual.md) permissions).

### Sudoers (passwordless frontend deploy)

`deploy.sh` runs `sudo -v` and `frontend_build_deploy.sh` uses `sudo` for `/var/www/gear-stack`. Configure:

```bash
sudo tee /etc/sudoers.d/gear-stack-deploy > /dev/null <<'EOF'
deploy ALL=(ALL) NOPASSWD: /bin/rm -rf /var/www/gear-stack/*, /bin/cp -r * /var/www/gear-stack/, /usr/bin/chown -R caddy\:deploy /var/www/gear-stack
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload caddy
EOF
sudo chmod 440 /etc/sudoers.d/gear-stack-deploy
sudo visudo -c -f /etc/sudoers.d/gear-stack-deploy
```

### SSH key

```bash
sudo su - deploy
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
# Copy private key to GitHub secret VPS_SSH_KEY
exit
```

## Verification

1. GitHub → Actions → check workflow runs on `main`
2. Settings → Secrets → all `VPS_*` secrets set
3. Test SSH: `ssh deploy@YOUR_HOST`
4. On failure: [ssh-troubleshooting.md](ssh-troubleshooting.md)

## Related

- [production-manual.md](production-manual.md) — current manual process
- [ssh-troubleshooting.md](ssh-troubleshooting.md) — SSH debugging
