# `container_share_tokens` table missing on production — share-token endpoints 500

**Status:** `done`
**Created:** 2026-07-23
**Severity:** High
**Module:** `gear` (backend — container share tokens)
**Source:** Production DB recon (VPS, `gear-stack-db`) run while scoping [#043](2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md)
**Plan:** folded into [docs/plans/2026-07-23-gear-backend-v1-v2-unification.md](../plans/2026-07-23-gear-backend-v1-v2-unification.md) as Phase 1 (migration `057`)

## Problem

The `container_share_tokens` table **does not exist on the production database**, even
though:

- `backend/migrations/schema_migrations` on production lists the migrations that create/touch
  this table (`032`, `036` — `add_container_share_tokens` and a related one) as **applied**.
- The feature is fully live in code: `db_models.py` (`ContainerShareTokenDB`), `repository.py`,
  and `router.py` all reference it, with active endpoints:
  - `GET  /containers/{container_id}/share-tokens`
  - `POST /containers/{container_id}/share-tokens`
  - `DELETE /containers/{container_id}/share-tokens/{token}`
  - `GET /containers/share/{token}` (public, unauthenticated access by token)

Since the physical table is absent, every one of these endpoints will raise
`relation "container_share_tokens" does not exist` at the database layer — an unhandled
`500`, not a graceful `404` or empty result.

This surfaced as a side finding while verifying [#043](2026-07-21--035--item-image-idor.md)'s
recon on production; it is **not** part of the V1/V2 duality itself (the table was supposed to
exist as a V1-era feature) — it looks like either a manual/out-of-band table drop that was never
reflected back into `schema_migrations`, or the migration that created it never actually ran
despite being recorded as applied. The mismatch between `schema_migrations` and physical schema
on production is itself concerning and worth a quick trust check on other recorded-applied
migrations before relying on that table for planning (see [#043](2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md)).

## Impact

- Any user attempting to share a container (generate a share link) gets an unhandled server
  error instead of a working feature or a clear error message.
- Public access to a previously-shared container via `/containers/share/{token}` is also broken
  the same way.
- Not yet confirmed whether this is currently exercised by the frontend UI, or a dead/unreachable
  code path from the user's perspective — needs a quick check before triage.

## Reproduction

1. On production, call `GET /api/gear/containers/{any_container_id}/share-tokens` as the
   authenticated owner.
2. Expect `500 relation "container_share_tokens" does not exist` (verify exact error via logs/
   Sentry) rather than an empty list or `404`.

## Proposed fix

Two things need to happen, in order:

1. **Root-cause the drift** — check `schema_migrations` history and, if possible, server/db
   logs or backups from around when `032`/`036` were recorded as applied, to understand whether
   the table was ever actually created and later dropped, or never created at all. This matters
   for trusting the rest of `schema_migrations` when planning [#043](2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md).
2. **Fix scoping decision** — since this table is V1-shaped (`container_id` FK target should be
   `gear_items_v2` per the same reasoning as [#043](2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md)), don't just recreate it pointing at legacy
   `gear_containers`. Either:
   - Recreate it now pointing at `gear_items_v2`, as a small standalone fix ahead of the full
     V1→V2 backend migration, or
   - Fold it into the V1→V2 migration plan being scoped for #043, so it's created once, correctly,
     as part of that work (avoids doing it twice).

## Scope

- [ ] Determine whether the share-token feature is reachable/used from the current frontend UI
- [ ] Root-cause why `schema_migrations` says applied but the table is absent
- [ ] Decide: standalone hotfix vs. fold into the #043 V1→V2 migration plan
- [ ] Recreate table (if kept) with FK pointing at `gear_items_v2`, not legacy `gear_containers`
- [ ] Spot-check other `schema_migrations`-recorded-applied migrations against production schema
      for similar drift, given this one was found to be false

## Verification

Once fixed: call all four share-token endpoints on production against a real container and
confirm no `500`s, share links resolve, and revocation works.

## Fix landed (2026-07-23, not yet deployed to production)

Migration `057_recreate_container_share_tokens.py` written and verified against a local restored
copy of the production backup (see Phase 1 in
[docs/plans/2026-07-23-gear-backend-v1-v2-unification.md](../plans/2026-07-23-gear-backend-v1-v2-unification.md)).
Table recreated with `container_id` FK → `gear_items_v2` (not legacy `gear_containers`).
`db_models.py`'s `ContainerShareTokenDB` ORM annotation updated to match. Integration tests added
(`test_share_tokens.py`, 3 passing) and full `tests/integration/gear/` suite (135 tests) still
green.

## Deployed and verified on production (2026-07-23)

Migrations `057`/`058` deployed to production; output matched the local dry run exactly
(table created, FK → `gear_items_v2`). User confirmed sharing a container works end-to-end on
production. Closed.
