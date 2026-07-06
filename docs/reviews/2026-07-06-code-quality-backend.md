# Code quality review — Backend

**Status:** `planned`  
**Scope:** FastAPI backend (`backend/app/`, `backend/tests/`)  
**Run:** One dedicated AI session

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md §4–5](../REVIEW_AND_REFACTOR_PLAN.md#4-solid--architecture)
- [research/refactor/README.md](../research/refactor/README.md) — refactor analysis program
- [migration-v1-to-v2.md](../migration-v1-to-v2.md) (V2 target state)

## Checklist

- [ ] God files: `gear/service.py`, `repository.py`, `router.py` — SRP, split plan
- [ ] Repository pattern consistency and interface usage
- [ ] Dependency injection (`Depends`, settings singleton vs injected)
- [ ] Error handling and logging (duplicated Sentry filters, etc.)
- [ ] Type hints and mypy coverage on critical paths
- [ ] Test coverage vs code volume (integration tests in `backend/tests/`)
- [ ] V1 vs V2 gear code — what can be removed, what still serves traffic
- [ ] CLI, migrations, seed scripts maintainability
- [ ] Shared-core drift with ops-monitor

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
