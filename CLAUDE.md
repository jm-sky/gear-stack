# CLAUDE.md

Gear Stack: Vue 3 + TypeScript frontend (repo root, `src/`) and FastAPI backend (`backend/`) for managing survival gear / bug-out bags. Package manager: **pnpm** only. Backend runs in Docker in dev.

Nested guides load only when you work in that dir: [src/CLAUDE.md](src/CLAUDE.md) (frontend rules), [backend/CLAUDE.md](backend/CLAUDE.md) (tests, CLI, Python rules). Architecture detail: [docs/claude/architecture.md](docs/claude/architecture.md) (read on demand).

## Commands

```bash
pnpm dev                # Vite dev server, port 5176 (VITE_PORT); /api proxied to VITE_API_PROXY_URL (default http://localhost:8000)
pnpm build              # type-check + build-only (regenerates PWA service worker)
pnpm lint               # eslint --fix --cache
pnpm type-check         # vue-tsc --build
pnpm test:run           # vitest once (pnpm test = watch; test:coverage)
pnpm test:e2e           # Playwright e2e (tests/e2e); test:integration = tests/integration
docker compose up -d    # backend stack, from REPO ROOT (compose.yaml -> docker-compose.dev.yml, name: gear-stack)
```

Node `^20.19.0` or `>=22.12.0`. Use `docker compose` (V2), never `docker-compose`.

## Critical rules

- **Docker safety:** NEVER run `docker`/`docker compose` if the project directory name starts with `_` (e.g. `_gear-stack-dev`) - it is a dev dir on the production server.
- **Containers (dev):** `gear-stack-app` (backend, auto-reload via WatchFiles - restart only for `.env` / `requirements.txt` changes), `gear-stack-db`, `gear-stack-redis`.
- **Gear data is V2-only.** Frontend: `useGearV2` / `useGearStoreV2` / `useGearQueries` / `gearQueryKeys`; backend: `gear_items_v2` (`GearItemDBV2`). V1 code was removed; do not reintroduce it. History: [docs/archive/v2-unified-model/migration-v1-to-v2.md](docs/archive/v2-unified-model/migration-v1-to-v2.md).
- **V2 cache gotcha:** `/gear` renders from TanStack Query. Any mutation (`useGearV2()` / `useGearMutations`) must invalidate `gearQueryKeys.all` or the UI goes stale.
- **Business logic** belongs in services (`modules/*/services`), not stores or components.
- **Shared core with ops-monitor** (`backend/app/core`, `app/common`, `cli`, frontend `src/shared`, `src/components/ui`): changes must be mirrored to `../ops-monitor`. See [docs/plans/REVIEW_AND_REFACTOR_PLAN.md](docs/plans/REVIEW_AND_REFACTOR_PLAN.md) and `../ops-monitor/docs/SHARED_CORE.md`.
- **Dependencies:** force transitive fixes via `pnpm.overrides` in `package.json` (not npm/yarn resolutions); re-run `pnpm build` after bumping build-toolchain deps. Plan: [docs/plans/security-dependabot-remediation.md](docs/plans/security-dependabot-remediation.md).
- Before committing Python: `python -m black .` and `python -m mypy .` in `backend/`.
- TypeScript: prefer dedicated union types over inline unions in props (global CLAUDE.md).

## Where to look (read on demand, don't bulk-read `docs/`)

| Need | File |
|------|------|
| Doc map + what is archived | [docs/README.md](docs/README.md) |
| Open bugs / debt | [docs/issues/README.md](docs/issues/README.md) |
| Review runs | [docs/reviews/README.md](docs/reviews/README.md) |
| Research / plans | [docs/research/README.md](docs/research/README.md), [docs/plans/README.md](docs/plans/README.md) |
| Deployment, Caddy, prod | [docs/deployment/README.md](docs/deployment/README.md) |
| Roadmap / features | [docs/ROADMAP.md](docs/ROADMAP.md), [FEATURES.md](FEATURES.md) |

Doc conventions: statuses `todo`, `planned`, `in progress`, `done`, `verification needed`. New issues `YYYY-MM-DD--NNN--slug.md`; reviews/research/plans `YYYY-MM-DD-slug.md`.

Do NOT read (huge / historical): `CHANGELOG.md` (130KB; only prepend a new entry on release), `docs/archive/**`, `V2_MIGRATION_STATUS.md` (completed V1->V2 migration status), `pnpm-lock.yaml`.
