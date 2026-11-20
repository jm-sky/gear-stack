# Backend rules (backend/)

FastAPI + PostgreSQL + Redis, async. Layout: `app/core`, `app/common` (shared core, mirror to ops-monitor), `app/modules/<feature>` (gear, auth, billing, ai, admin, stats, ...), `migrations/`, `cli/`, `tests/`.

- Run Docker from the **repo root**; never if the dir name starts with `_` (see root CLAUDE.md). Dev container: `gear-stack-app`; auto-reload on, restart only for `.env` / `requirements.txt` changes.
- Before committing Python, in `backend/`: `python -m black .` and `python -m mypy .`.
- Gear data lives in `gear_items_v2` (`GearItemDBV2`); no V1 models/tables.

## Tests (pytest + pytest-asyncio, real PostgreSQL `backend_test`)

```bash
docker exec gear-stack-app python -m pytest tests/ -v
docker exec gear-stack-app python -m pytest tests/integration/gear/test_containers_crud.py::TestContainerCreate::test_create_container_minimal_data -v
docker exec gear-stack-app python -m pytest tests/ --cov=app --cov-report=html
# without Docker: cd backend && source .venv/bin/activate && python -m pytest tests/ -v
docker exec gear-stack-app python -m cli db init-test [--force]   # create/recreate test DB
```

## CLI (`python -m cli`, Django-style; no args = interactive menu; prefix `docker exec gear-stack-app`, add `-it` for interactive)

```bash
python -m cli db init | migrate | migrate-status | init-test [--force]
python -m cli db seed catalogue | seed-remove catalogue
python -m cli users create | list | set-role | toggle-admin
python -m cli test sentry | storage | email
```
