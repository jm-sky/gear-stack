# Performance review — Frontend

**Status:** `planned`  
**Scope:** Vue 3 frontend, build, PWA  
**Run:** One dedicated AI session

## Baseline

- [migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md) (TanStack Query / V2 cache)
- [research/LIGHTHOUSE_CRITICAL_PATH_ANALYSIS.md](../research/LIGHTHOUSE_CRITICAL_PATH_ANALYSIS.md)
- [research/PERFORMANCE_ANALYSIS.md](../research/PERFORMANCE_ANALYSIS.md)
- [issues/README.md](../issues/README.md) (stale cache after mutations)

## Checklist

- [ ] Bundle size and code-splitting (route-level lazy imports)
- [ ] TanStack Query: `staleTime`, invalidation, duplicate fetches
- [ ] V1/V2 double subscriptions or redundant API calls
- [ ] Image loading: per-item requests in galleries, lazy load, sizes
- [ ] Large lists / tables (virtualization if needed)
- [ ] PWA service worker cache strategy (`pwa.config.ts`)
- [ ] Re-renders in heavy pages (container detail, items table)
- [ ] `localStorage` read/write on hot paths

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
