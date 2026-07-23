# Backend V1→V2 Gear Model Unification — Phased Implementation Plan

**Status:** `in progress` — Phases 0-4 executed and deployed to production 2026-07-23 (migrations
057/058 live, user-verified: item images, sharing, ratings/reports/promotions all working);
Phase 5 (drop V1 tables) remaining
**Created:** 2026-07-23
**Drives:** [docs/issues/2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md](../issues/2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md), [docs/issues/2026-07-23--044--container-share-tokens-table-missing-prod.md](../issues/2026-07-23--044--container-share-tokens-table-missing-prod.md)
**Supersedes the open TODOs in:** [UNIFIED_MODEL_IMPLEMENTATION_PLAN.md](UNIFIED_MODEL_IMPLEMENTATION_PLAN.md) ("❌ Backend routing: V2 API exists but isn't default", "❌ Cleanup V1: old tables/models still exist")
**Context:** frontend V1→V2 migration is already complete ([migration-v1-to-v2.md](../archive/v2-unified-model/migration-v1-to-v2.md), done 2026-06-13). This plan finishes the matching backend work: eliminate the legacy V1 gear data model (`gear_containers`, `gear_items`) and make `gear_items_v2` the sole backend source of truth.

Single-user production app (the user is the only user) — real personal data (163+ items on
production), backup available, one branch/staging-phase process is fine, but the data itself
must be handled carefully. All phases below are designed to be independently shippable with no
window where an endpoint 500s or data is silently lost.

## Key discoveries that refine the two issues above

1. **`router.py` is NOT "41 dead V1 endpoints."** Only ~16 (container CRUD, item CRUD,
   batch-order, stats) duplicate `router_v2.py`. The other ~25 (public browsing, ratings,
   reports, promotions, share tokens, `/catalogue/*`, `/me/limits`, the included
   `item_image_router`) have **no V2 equivalent** and are live, frontend-facing. `repository.py`
   / `service.py` / `router.py` **cannot be deleted wholesale** — most must be **repointed** to
   `gear_items_v2`, not removed.

2. **The frontend V1 container-CRUD/stats calls are already dead.**
   `gearContainerApiService.ts` still *defines* `createContainer/getContainers/getContainer/
   updateContainer/deleteContainer/deleteAllContainers/getContainerWeight/getContainerReadiness`,
   but grep shows **0 callers** anywhere in `src/` outside the file itself. Its only live methods
   are `rateContainer`, `deleteContainerRating`, `reportPublicContainer`, `withdrawReport`,
   `getReportStatus`. The dead CRUD/stats methods can be deleted with zero frontend impact; the
   file itself stays as the ratings/reports client (it is not fully removable).

3. **Two modules outside `gear/` read the V1 tables directly — not mentioned in either issue,
   and will hard-break on `DROP TABLE`:**
   - `app/modules/stats/router.py` (lines 11, 73–108) — `count(GearContainerDB.id)` /
     `GearItemDB.id` backing live `/stats/containers`, `/stats/items`.
   - `app/modules/admin/repository.py` (import line 14; `get_all_containers`,
     `get_container_by_id`, `update_container`, `get_all_items`, `get_item_by_id`) backing
     `/admin/containers`, `/admin/items`. Uses `selectinload(GearContainerDB.items)` /
     `joinedload(GearContainerDB.user)` — needs a real rewrite to V2's shape.

   Any plan that drops `gear_containers`/`gear_items` without repointing these two modules will
   500 the stats and admin pages. Explicit tasks in Phase 3.

