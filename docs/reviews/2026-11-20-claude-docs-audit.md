# Claude Code docs audit

**Status:** `done` | **Date:** 2026-11-20 | **Scope:** documentation loaded or read by Claude Code in this repo

## Findings

1. Root `CLAUDE.md` was 22,293 B, loaded every session. Roughly 70% was generic (Vue/Tailwind/TS best practice, feature list, tech-stack lists, full CLI/test command listings) or architecture detail needed only occasionally.
2. Stale / contradictory facts in the old file:
   - "Hybrid architecture ... gear containers in localStorage `gear-stack:containers`" contradicted the V1->V2 section. Reality: gear is V2/backend (`gear_items_v2`); `useGearStoreV2` keeps an offline cache under `gear-stack:items-v2`; `gear-stack:containers` is only a legacy V1 snapshot read by `v1ToV2Migration` / `dataMigrationService` for local->API upload.
   - "Service classes ... `gearService.createContainer` / `useGearStore`" examples refer to V1 code that no longer exists (`src/modules/gear/services` has only V2/API services).
   - Module list omitted `billing`.
   - Action icon keys list was outdated (missing `clone`, `publish`, `ai`, `aiPremium`, `exportToCSV`, `exportToJson`, `exportAllToMarkdown`, `uploadPhoto`, `starItem`, `toggleItemImages`; `exportAllToPrompt` is not a key). Replaced by "keys = object keys in actionIcons.ts".
   - Commands list lacked `test:e2e` / `test:integration`; `pnpm build` is `run-p type-check build-only` (parallel), fine as described.
   - Container names verified OK (`gear-stack-app`, `-db`, `-redis`); ESLint rules verified (semi never, single quotes, max-attributes, self-closing, perfectionist import groups). Object keys are explicitly unsorted (`sort-objects: unsorted`), now noted. "No line break before else/catch/finally" is not an ESLint rule in the config - kept as a style note.
3. Trailing line "Run black and mypy" was glued to the Responsive Design section; now an explicit rule.
4. `docs/` is 2.7 MB / 193 files; `docs/README.md` (last updated 2026-07-06) did not tell agents what is historical. `CHANGELOG.md` is 132 KB and `FEATURES.md` 21 KB; neither should be read whole.
5. `.claude/` had only `commands/release-version.md` (fine, 384 B), no settings.

## Changes

| File | Change | Size |
|------|--------|------|
| `CLAUDE.md` | rewritten lean: overview, commands, critical rules, doc index, do-not-read list | 22,293 -> 3,805 B |
| `src/CLAUDE.md` (new) | frontend ESLint specifics, Vue/TS conventions, icons/Checkbox/Tailwind gotchas (lazy-loaded in `src/`) | 2,821 B |
| `backend/CLAUDE.md` (new) | tests, CLI, black/mypy, Docker notes (lazy-loaded in `backend/`) | 1,524 B |
| `docs/claude/architecture.md` (new) | modules, state/persistence, routing, i18n (on demand) | 2,295 B |
| `docs/README.md` | added "Dla agentow AI" section listing historical docs to skip | small |
| `.claude/settings.json` (new) | `permissions.deny` Read for `node_modules`, `dist`, `coverage`, `backend/.venv` | minimal |
| `docs/reviews/README.md` | added row for this review | - |

Always-loaded context in this repo: 22.3 KB -> 3.8 KB (about -83%); work in `src/` or `backend/` adds 1.5-2.8 KB.

Design choice: nested `CLAUDE.md` files were chosen over a `docs/claude/*` dump for rules because they load automatically exactly when relevant, while architecture (rarely needed) stays an on-demand file linked from the root.

Not denied on purpose: `docs/archive/**` (user may legitimately ask about history; the root file and docs index already tell agents to skip it), `CHANGELOG.md` (release flow edits it), `pnpm-lock.yaml` (dependency work in progress by another agent).

## Recommended follow-ups (need user decision)

- Move `V2_MIGRATION_STATUS.md` (11 KB, completed migration) to `docs/archive/v2-unified-model/`; it is referenced by `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/plans/README.md`, `docs/plans/UNIFIED_MODEL_IMPLEMENTATION_PLAN.md` and several archive files, so links must be updated.
- Mark/move finished phase reports: `docs/deployment/PHASE-6-COMPLETION.md`, `PHASE-6-QUICK-START.md`, `docs/plans/PHASE-5-COMPLETION-SUMMARY.md`, `docs/testing/MIGRATION_V2_TESTING_REPORT.md`; review `docs/plans/` (30+ files, many likely done) and set statuses in `plans/README.md`.
- Refresh `docs/ROADMAP_OFFLINE.md` (localStorage-only framing is outdated) and `FEATURES.md` / `README.md` (22 KB, 21 KB) for the same V2/backend reality; consider trimming `README.md` duplicates.
- Consider splitting `CHANGELOG.md` (132 KB) into per-year files, keeping the latest in root, and updating `.claude/commands/release-version.md` accordingly.
- Decide whether to add `Read(./docs/archive/**)` to deny rules if agents keep wandering in.
- Mirror the architecture/state-persistence correction into ops-monitor's CLAUDE.md if it shares the stale text (outside this repo; not touched).
- Parent `CLAUDE.md` files (`/home/madeyskij/projects/CLAUDE.md`, `~/.claude/CLAUDE.md`) also load here; not edited.
