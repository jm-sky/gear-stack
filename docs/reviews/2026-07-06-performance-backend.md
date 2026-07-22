# Performance review — Backend

**Status:** `planned`  
**Scope:** FastAPI backend, PostgreSQL, storage  
**Run:** One dedicated AI session

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md](../plans/REVIEW_AND_REFACTOR_PLAN.md) (N+1 mentions in gear service)
- [research/billing-performance-recommendations.md](../research/billing-performance-recommendations.md)
- [research/PERFORMANCE_ANALYSIS.md](../research/PERFORMANCE_ANALYSIS.md)
- [issues/2026-07-05--009--catalogue-images.md](../issues/2026-07-05--009--catalogue-images.md) (transaction/session patterns)

## Checklist

- [ ] N+1 queries in gear V2 list/detail/catalogue endpoints
- [ ] Missing indexes on hot paths (`gear_items_v2`, images, FKs)
- [ ] Large payloads: container trees, image metadata, export endpoints
- [ ] SQLAlchemy session lifecycle (commits, flush, transaction boundaries)
- [ ] Image processing and storage I/O (local vs S3)
- [ ] Rate limiting impact under load
- [ ] AI module: streaming, timeouts, token usage
- [ ] Caching opportunities (read-heavy catalogue, stats)

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
