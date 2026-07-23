# Backend gear V1/V2 model duality — item-image ownership/visibility checks broken for V2-native items

**Status:** `in progress`
**Created:** 2026-07-23
**Severity:** High
**Module:** `gear` (backend — data model / item images)
**Source:** Manual verification of [#035](2026-07-21--035--item-image-idor.md) by the user
**Plan:** [docs/plans/2026-07-23-gear-backend-v1-v2-unification.md](../plans/2026-07-23-gear-backend-v1-v2-unification.md)

## Problem

The backend still runs **two parallel gear data models**, even though the frontend V1→V2
migration was declared complete on 2026-06-13 (see
[`docs/archive/v2-unified-model/migration-v1-to-v2.md`](../archive/v2-unified-model/migration-v1-to-v2.md)):

- **V1** — tables `gear_containers` / `gear_items` (`backend/app/modules/gear/db_models.py`),
  written via `backend/app/modules/gear/repository.py`. Still actively used by ~41 endpoints in
  `router.py`: public container browsing (`/gear/public/containers*`), ratings, reports,
  promotions, share tokens, and — critically — the entire item-image feature
  (`item_image_router.py` / `item_image_repository.py` / `image_upload_service.py`, added in
  [#035](2026-07-21--035--item-image-idor.md)).
- **V2** — single table `gear_items_v2` (`db_models_v2.py`, `GearItemDBV2` /
  `GearContainerDBV2` via `item_type`), written via `repository_v2.py`. This is what the current
  authenticated UI (`/gear/:id`) actually renders and mutates today (per the V1/V2 gotcha in
  `CLAUDE.md`).

**There is no bridge between them.** `repository_v2.py` never writes to `gear_containers` /
`gear_items`, so any container or item created through today's normal UI exists **only** in
`gear_items_v2`.

The item-image ownership/visibility check added in #035
(`ItemImageRepository.get_item_owner_and_visibility`, `item_image_repository.py:187-213`) joins
exclusively against the **V1** tables:

```python
select(GearContainerDB.user_id, GearContainerDB.is_public, GearContainerDB.is_hidden_by_reports)
    .join(GearItemDB, GearItemDB.container_id == GearContainerDB.id)
    .where(GearItemDB.id == item_id)
```

and `item_images.item_id` has an FK to `gear_items.id` (V1), not `gear_items_v2.id`. The same
V1-only lookup backs `_verify_item_ownership()`, used by `upload_image`, `validate_upload`,
`delete_image`, `reorder_images`, and `toggle_primary_image`.

## Impact

For any container/item that only exists in V2 (i.e. anything created or edited through today's
normal app) — confirmed live on prod by the user during #035 verification:

- `GET /api/gear/items/{item_id}/images` returns `404 Item not found` **even when the container
  is marked public**, because toggling "public" in the UI updates `gear_items_v2.is_public`,
  which the V1-only join never sees.
- By the same mechanism, `upload_image` / `delete_image` / `reorder_images` /
  `toggle_primary_image` also 404 for V2-native items, since `_verify_item_ownership` uses the
  same broken lookup. The entire item-image feature appears to be non-functional for any item
  created after the frontend's V2 cutover — not just a visibility edge case.
- Only pre-migration items that still happen to have a matching row in the legacy V1 tables
  behave correctly, which is why some containers looked fine during testing and others didn't.

This is the concrete case that surfaced the problem; the same V1/V2 split likely affects the
other V1-only endpoints listed above (ratings, reports, promotions, public browsing) whenever
they're asked about a V2-native container/item — not yet individually verified.

## Reproduction

1. Log in, create/open a container via the normal `/gear/:id` UI (V2-backed) — e.g. "Bagażnik".
2. Mark it public.
3. As a guest, `GET /api/gear/items/{item_id}/images` for one of its items → `404 Item not
   found`, regardless of the public toggle.
4. Compare with a pre-migration container (e.g. one reachable via `/gear/public/containers/...`
   browsing) — the same call works correctly, because it still has a matching V1 row.

## User request — stop patching around the duality

> Chcę pozbyć się tego śmietnika z dwoistością, chcę mieć spójnie wszędzie tylko V2, aby więcej
> nie było takich głupich konfliktów. To miało być zrobione miesiąc temu.

The frontend migration doc marks V1 "usunięte" (removed) as of 2026-06-13, but the **backend**
V1 tables, repository, and ~41 router endpoints are still live and are the actual source of
truth for several features (item images, public browsing, ratings/reports/promotions). The ask
is to finish the migration on the backend too — one model (V2) everywhere — rather than
special-casing or re-patching the V1 join every time a feature like this trips over it.

## Proposed fix

Two possible directions — needs scoping before starting:

1. **Finish the backend migration to V2 everywhere** (matches the explicit ask above): port the
   remaining V1-only backend features (item images, public container browsing, ratings, reports,
   promotions, share tokens) onto `gear_items_v2`, migrate/backfill any legacy rows, then drop
   `gear_containers` / `gear_items` and all of `db_models.py` / `repository.py` / `router.py`'s
   V1 surface. `item_images.item_id` FK moves to `gear_items_v2.id`.
2. Minimal patch (not preferred per the user's ask, but noted for completeness): make
   `item_image_repository.py` look up ownership/visibility against `gear_items_v2` (falling back
   to V1 only for pre-migration data) — fixes this one symptom without addressing the underlying
   duality, so the same class of bug will resurface in the next V1-only feature that gets touched.

Given the explicit request, direction 1 is the intended fix; this issue should stay `todo` until
that's scoped into a plan (likely belongs in `docs/plans/`, given the size).

## Scope

- [ ] Scope a plan for full backend V1 → V2 migration (tables, repository, router endpoints,
  FKs) — see `docs/plans/README.md`
- [ ] Migrate/backfill legacy `gear_containers` / `gear_items` rows into `gear_items_v2`
- [ ] Re-point item-image feature at V2 (`item_images.item_id` FK, ownership/visibility joins)
- [ ] Re-point public container browsing, ratings, reports, promotions, share tokens at V2
- [ ] Remove `db_models.py` (V1), `repository.py` (V1), V1 endpoints in `router.py`
- [ ] Re-verify [#035](2026-07-21--035--item-image-idor.md) end-to-end once item images run on V2

## Production DB recon (2026-07-23)

Before scoping the migration plan, checked actual schema state on both the local dev DB and
production (VPS, `gear-stack-db`). This corrects and extends the analysis above.

**Migrations 050–054 (create `gear_items_v2`, migrate data, repoint FKs) are applied on both
dev and prod** (`schema_migrations`, prod `applied_at` 2026-01-08). But the two environments
diverge in an important way:

| | dev (local) | production |
|---|---|---|
| `gear_containers` rows | 0 | 20 |
| `gear_items` rows | 0 | 143 |
| `gear_items_v2` rows | 9 | 165 |

**On production, V1 tables are NOT empty** — migration `051_migrate_data_to_unified_model`
*copied* V1 rows into `gear_items_v2` but never deleted the originals. 20 + 143 = 163, vs. 165
in `gear_items_v2` — **at least 2 rows exist only in V2** (created after the app's cutover to
V2, with no V1 counterpart), which is itself proof that any "V1 is still the source of truth"
framing is wrong going forward — V1 is now a stale, partially-diverged copy, not a live twin.

**FK state is worse than originally described** — the original "Problem" section above says
`item_images.item_id` has an FK to `gear_items.id`. On production it actually has **two FK
constraints on the same column simultaneously**:
- `fk_item_images_item_id → gear_items` (old, V1)
- `item_images_item_id_fkey → gear_items_v2` (new, added by migration 052)

Same double-FK pattern on `container_ratings.container_id`. Root cause: migration 052 ran
`DROP CONSTRAINT IF EXISTS item_images_item_id_fkey` / `..._container_ratings_container_id_fkey`
to remove the old FK before adding the new one — but the *actual* old constraint names in
production were `fk_item_images_item_id` / `fk_container_ratings_container` (different naming
convention, likely from an earlier hand-written migration). `DROP CONSTRAINT IF EXISTS` with the
wrong name silently no-ops, so the old FK was never dropped — both now co-exist on the same
column.

**Practical consequence:** because both FKs are enforced, `item_images.item_id` /
`container_ratings.container_id` must currently satisfy *both* — the referenced row must exist
in **both** `gear_items` (V1) and `gear_items_v2` (V2). Any of the ≥2 V2-only items (created
post-cutover, no V1 row) would hit an **FK constraint violation** (not just the ownership-check
404 described above) if an image or rating were attempted for them — a second, more severe bug
than the app-level 404, currently masked because the broken V1-only ownership check 404s first
and the code never reaches the INSERT.

**`item_promotions` and `content_reports` were never repointed at all** — migration 052 only
touched `item_images`, `container_share_tokens`, and `container_ratings`. On production:
- `item_promotions.item_id` → still only `gear_items` (V1), 0 rows
- `content_reports.container_id` → still only `gear_containers` (V1), 0 rows

**`container_share_tokens` does not exist on production at all**, despite migrations that
create it being recorded as applied — filed separately as
[#044](2026-07-23--044--container-share-tokens-table-missing-prod.md) since it's an independent
anomaly (live 500s, not part of the V1/V2 duality itself), but it also means the recorded-applied
state in `schema_migrations` can't be fully trusted when scoping the fix below.

**Revised understanding for the plan:** this is no longer "finish a migration that still needs a
data backfill" — the data copy already happened. What's actually needed:
1. Reconcile the ≥2 V2-only rows and confirm `gear_items_v2` is a complete, correct superset of
   the 163 V1 rows (no silent field-mapping loss from migration 051) before anything is dropped.
2. Drop the *actual* old FK constraints by their real names (`fk_item_images_item_id`,
   `fk_container_ratings_container`, ...) — don't trust migration 052's constraint names.
3. Add the missing new FKs for `item_promotions` and `content_reports` → `gear_items_v2`.
4. Re-point the ownership/visibility/read code (`item_image_repository.py`, ratings, reports,
   promotions, public browsing, share tokens) at V2 — the part originally scoped above.
5. Only then, once V2 is verified authoritative and nothing references V1 anymore, drop
   `gear_containers` / `gear_items` and the dead V1 code.
6. Spot-check whether other `schema_migrations`-recorded migrations have similar drift, given
   `container_share_tokens` was found to silently not match its recorded state.

## Verification

Blocked on the fix above. Once done: repeat the #035 verification steps (owner/cross-user
access, public/private visibility) against V2-native containers and items, plus a regression
pass on public browsing, ratings, reports, and promotions. Also verify the FK cleanup directly
against production's actual constraint names, not just dev.

## Code repointing landed (2026-07-23, not yet deployed to production)

Phases 0-3 of [the plan](../plans/2026-07-23-gear-backend-v1-v2-unification.md) are done and
verified against a local restored copy of the production backup: item-image ownership/visibility
(the original symptom here), public browsing, ratings, reports (incl. auto-hide), promotions, and
the catalogue-linking subsystem (not originally in scope — found broken by the same root cause
while tracing real call paths) all now correctly resolve V2-native containers/items instead of
404ing or silently no-op'ing. `stats`/`admin` modules (also not originally in scope, found via
direct grep for `GearContainerDB`/`GearItemDB` usage) were repointed too, since they'd otherwise
500 once Phase 5 drops the V1 tables. Phase 4 (dead V1 CRUD endpoints/methods/tests/frontend
service methods — zero real callers, confirmed) also done. Full backend test suite green
throughout (`ruff`/`black`/`mypy` clean; `pnpm type-check`/`pnpm lint` clean), all local/dev-only
so far. **Still open:** deploy migrations `057`/`058` + all this code to production and verify
end-to-end there, then Phase 5 (drop V1 tables, remove the ORM classes) — issue stays
`in progress` until production is verified.

## Deployed and verified on production (2026-07-23)

Migrations `057`/`058` deployed; backend restarted. Output matched the local dry run exactly
(same FKs dropped/added, same "already correct, nothing to add" results, zero orphan-row
failures). User confirmed on production: item images load correctly, container sharing works,
and ratings/reports/promotions are functional — the original #043 symptom (and everything else
repointed in Phases 3a-3d) is fixed end-to-end, not just in local testing.

**Remaining:** Phase 5 (drop `gear_containers`/`gear_items`, remove the V1 ORM classes) — this
is the last step of the user's original ask to eliminate the V1/V2 duality entirely, so this
issue stays `in progress` until that lands. Take a fresh production backup immediately before
running migration `059`.
