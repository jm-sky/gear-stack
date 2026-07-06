# Code quality review — Frontend

**Status:** `planned`  
**Scope:** Vue 3 frontend (`src/`)  
**Run:** One dedicated AI session

## Baseline

- [REVIEW_AND_REFACTOR_PLAN.md §4, §6](../REVIEW_AND_REFACTOR_PLAN.md)
- [research/refactor/README.md](../research/refactor/README.md) — refactor analysis program
- [migration-v1-to-v2.md](../migration-v1-to-v2.md)
- [V2_CODE_REVIEW_FINDINGS.md](../V2_CODE_REVIEW_FINDINGS.md)

## Checklist

- [ ] V1/V2 duplication: `useGear` vs `useGearV2`, stores, services, invalidation
- [ ] Component size and responsibility (pages vs composables vs services)
- [ ] Pinia vs TanStack Query boundaries (server vs client state)
- [ ] ESLint / project conventions (`.cursorrules`, `eslint.config.ts`)
- [ ] TypeScript strictness, union types in `types/`
- [ ] DRY: action icons, category icons, route helpers
- [ ] Test coverage (`*.spec.ts`, vitest)
- [ ] Dead code and legacy paths still imported
- [ ] Shared UI (`src/shared/`, `src/components/ui/`) drift with ops-monitor

## Cross-check

- [issues/README.md](../issues/README.md) (recurring V1/V2 pattern)

## Findings

| Severity | Location | Finding | Recommendation |
|----------|----------|---------|----------------|
| | | | |

## Follow-ups

_(Link new files under `docs/issues/` when actionable)_
