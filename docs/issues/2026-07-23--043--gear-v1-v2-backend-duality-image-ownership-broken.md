# Backend gear V1/V2 model duality — item-image ownership/visibility checks broken for V2-native items

**Status:** `todo`
**Created:** 2026-07-23
**Severity:** High
**Module:** `gear` (backend — data model / item images)
**Source:** Manual verification of [#035](2026-07-21--035--item-image-idor.md) by the user

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

## Verification

Blocked on the fix above. Once done: repeat the #035 verification steps (owner/cross-user
access, public/private visibility) against V2-native containers and items, plus a regression
pass on public browsing, ratings, reports, and promotions.