4. **Dev DB diverges from prod exactly as #043 warned — confirmed by direct query:**

   | table.column | dev refs | prod refs (per #043 recon) |
   |---|---|---|
   | `item_images.item_id` | `gear_items_v2` (single, clean) | **double FK** → `gear_items` + `gear_items_v2` |
   | `container_ratings.container_id` | `gear_items_v2` (single, clean) | **double FK** → `gear_containers` + `gear_items_v2` |
   | `container_share_tokens.container_id` | `gear_items_v2` (table **exists** in dev) | **table missing** on prod |
   | `item_promotions.item_id` | `gear_items` (V1, un-migrated) | `gear_items` (V1, un-migrated) |
   | `content_reports.container_id` | `gear_containers` (V1, un-migrated) | `gear_containers` (V1, un-migrated) |

   The FK migration in Phase 2 must be **programmatic** (enumerate constraints by column via
   `pg_constraint`, drop any not referencing `gear_items_v2`, ensure one that does) — a
   hardcoded-name migration would be correct on neither environment and would repeat the exact
   `052` bug. It must also be a no-op where already correct (dev's `item_images`/`ratings`).

5. **`db_models.py` cannot be deleted wholesale.** It also defines `ItemImageDB`,
   `ContainerShareTokenDB`, `ContainerRatingDB`, `ItemPromotionDB`, `ContentReportDB`,
   `GlobalCatalogueItemDB`, `CatalogueItemImageDB` — all of which survive. Only `GearContainerDB`
   and `GearItemDB` (and their ORM `relationship()` wiring on the surviving models) get removed.

6. **#044 recommendation: fold into this plan as the first migration (`057`), not a separate
   branch.** The share-tokens table must be recreated pointing at `gear_items_v2` — the exact
   target of this plan — so a standalone hotfix would duplicate the work. The user is on one
   staging branch, so a separate branch buys nothing. The migration is self-contained enough to
   ship and verify on its own *before* the rest of the sequence, satisfying "independently
   shippable." **Land it first.**

**Migration numbering:** last existing is `056`. New migrations: **057, 058, 059**. Runner is
`app/core/migrations.py` (`discover_migrations()` sorts by numeric prefix, runs `upgrade()`,
records into `schema_migrations`). Follow the `050`/`052` style exactly: `table_exists()` /
`constraint_exists()` helpers, `async with engine.begin()`, `sys.exit(1)` on unsafe state,
idempotent `upgrade()`/`downgrade()`.

---

## Phase 0 — Verify V2 is an authoritative superset (read-only, no code)

**Goal:** prove `gear_items_v2` completely and field-accurately contains the 163 V1 rows, and
enumerate the ≥2 V2-only rows, before anything is dropped or repointed.

Run against a **restored copy of the prod backup**, then prod read-only — never write:

1. Confirm the DB backup exists and is restorable (don't assume — verify).
2. Reconciliation queries (all must return **0 rows** except the last):

```sql
-- (a) V1 containers missing from V2
SELECT c.id FROM gear_containers c
  LEFT JOIN gear_items_v2 v ON v.id=c.id AND v.item_type='container'
  WHERE v.id IS NULL;
-- (b) V1 items missing from V2
SELECT i.id FROM gear_items i
  LEFT JOIN gear_items_v2 v ON v.id=i.id AND v.item_type='item'
  WHERE v.id IS NULL;
-- (c) container field drift (mirrors migration 051 mapping)
SELECT c.id FROM gear_containers c JOIN gear_items_v2 v ON v.id=c.id
  WHERE c.name           IS DISTINCT FROM v.name
     OR c.user_id        IS DISTINCT FROM v.user_id
     OR c.type           IS DISTINCT FROM v.container_type
     OR c.is_public      IS DISTINCT FROM v.is_public
     OR c.parent_container_id IS DISTINCT FROM v.parent_item_id
     OR COALESCE(c.price,-1)  IS DISTINCT FROM COALESCE(v.price,-1)
     OR COALESCE(c.weight,-1) IS DISTINCT FROM COALESCE(v.weight,-1);
-- (d) item field drift
SELECT i.id FROM gear_items i JOIN gear_items_v2 v ON v.id=i.id
  WHERE i.name         IS DISTINCT FROM v.name
     OR i.container_id IS DISTINCT FROM v.parent_item_id
     OR i.category     IS DISTINCT FROM v.category
     OR i."order"      IS DISTINCT FROM v.order_index
     OR i.catalogue_item_id IS DISTINCT FROM v.catalogue_item_id;
-- (e) the >=2 V2-only (post-cutover) rows -- inspect & keep, must NOT be lost
SELECT v.id, v.item_type, v.name, v.created_at FROM gear_items_v2 v
  WHERE NOT EXISTS (SELECT 1 FROM gear_containers c WHERE c.id=v.id)
    AND NOT EXISTS (SELECT 1 FROM gear_items i WHERE i.id=v.id);
```

3. Snapshot prod's **actual** FK constraint names/targets (audit trail for Phase 2):

```sql
SELECT tc.table_name, tc.constraint_name, kcu.column_name, ccu.table_name AS refs
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name
  JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name=ccu.constraint_name
  WHERE tc.constraint_type='FOREIGN KEY'
    AND tc.table_name IN ('item_images','container_ratings','container_share_tokens','item_promotions','content_reports');
```

4. Spot-check other `schema_migrations`-recorded tables exist physically (the #044 lesson):
   assert `container_share_tokens` absent, and quickly confirm 3–4 other recently-recorded
   migrations' tables/columns exist.

**Exit criteria:** queries (a)–(d) return 0 rows; the V2-only rows in (e) are understood and
intentional; backup verified restorable; prod constraint names recorded. **If (a)–(d) are
non-empty, STOP** — author a corrective backfill migration before proceeding.

**Rollback:** none (read-only).

### Phase 0 — executed 2026-07-23 (production backup `.backups/gear-stack-postgres-20260722-130903.sql.gz` restored into local `gear-stack-db`/`backend`, replacing the dev dataset)

Results: (a) 0, (b) 0 — no V1 rows missing from V2. (c) 1, (d) 2 — investigated individually,
all three are **explained by expected post-cutover staleness of V1, not data loss or a migration
bug**:
- Container "Płaszcz": V1 `is_public=true` vs V2 `is_public=false` — unpublished via the app
  after cutover; only V2 was updated (the exact mechanism behind #043).
- Item "Anker PowerCore 20100" (V1 name) renamed to "Anker Zolo 20K 45W" in V2 — post-cutover
  rename, V1 never caught up.
- Item "Latarka Olight i3T 2 EOS": V1 `order=1` vs V2 `order_index=NULL` — same pattern, lowest
  stakes (display order only).

In every case V2 holds the newer/correct value and V1 the stale one — confirms V2 is
authoritative and the plan's premise (V1 is a frozen, diverging copy, not a live twin) holds.
**No corrective backfill needed; proceed.**

(e) confirmed 2 V2-only rows ("Maseczka", "Igła do strzykawki", both created 2026-07-04, after
cutover) — intentional, not orphans.

FK snapshot on the restored copy **exactly matches** the production recon in #043/#044: double
FK on `item_images.item_id` (`fk_item_images_item_id → gear_items` + `item_images_item_id_fkey →
gear_items_v2`) and `container_ratings.container_id` (`fk_container_ratings_container →
gear_containers` + `container_ratings_container_id_fkey → gear_items_v2`); `item_promotions` and
`content_reports` still single-FK to V1 only; `container_share_tokens` absent. This local
restored copy is now a faithful stand-in for production and will be used to test migrations
`057`–`059` before they ever touch the real server.

**User decisions (2026-07-23):** no bake/soak period between Phase 4 and Phase 5 — proceed
directly to Phase 5 once Phase 4's verification passes. `stats`/`admin` repointing (3c/3d) stays
in this same plan, not split out.

---

## Phase 1 — Recreate `container_share_tokens` on prod (fixes #044)

**Goal:** stop the live 500s and give the table an FK to `gear_items_v2`. Independently
shippable.

**New migration:** `migrations/057_recreate_container_share_tokens.py`
- `upgrade()`: `if not table_exists(conn,'container_share_tokens')`: `CREATE TABLE
  container_share_tokens (...)` matching `ContainerShareTokenDB` in `db_models.py` (id,
  container_id, user_id, token, expires_at, created_at), with `container_id` FK →
  `gear_items_v2(id) ON DELETE CASCADE` and `user_id` FK → `users(id)`. Idempotent — no-op on dev
  (table already exists there).
- `downgrade()`: `DROP TABLE IF EXISTS container_share_tokens`.

**Files:** only the new migration. No app code change (ORM model `ContainerShareTokenDB` and
repository/router already reference it).

**Verify before:** Phase 0 done. **Verify after:** on the restored-backup copy, hit all four
share-token endpoints (`GET/POST/DELETE /gear/containers/{id}/share-tokens`,
`GET /gear/shared/containers/{token}`) — no 500. Confirm `schema_migrations` now records 057.

**Tests:** add `backend/tests/integration/gear/test_share_tokens.py` exercising create/list/
revoke against a V2 container fixture — currently none exists.

**Rollback:** run `057 downgrade`, or restore backup. Low risk (creating a missing table).

### Phase 1 — executed 2026-07-23

`migrations/057_recreate_container_share_tokens.py` written and applied via `python -m cli db
migrate` against the local restored-production copy (Phase 0 environment). Idempotent re-run
confirmed as a no-op. Table now exists with `container_id FK -> gear_items_v2(id)`.

**Deviation from the original phase split, discovered while testing:** the integration test
suite's `backend_test` database is built from `Base.metadata.create_all()` (SQLAlchemy ORM
metadata), **not** from the raw-SQL migrations — so `ContainerShareTokenDB.container_id`'s
Python-level `ForeignKey("gear_containers.id")` declaration in `db_models.py` was what actually
governed the test DB's schema, regardless of migration 057. Testing `create_share_token` against
a V2-only container immediately hit a real `ForeignKeyViolationError` in the test DB (correctly
pointing at `gear_containers`, not yet fixed) even though the migrated dev/prod-copy DB was
already correct. Fixed by updating `db_models.py` now rather than deferring to Phase 3e:
- `ContainerShareTokenDB.container_id`: `ForeignKey("gear_containers.id")` →
  `ForeignKey("gear_items_v2.id")`
- `ContainerShareTokenDB.container` relationship: retargeted from `"GearContainerDB"` to
  `"GearItemDBV2"` (required — `foreign_keys=[...]` pointing at a column whose FK no longer
  targets `GearContainerDB`'s table would fail SQLAlchemy mapper configuration otherwise)

This relationship/FK-annotation fix was unused by any query (`ContainerShareTokenDB.container`
had zero callers — all lookups do explicit joins), so it was a safe, isolated change. **Note for
Phase 3e:** this table's ORM hygiene is now done; the remaining relationship cleanup there is for
`item_images`, `container_ratings`, `item_promotions`, `content_reports`, and the
`GearContainerDB`/`GearItemDB` back-refs only.

`tests/integration/gear/test_share_tokens.py` added: 3 tests — create and revoke against a
V2-only container fixture (pass, confirming the #044 fix), plus one deliberately documenting the
still-open Phase 3 gap (`get_share_tokens_by_container` returns `[]` for V2-only containers
because its ownership check still queries V1 `GearContainerDB` — must be updated to assert
non-empty once Phase 3 lands). Full `tests/integration/gear/` suite re-run: **135 passed**, no
regressions. `black`/`mypy` clean on changed files.

---

## Phase 2 — Reconcile all ancillary FKs to `gear_items_v2` (programmatic)

**Goal:** eliminate prod's double-FKs on `item_images`/`container_ratings`, and migrate the still
-V1 `item_promotions`/`content_reports` FKs — all **without hardcoding constraint names**.
Idempotent, correct on both dev and prod.

**New migration:** `migrations/058_reconcile_gear_v2_foreign_keys.py`
- Helper `fk_constraints_on_column(conn, table, column) -> list[(constraint_name,
  referenced_table)]` querying `pg_constraint` joined to `pg_attribute`/`pg_class` (or
  `information_schema.key_column_usage` + `constraint_column_usage`) — resolves the **real**
  names present in *this* database.
- For each `(table, column)` in:
  - `('item_images','item_id')`
  - `('container_ratings','container_id')`
  - `('container_share_tokens','container_id')` (belt-and-suspenders; already correct post-057)
  - `('item_promotions','item_id')`
  - `('content_reports','container_id')`

  do: (1) `if not table_exists`: skip; (2) look up all FK constraints on the column; (3)
  `DROP CONSTRAINT` **by their actual discovered names** for any whose referenced table ≠
  `gear_items_v2`; (4) if none now references `gear_items_v2`, `ADD CONSTRAINT ... FOREIGN KEY
  (col) REFERENCES gear_items_v2(id) ON DELETE CASCADE`. This drops prod's stale
  `fk_item_images_item_id` / `fk_container_ratings_container` by their real names, adds the
  missing `gear_items_v2` FK for promotions/reports, and no-ops on dev (already single-and
  -correct).
- **Pre-flight safety** inside `upgrade()` before adding a new FK: assert no orphan rows would
  violate it, e.g. `SELECT count(*) FROM item_promotions p LEFT JOIN gear_items_v2 v ON
  v.id=p.item_id WHERE v.id IS NULL` (and same for content_reports/container_id). If >0,
  `sys.exit(1)` with a clear message rather than crash mid-`ALTER`. (Both are 0 rows on prod
  today per #043, but verify — don't trust.)
- `downgrade()`: drop the `gear_items_v2` FK on promotions/reports and re-add to
  `gear_items`/`gear_containers` **only if those tables still exist**; do **not** attempt to
  reconstruct prod's buggy double-FK. Note in the docstring that true rollback is the Phase 0
  backup.

**Files:** only the new migration.

**Verify before:** 057 applied. **Verify after:** re-run the Phase-0 constraint snapshot query —
every target column now has **exactly one** FK → `gear_items_v2`, and **zero** FKs remain to
`gear_items`/`gear_containers` from these five tables. On the restored-backup copy, insert an
image/rating/promotion/report for one of the **V2-only** items from Phase 0(e) — it must now
succeed (previously would hit the FK-violation described in #043).

**Tests:** extend `test_migration_integrity.py` with an assertion that these five columns
reference `gear_items_v2` and nothing else (query `information_schema`). This test is the guard
against a future `052`-style regression.

**Rollback:** `058 downgrade` or backup restore.

### Phase 2 — executed 2026-07-23

`migrations/058_reconcile_gear_v2_foreign_keys.py` written and applied against the local
restored-production copy. Confirmed exactly the expected behavior: dropped the two stale FKs
(`fk_item_images_item_id → gear_items`, `fk_container_ratings_container → gear_containers`) by
their real discovered names, left the existing correct `gear_items_v2` FKs on those two columns
untouched, added the two missing FKs (`item_promotions.item_id`, `content_reports.container_id`
→ `gear_items_v2`), and confirmed `container_share_tokens` already correct (no-op). Re-run is a
full no-op (idempotent). Post-migration snapshot: all five columns now have **exactly one** FK,
to `gear_items_v2` — zero remaining references to `gear_containers`/`gear_items` from these
tables. Orphan pre-flight found 0 orphans for `item_promotions`/`content_reports`, matching #043.

Added `test_container_share_tokens_fk_only_gear_items_v2` to `test_migration_integrity.py` —
scoped to just `container_share_tokens` rather than all five columns, because `backend_test`
(the integration test database) is built from `Base.metadata.create_all()` (i.e. from the ORM
model declarations in `db_models.py`), not from these raw-SQL migrations. Only
`ContainerShareTokenDB` has had its ORM `ForeignKey`/`relationship` updated so far (Phase 1); the
other four models (`ItemImageDB`, `ContainerRatingDB`, `ItemPromotionDB`, `ContentReportDB`)
still declare V1-pointing relationships on purpose — `GearContainerDB.items`, for example, is
actively used throughout the still-live V1 repository methods (`selectinload(GearContainerDB.items)`
appears 7+ times in `repository.py`), so repointing it now would be a Phase 3/3e change, not a
Phase 2 one. The remaining four columns' FK-only-gear_items_v2 assertions should be added to this
test once Phase 3e updates their ORM declarations to match.

Full `tests/integration/gear/` suite: **136 passed**, 0 failures (confirmed via a clean, single
run — an earlier run produced a scary-looking batch of `ERROR`s that turned out to be a
concurrency artifact from two overlapping pytest invocations racing against the same
non-isolated `backend_test` database, not a real regression). `black`/`mypy` clean (migrations/
is excluded from mypy per `pyproject.toml`, consistent with all prior migration files).

---

## Phase 3 — Repoint all read/ownership/write code to `gear_items_v2` (no schema change, contracts stable)

**Goal:** make every surviving endpoint read/write `gear_items_v2` while keeping REST paths and
response schemas byte-identical, so all live frontend consumers need zero changes. This is the
largest phase; split into independently testable sub-steps. **No `DROP` anywhere in this phase**
— V1 tables remain as a fallback safety net until Phase 5.

**3a. Item images (the original #043/#035 symptom).**
- `app/modules/gear/item_image_repository.py`: rewrite `get_item_owner_and_visibility`,
  `get_item_owner_id`, `get_image_owner_id` to use `GearItemDBV2` (import from `db_models_v2`).
  Ownership = the item row's own `user_id`; visibility = self-join to parent container:
  `SELECT item.user_id, parent.is_public, parent.is_hidden_by_reports FROM gear_items_v2 item
  JOIN gear_items_v2 parent ON item.parent_item_id = parent.id WHERE item.id = :item_id`. Keep
  the same return tuple shape so callers (`_verify_item_ownership` in `image_upload_service.py`,
  `item_image_router.py`) are untouched.
- `image_upload_service.py`: audit any residual `GearItemDB` lookups and swap to V2.

**3b. Public browsing / ratings / reports / promotions / share tokens (`repository.py` +
`service.py`).**
- `repository.py`: rewrite the retained methods to query `GearItemDBV2` with `item_type` filters
  instead of `GearContainerDB`/`GearItemDB`. Concretely: `get_public_containers`,
  `get_public_container`, `get_public_container_for_reporting` (filter `item_type='container'`,
  `is_public=True`, `is_hidden_by_reports` handling); rating methods
  `get/upsert/delete_container_rating`, `get_container_average_user_rating`,
  `get_container_owner_rating`, `get_container_user_rating_count`,
  `get_container_ratings_data`; promotion methods `get_promotion_by_item_and_user`,
  `create_promotion`, `get_promotions_by_item`; share-token methods `create_share_token`,
  `get_container_by_token`, `get_share_tokens_by_container`, `revoke_share_token`; report methods
  `create_container_report`, `get_reports_for_container`,
  `count_active_reports_for_container`, `set_container_hidden_by_reports` (now updates
  `gear_items_v2.is_hidden_by_reports`), `get_report_by_container_and_user`, `delete_report`,
  `get_all_reports`, `update_report_status`; and `count_user_containers`/`count_user_items` for
  `/me/limits`.
- `service.py`: `_map_container_to_response`, `_map_container_to_response_with_author`,
  `_map_item_to_response` currently take `GearContainerDB`/`GearItemDB`. Repoint to accept
  `GearItemDBV2` and map field-name differences (`container_type`→`type`, `order_index`→`order`,
  `parent_item_id`→`parentContainerId`/`container_id`). A mapper likely already exists in
  `service_v2.py`/`schemas_v2.py` — reuse it rather than duplicating. `get_public_container` must
  also fetch child items (V2 `children` / a `parent_item_id` query) to populate
  `ContainerResponse.items`.
- Response schemas in `schemas.py` (`ContainerResponse`, `ItemResponse`, `ShareTokenResponse`,
  `ContentReportResponse`, etc.) stay **unchanged** — only the data source under them changes.

**3c. Stats module (newly discovered).**
- `app/modules/stats/router.py` lines 11, 73–108: replace `count(GearContainerDB.id)` →
  `count(GearItemDBV2.id) WHERE item_type='container'`, and `count(GearItemDB.id)` → `... WHERE
  item_type='item'`. Same for the `created_at >= month_start` variants.

**3d. Admin module (newly discovered).**
- `app/modules/admin/repository.py` (import line 14; methods `get_all_containers`,
  `get_container_by_id`, `update_container`, `get_all_items`, `get_item_by_id`): rewrite onto
  `GearItemDBV2`. Replace `selectinload(GearContainerDB.items)` with a `parent_item_id`-based
  children query and `joinedload(GearContainerDB.user)` with the V2 `user` relationship.
  `app/modules/admin/service.py` mapping methods (`get_all_containers` @238,
  `get_container_by_id` @273, `update_container` @305, `get_all_items` @366, `get_item_by_id`
  @401) adjust to the V2 field names but keep `AdminContainerResponse`/`AdminItemResponse`
  output shape stable so `/admin/*` frontend is unaffected.

**3e. ORM relationship hygiene.** In `db_models.py`, the surviving ancillary models still
declare relationships to V1 (`ItemImageDB.item`→`GearItemDB`, `ContainerShareTokenDB.container`→
`GearContainerDB`, `ContainerRatingDB.container`→`GearContainerDB`, and the
`GearItemDB.images`/`GearContainerDB.items`/`.ratings` back-refs). These are only needed if code
navigates them; since 3a–3d move to explicit joins, drop or repoint these `relationship()` lines
to `GearItemDBV2` in this phase so they don't error when V1 classes are removed in Phase 5.
(Prefer removing unused ones outright.)

**Files touched:** `item_image_repository.py`, `image_upload_service.py`, `repository.py`,
`service.py`, `stats/router.py`, `admin/repository.py`, `admin/service.py`, `db_models.py`
(relationships only). No migration, no frontend change.

### Phase 3a — executed 2026-07-23

`item_image_repository.py` rewritten: `get_item_owner_and_visibility` now selects the item's own
`user_id` from `gear_items_v2` (V2 items carry `user_id` directly, unlike V1 where only
containers did) and self-joins to the immediate parent row for `is_public`/`is_hidden_by_reports`
(`aliased(GearItemDBV2)`); `get_image_owner_id` now joins `item_images` -> `gear_items_v2`
directly (no more 3-table V1 join). `image_upload_service.py` needed **no changes** -- it only
calls the repository methods above. Import cleanup: dropped `GearContainerDB`/`GearItemDB`
imports from `item_image_repository.py` entirely.

**Same ORM-annotation issue as Phase 1, recurring:** writing a real regression test (insert an
image for a V2-only item) immediately hit `ForeignKeyViolationError` against `backend_test`,
because `ItemImageDB.item_id` still declared `ForeignKey("gear_items.id")` (V1) in
`db_models.py` -- unrelated to my query-layer changes above, but blocking on testability the same
way `ContainerShareTokenDB` was in Phase 1. Fixed now rather than deferred: `item_id` FK
retargeted to `gear_items_v2.id`; the paired `ItemImageDB.item <-> GearItemDB.images`
`back_populates` relationship was deleted outright (confirmed zero navigational use anywhere in
the codebase via grep -- all lookups are explicit joins), rather than repointed, since keeping a
now-pointless one-way relationship added nothing.

**Adjustment to the plan, worth calling out:** this is the second time "just repoint the query
code, defer the ORM annotation to Phase 3e" turned out to be unworkable in practice, because the
integration test database (`backend_test`) is built from `Base.metadata.create_all()` --  i.e.
from the ORM declarations directly, with no raw-SQL migrations involved. **The revised rule going
forward: fix each ancillary table's ORM FK annotation (and any now-dead relationship pointing at
GearContainerDB/GearItemDB) in the same sub-step that repoints its query code**, not as a
separate deferred pass. This still isn't "Phase 3e in one shot" -- `GearContainerDB.items`
(used 7+ times in still-live V1 CRUD in `repository.py`) stays untouched until Phase 4 removes
that V1 CRUD surface; only the *specific* relationship tied to the table being repointed in each
sub-step gets fixed, in lockstep.

Test changes: added `create_test_container_v2`/`create_test_item_v2` helpers to `conftest.py`
(parallel to the existing V1 `create_test_container`/`create_test_item`, which stay unchanged --
`test_containers_crud.py`/`test_items_crud.py` intentionally still test V1 CRUD directly and must
keep doing so until Phase 4). Rewrote `test_item_images_authorization.py` entirely onto the V2
helpers (was building V1-only containers/items, which the newly-repointed repository can no
longer see at all) and added `test_get_item_images_v2_only_item_no_v1_counterpart` as the direct
regression test for #043's actual reported symptom.

Full `tests/integration/gear/` suite: **137 passed**, 0 failures (clean single run). `black`
clean; `python -m mypy .` (project-wide, per CLAUDE.md) clean, 206 source files.

**Verify before:** Phases 1–2 applied. **Verify after (re-verification of #035/#043):** on the
restored-backup copy, for a **V2-native** container (created post-cutover, in Phase-0(e) set):
`GET /gear/items/{id}/images` as guest returns images when the container is public and 404 when
private (previously always 404); upload/delete/reorder/toggle-primary work for the owner and 404
cross-user; public browsing, ratings, reports, promotions, share tokens, `/stats/*`, `/admin/*`
all return correct data for V2-native rows.

**Tests to update/add per sub-step:**
- `test_item_images_authorization.py` + `conftest.py`: the fixtures
  `create_test_container`/`create_test_item` currently build **V1** rows via `GearService`.
  Switch them to create `gear_items_v2` rows (via `GearServiceV2`) so these tests exercise the
  new ownership path. `conftest.py` helpers `get_container_count`/`get_item_count` (lines 15–24,
  using `GearContainerDB`/`GearItemDB`) must move to `GearItemDBV2` + `item_type`.
- `test_unified_model_v2.py`: extend to cover ratings/reports/promotions/share-tokens/public
  -browsing against V2 rows (new coverage — currently only core CRUD).
- `test_migration_integrity.py`, `test_nesting_relationships.py`: update the V1-model imports
  flagged by grep.
- Add stats/admin integration coverage asserting counts and listings come from `gear_items_v2`.

**Rollback:** revert the code diff (git). Because no schema changed and V1 tables still exist,
reverting fully restores prior behavior. This is the phase's safety property — repoint reads
first, keep the old tables, prove it, *then* drop.

### Phase 3a/3b — executed 2026-07-23

**3a done as scoped:** `item_image_repository.py`'s `get_item_owner_and_visibility`/
`get_item_owner_id`/`get_image_owner_id` rewritten onto `gear_items_v2` (self-join via
`aliased(GearItemDBV2)` for the parent container's visibility). `image_upload_service.py`
needed no changes. `ItemImageDB`'s ORM FK/relationship fixed in lockstep (same reasoning as
Phase 1 — `backend_test` is built from `Base.metadata.create_all()`, so the ORM declaration,
not the migration, governs what the test suite actually exercises). New test
`test_item_images_authorization.py` rewritten onto V2 fixtures, `test_get_item_images_v2_only_item_no_v1_counterpart`
added as the direct #043 regression test.

**3b turned out to be much larger than scoped.** The plan listed repository.py's public
browsing/ratings/reports/promotions/share-token *repository methods*. Reading them found most
(ratings, promotions, `create_share_token`/`revoke_share_token`) don't touch V1 models at all —
only their **ORM FK/relationship annotations** needed fixing (`ContainerRatingDB`,
`ItemPromotionDB`, `ContentReportDB` → `gear_items_v2`, same lockstep pattern as 3a/Phase 1).
What actually needed **query rewrites** was different from the plan's list, found by tracing
real call chains:

- `repository.py`: `get_public_containers`/`get_public_container`/`get_public_container_for_reporting`,
  `count_user_containers`/`count_user_items`, `get_container_by_token`, `get_share_tokens_by_container`
  (ownership check), `set_container_hidden_by_reports` — all rewritten onto `GearItemDBV2`.
  New `get_container_v2_owned_or_public()` added and used by `router.py`'s two rating endpoints
  (`rate_container`, `delete_container_rating`), which had their own independent V1-then-V1-public
  fallback chain that 404'd for private V2-only containers even for their own owner.
- `service.py`: added `_map_item_v2_to_response`/`_map_container_v2_to_response_with_author`
  (V2 counterparts of the V1-only mappers, which stay untouched — they're now scoped
  exclusively to the V1 CRUD methods Phase 4 deletes). Added `GearItemDBV2.user` relationship
  (db_models_v2.py) since V2 had no user-lookup relationship at all (needed for public-container
  author names).
- **The catalogue-linking subsystem was not in the plan's inventory at all**, and turned out to
  be completely broken for V2-native items by the identical root cause: `can_promote_item`,
  `promote_item`, `get_promotion_status`, `update_item_from_catalogue`, `link_item_to_catalogue`,
  `fetch_images_from_catalogue`, `add_catalogue_item_to_container`, `_copy_catalogue_images_to_item`'s
  existence check, and `_add_item_to_catalogue`/`add_item_to_catalogue` all queried `GearItemDB`/
  `GearContainerDB` (V1) directly rather than going through `repository.py`. All rewritten onto
  `GearItemDBV2` / `GearRepositoryV2` (added `self._repository_v2 = GearRepositoryV2(repository.db)`
  to `GearService.__init__`). `add_catalogue_item_to_container` now creates via
  `GearRepositoryV2.create_item` instead of V1 `create_item`, fixing the plan's flagged
  "only endpoint that still creates a V1 item" concern.

**Real bug found via testing, not in the plan:** `_map_item_v2_to_response`'s first draft
crashed (`pydantic.ValidationError`) mapping any real V2 item with no `weight` set, because the
V1-shaped `ItemResponse` schema requires `weight`/`weightUnit` non-optional — true for V1's
NOT-NULL columns, **not** true for `gear_items_v2` (nullable, and `GearItemCreateV2` doesn't
default them the way it defaults `quantity`/`status`/`priority`/`category`). Fixed by defaulting
to `0.0`/`"g"` at the mapping layer rather than crashing. This was invisible before Phase 3b
because the old V1-only public/promotion code paths only ever saw legacy rows that always had a
concrete weight.

Test additions: `test_unified_model_v2.py::TestGearServiceRepointedAtV2` (4 tests) covering
public browsing with author name, rating + reporting + auto-hide, promotion eligibility/
promoting/status, and catalogue-item-to-V2-container — all against V2-only containers/items,
using `GearService`/`GearRepository` (the classes that back the live endpoints) rather than
`GearServiceV2` directly, to actually exercise the repointed code. `test_share_tokens.py`'s
Phase-1 "known gap" test flipped from asserting `[]` to asserting the token is now returned
(exactly the update its own docstring called for).

Full `tests/integration/gear/` suite: **141 passed**, 0 failures (clean single run). `black`/
`mypy` (project-wide) clean.

### Phase 3c/3d — executed 2026-07-23

**3c (`stats/router.py`):** straightforward — `get_container_stats`/`get_item_stats` repointed
from `count(GearContainerDB.id)`/`count(GearItemDB.id)` to `count(GearItemDBV2.id) WHERE
item_type='container'/'item'` (including the `created_at >= month_start` variants). No mapping
layer involved, no surprises.

**3d (`admin/repository.py` + `admin/service.py`):** `get_all_containers`, `get_container_by_id`,
`update_container`, `delete_container`, `get_all_items`, `get_item_by_id`, `delete_item`
rewritten onto `GearItemDBV2` (self-`aliased()` for the item-count-per-container aggregate and
for the item→parent-container join, since it's the same table). `admin/service.py`'s field
mapping updated (`container.type` → `container.container_type`, `.items` → `.children` filtered
to `item_type='item'` since `.children` includes nested sub-containers unlike V1's
`GearContainerDB.items`, `item.container_id` → `item.parent_item_id`) plus the same
nullable-weight/category/quantity defensive defaulting as 3a/3b (`AdminItemResponse.weight`/
`category`/`quantity`/`status`/`priority`/`containerId` are all non-optional but genuinely
nullable on `gear_items_v2`).

**Two real bugs found only by writing tests, not visible from reading the code:**
1. `get_all_containers`'s aggregate query (`func.count(...).group_by(...)`) combined with
   `joinedload(GearItemDBV2.user)` raised `MissingGreenlet` — `joinedload` adds a JOIN to the
   *same* statement, which doesn't compose with `GROUP BY`. V1's original code already knew
   this and used `selectinload(GearContainerDB.user)` there specifically (while using
   `joinedload` for the single-row `get_container_by_id`/`update_container`, where it's safe) —
   missed on first pass since it looked like an arbitrary V1 inconsistency rather than a
   deliberate constraint. Fixed by matching V1's choice per-method rather than applying
   `joinedload` everywhere.
2. `update_container`'s plain `await self.db.refresh(container_db)` (inherited verbatim from V1)
   expires **all** attributes including the eagerly-loaded `.children`/`.user`, so accessing
   `.children` afterward in `admin/service.py` triggers a lazy, sync-only reload that crashes
   under async SQLAlchemy (`MissingGreenlet`). This looks like a **latent bug already present in
   the original V1 code** (same `refresh()` + `.items` access pattern), just never triggered
   because no existing test exercises "update a container via admin, then read its item count in
   the same response." Fixed (for the V2 path) by scoping the refresh to
   `attribute_names=["updated_at", *data.keys()]`, which reloads only the changed columns and
   leaves the eager-loaded relationships alone.

Test additions: `tests/integration/gear/test_admin_stats_v2.py` (3 tests) — admin
list/get/update/delete against a V2-only container+item, and stats endpoints counting a V2-only
container/item — calling the real `AdminService`/`AdminRepository`/stats router functions
directly, not just checking query shape.

**Phase 3e (ORM relationship hygiene) needed no separate pass** — it was completed incrementally
in lockstep with 3a/3b/3d as each ancillary table's query code was repointed (see the "recurring
adjustment" notes above): `ContainerShareTokenDB`, `ItemImageDB`, `ContainerRatingDB`,
`ItemPromotionDB`, `ContentReportDB` all now point at `GearItemDBV2`, and `GearItemDBV2.user` was
added. The only remaining `GearContainerDB`/`GearItemDB` relationships left in `db_models.py`
(`GearItemDB.container` ⟷ `GearContainerDB.items`, `GearContainerDB.user`) are internal to the
V1 CRUD classes themselves — exactly what Phase 4 deletes along with the classes.

**Phase 3 complete.** Full `tests/integration/gear/` + `tests/test_admin_authorization.py`
suite: all green (clean single run). `black`/`mypy` (project-wide) clean throughout.

---

## Phase 4 — Remove the dead V1 endpoint/method surface (code only, no table drop)

**Goal:** delete the now-duplicate, frontend-unused CRUD/stats surface. Nothing here is
reachable from the frontend (proven: 0 callers).

**What to delete:**
- `router.py`: the container-CRUD endpoints (`POST/GET/PATCH/DELETE /containers`,
  `GET /containers/{id}`, `DELETE /containers`), item-CRUD endpoints
  (`POST /containers/{id}/items`, `GET /containers/{id}/items`, `GET /items`,
  `GET /items/{id}`, `PATCH /items/{id}`, `PATCH /items/{id}/move`, `DELETE /items/{id}`,
  `PATCH /items/batch-order`), and the two stats endpoints
  (`/containers/{id}/stats/weight`, `/stats/readiness`). **Keep** everything repointed in
  Phase 3 (public, ratings, reports, promotions, share tokens, catalogue, `/me/limits`, and the
  included `item_image_router` + `catalogue_item_image_router`).
- `repository.py` / `service.py`: delete the corresponding CRUD methods (`create_container`,
  `get_container(s)`, `update_container`, `delete_container`, `delete_all_containers`,
  `create_item`, `get_item(s)`, `get_all_items`, `update_item`, `move_item`, `delete_item`,
  `batch_update_item_order`, and the weight/readiness calculators) once confirmed unused by any
  retained endpoint.
- Frontend `src/modules/gear/services/gearContainerApiService.ts`: prune the dead methods
  `createContainer/getContainers/getContainer/updateContainer/deleteContainer/
  deleteAllContainers/getContainerWeight/getContainerReadiness` (0 callers). **Keep**
  `rateContainer/deleteContainerRating/reportPublicContainer/withdrawReport/getReportStatus` —
  the file remains as the ratings/reports client.

**Verify before:** Phase 3 verified in prod-like environment. **Verify after:** full app smoke
test (auth UI CRUD via `/gear/v2/*`, public pages, ratings, reports, share, catalogue, admin,
stats); `grep -rn "GearContainerDB\|GearItemDB\b" app/` returns only `db_models.py` definitions
and migration files (no live query sites); frontend build passes with the pruned service.

**Rollback:** git revert. Tables still present, so no data risk.

### Phase 4 — executed 2026-07-23

`router.py`: deleted the container/item CRUD block (`create_container` through
`batch_update_item_order`, ~500 lines) and the two stats endpoints
(`/containers/{id}/stats/weight`, `/stats/readiness`), plus the now-dead
`get_optional_billing_service`/`OptionalBillingServiceDep` helper (only those deleted endpoints
used it). `repository.py`/`service.py`: deleted the corresponding CRUD methods and the
now-fully-dead V1 mappers (`_map_item_to_response`, `_map_container_to_response`,
`_map_container_to_response_with_author` — the latter was already orphaned since Phase 3b
repointed every caller onto `_map_container_v2_to_response_with_author`), plus
`calculate_container_weight`/`calculate_container_readiness` (no callers left once the stats
endpoints were gone — confirmed backend has no V2 equivalent either; weight/readiness
calculation is a frontend-only concern for V2, per `containerCalculationsV2.ts`).

**One more #043-pattern bug found only by `mypy`, after deletion:** `create_share_token`
(service.py) still verified ownership via the now-deleted `self.repository.get_container()` (a
different code path than the ones audited in 3b, since it called the repository method by name
rather than a raw `GearContainerDB` query, so it didn't show up in the `grep -rn GearContainerDB`
sweep). Would have always raised "Container not found or access denied" for a V2-only
container's own owner. Fixed by switching to `self._repository_v2.get_item(container_id,
user_id)`. **Lesson:** the `GearContainerDB`/`GearItemDB` grep sweep this plan relied on
throughout finds *direct model usage*, not calls to repository methods that wrap them — deleting
the V1 repository methods (this phase) forced mypy to surface the ones the grep missed.

**Verification before deleting anything:** re-confirmed zero frontend callers of the 8 dead
`gearContainerApiService.ts` methods (`grep` across `src/`, not just the assumption from
Phase 3b's inventory) and zero direct calls to the 12 V1 REST paths bypassing that service
class — both clean, matching the plan.

**Frontend:** pruned `gearContainerApiService.ts` down to the 5 live methods
(`rateContainer`/`deleteContainerRating`/`reportPublicContainer`/`getReportStatus`/
`withdrawReport`); removed the now-unused `cleanContainerData` helper and V1 DTO imports.
`pnpm type-check` and `pnpm lint` clean.

**Test files:** deleted `test_containers_crud.py`, `test_data_integrity.py`,
`test_items_crud.py`, `test_nesting_relationships.py`, `test_weight_calculations.py` — all five
were 100% V1-only ("PHASE 0: pre-migration baseline" suites per their own docstrings), testing
methods that no longer exist. Verified `test_unified_model_v2.py` already has equivalent V2
coverage (create/read/update/move/delete, nesting, cascade delete) before deleting — no coverage
gap. Removed the three vacuous V1-vs-V2 row-count comparison tests from
`test_migration_integrity.py` (`test_all_containers_migrated`, `test_all_items_migrated`,
`test_total_count_preserved`) since there's no longer a way to write V1 data to compare against;
kept the V2 field-mapping tests and the Phase 2 FK regression test.

**Full-suite verification caught 7 failures** (`test_billing_service.py` x5, `test_main.py` x2,
`test_convert_empty_strings_middleware.py` x2) — confirmed **pre-existing and unrelated**: none
of the three files reference gear code at all, and re-running them against the Phase 0-3
committed state (via `git stash` of Phase 4's uncommitted changes) reproduced the identical
failures. Not fixed here (out of scope); full suite is otherwise green.

`ruff check`/`black`/`mypy` (project-wide) clean throughout. Full backend `tests/` suite green
(excluding the 7 pre-existing unrelated failures). `pnpm type-check`/`pnpm lint` clean.

**Phase 4 complete.**

---

## Phase 5 — Drop V1 tables and models (final)

**Goal:** single source of truth. Only run once Phases 3–4 have been live and stable — by now
nothing reads V1, so there's no window where an endpoint 500s.

**Pre-drop gate (in the migration and manually):**
- Re-run Phase-0 reconciliation (a)–(d): still 0 rows.
- `grep -rn "gear_containers\|gear_items\b" app/` → no live SQL/ORM (only `db_models.py` classes
  to be removed + migration files).
- Confirm Phase 2 left **no** FK from any surviving table to `gear_containers`/`gear_items`
  (re-run the "other tables FK-referencing" query — should be empty except the V1 tables' own
  internal self-FKs).

**New migration:** `migrations/059_drop_v1_gear_tables.py`
- `upgrade()`: guard — `if any external FK references gear_items/gear_containers: sys.exit(1)`.
  Then `DROP TABLE IF EXISTS gear_items CASCADE; DROP TABLE IF EXISTS gear_containers CASCADE;`
  (order: items first). The internal self-referential FKs (`parent_container_id`,
  `container_id`, `nested_container_id`, `linked_item_id`) drop with the tables.
- `downgrade()`: recreate empty `gear_containers`/`gear_items` from the `010`/`011` DDL
  (best-effort; note that real recovery is the Phase-0 backup — the data is not restored by
  downgrade).

**Code:** remove `GearContainerDB` and `GearItemDB` classes from `db_models.py` (keep
`ItemImageDB`, `ContainerShareTokenDB`, `ContainerRatingDB`, `ItemPromotionDB`,
`ContentReportDB`, `GlobalCatalogueItemDB`, `CatalogueItemImageDB`). Remove any last stray
`from app.modules.gear.db_models import GearItemDB` local imports in `service.py` (should
already be gone after Phase 3; double-check). Optionally relocate the 5 surviving ancillary
models into `db_models_v2.py` for cohesion (not required for correctness).

**Verify before:** gate above green, backup fresh. **Verify after:** app boots (SQLAlchemy mapper
configures with no V1 classes); full smoke test again; `schema_migrations` records 059; a final
grep shows `gear_containers`/`gear_items` appear only in historical migration files.

**Rollback:** this is the only destructive phase — rollback = restore the Phase-0 backup
(downgrade recreates empty tables but not data). **Take a fresh backup immediately before
running 059.**

---

## Cross-cutting notes

- **Endpoint contracts stay stable in every phase** except the deliberate deletions in Phase 4
  (which have 0 frontend callers). No live consumer path changes. The only endpoint that
  *creates* a V1 item today, `POST /gear/containers/{id}/items/from-catalogue/{cid}` (used by
  `catalogueApiService.ts`), is repointed to write `gear_items_v2` in Phase 3b rather than
  dropped.
- **Ordering guarantees no 500 window:** `057` fixes an existing 500; `058` only tightens/adds
  FKs already satisfiable; `059` runs after all reads are off V1. Reads are moved (Phase 3)
  before the source tables are removed (Phase 5).
- **`schema_migrations` trust:** every new migration verifies physical state (`table_exists`,
  `constraint_exists`, `pg_constraint` lookups, orphan-row pre-flights) rather than trusting
  recorded-applied status — the lesson from #044 and the `052` bug is baked into `057` and `058`.

## Critical files

- `backend/app/modules/gear/item_image_repository.py`
- `backend/app/modules/gear/repository.py`
- `backend/app/modules/gear/service.py`
- `backend/app/modules/gear/router.py`
- `backend/migrations/052_update_foreign_keys_to_unified_model.py` (pattern reference for new
  057/058/059)
- Also load-bearing: `backend/app/modules/stats/router.py`, `backend/app/modules/admin/
  repository.py`, `backend/app/modules/admin/service.py`, `backend/app/modules/gear/
  db_models.py`, `backend/app/modules/gear/db_models_v2.py`,
  `backend/tests/integration/gear/conftest.py`, frontend
  `src/modules/gear/services/gearContainerApiService.ts`
