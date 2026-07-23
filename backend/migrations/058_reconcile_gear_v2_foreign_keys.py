"""Migration: Reconcile ancillary-table foreign keys onto gear_items_v2, programmatically.

Fixes the FK half of docs/issues/2026-07-23--043--gear-v1-v2-backend-duality-image-ownership-broken.md
(Phase 2 of docs/plans/2026-07-23-gear-backend-v1-v2-unification.md). Production recon found:

- `item_images.item_id` and `container_ratings.container_id` each have TWO simultaneous FK
  constraints (one stale, to legacy `gear_items`/`gear_containers`, one correct, to
  `gear_items_v2` -- added by migration 052, which tried to `DROP CONSTRAINT IF EXISTS
  item_images_item_id_fkey` / `..._container_ratings_container_id_fkey` before adding the new
  one, but the *actual* old constraint names in production were `fk_item_images_item_id` /
  `fk_container_ratings_container` -- a different naming convention. `DROP CONSTRAINT IF EXISTS`
  with the wrong name silently no-ops, so both constraints now coexist).
- `item_promotions.item_id` and `content_reports.container_id` were never touched by 052 at all
  -- still FK only to legacy `gear_items` / `gear_containers`.
- `container_share_tokens.container_id` is already correct after migration 057, but is included
  here too (belt-and-suspenders / self-healing if it's ever re-pointed by accident).

This migration does NOT hardcode constraint names (that's exactly what caused the 052 bug). It
looks up whatever FK constraints actually exist on each (table, column) via
`information_schema`, drops any that reference something other than `gear_items_v2`, and adds a
`gear_items_v2` FK if none already exists -- correct on both a database where 052's cleanup
worked and one where it didn't (dev vs. prod diverge here; see #043).

Usage:
    python migrations/058_reconcile_gear_v2_foreign_keys.py upgrade
    python migrations/058_reconcile_gear_v2_foreign_keys.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine

# (table, column, fallback FK name to use if we need to add a new constraint)
TARGET_COLUMNS = [
    ("item_images", "item_id", "item_images_item_id_fkey"),
    ("container_ratings", "container_id", "container_ratings_container_id_fkey"),
    ("container_share_tokens", "container_id", "container_share_tokens_container_id_fkey"),
    ("item_promotions", "item_id", "item_promotions_item_id_fkey"),
    ("content_reports", "container_id", "content_reports_container_id_fkey"),
]

# Downgrade only knows how to restore these two -- 057/052 already left item_images and
# container_ratings pointing at gear_items_v2 as their *correct* state, so downgrade must not
# recreate their stale V1 FK (that would just resurrect the double-FK bug this migration fixes).
DOWNGRADE_V1_TARGETS = {
    "item_promotions": ("item_id", "gear_items", "fk_item_promotions_item_id"),
    "content_reports": ("container_id", "gear_containers", "fk_content_reports_container"),
}


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def get_fk_constraints_on_column(conn, table_name: str, column_name: str) -> list[tuple[str, str]]:
    """Look up the real FK constraint(s) on a (table, column), by inspecting the database.

    Returns a list of (constraint_name, referenced_table) -- there may be more than one, which
    is exactly the double-FK situation this migration is meant to clean up. Never assume a
    constraint name; that assumption is what caused the bug in migration 052.
    """
    result = await conn.execute(
        text("""
            SELECT tc.constraint_name, ccu.table_name AS referenced_table
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name = :table_name
                AND kcu.column_name = :column_name;
        """),
        {"table_name": table_name, "column_name": column_name},
    )
    return [(row.constraint_name, row.referenced_table) for row in result.fetchall()]


async def count_orphans(conn, table_name: str, column_name: str) -> int:
    """Count rows in table_name.column_name that would violate a new FK to gear_items_v2."""
    result = await conn.execute(text(f"""
            SELECT count(*) FROM {table_name} t
            LEFT JOIN gear_items_v2 v ON v.id = t.{column_name}
            WHERE t.{column_name} IS NOT NULL AND v.id IS NULL;
        """))  # noqa: S608 -- table/column names come only from TARGET_COLUMNS above, not user input
    return result.scalar() or 0


async def reconcile_column(conn, table_name: str, column_name: str, new_constraint_name: str) -> None:
    """Ensure (table_name, column_name) has exactly one FK, pointing at gear_items_v2."""
    if not await table_exists(conn, table_name):
        print(f"  ⚠️  {table_name} does not exist, skipping")
        return

    fks = await get_fk_constraints_on_column(conn, table_name, column_name)
    already_correct = [name for name, ref in fks if ref == "gear_items_v2"]
    stale = [(name, ref) for name, ref in fks if ref != "gear_items_v2"]

    if not already_correct:
        orphan_count = await count_orphans(conn, table_name, column_name)
        if orphan_count > 0:
            print(
                f"❌ Error: {table_name}.{column_name} has {orphan_count} row(s) not present in "
                f"gear_items_v2 -- adding the FK would fail. Investigate before re-running "
                f"(see Phase 0 reconciliation in docs/plans/2026-07-23-gear-backend-v1-v2-unification.md)."
            )
            sys.exit(1)

    for name, ref in stale:
        await conn.execute(text(f'ALTER TABLE {table_name} DROP CONSTRAINT "{name}";'))  # noqa: S608
        print(f"  ✓ Dropped stale FK {name} ({table_name}.{column_name} -> {ref})")

    if not already_correct:
        await conn.execute(text(f"""
                ALTER TABLE {table_name}
                ADD CONSTRAINT "{new_constraint_name}"
                    FOREIGN KEY ({column_name})
                    REFERENCES gear_items_v2(id)
                    ON DELETE CASCADE;
            """))  # noqa: S608
        print(f"  ✓ Added FK {new_constraint_name} ({table_name}.{column_name} -> gear_items_v2)")
    else:
        print(f"  ✓ {table_name}.{column_name} already has FK {already_correct[0]} -> gear_items_v2, nothing to add")


async def upgrade() -> None:
    """Reconcile all ancillary-table FKs onto gear_items_v2."""
    print("Reconciling gear-related foreign keys onto gear_items_v2...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if not items_v2_exist:
            print("❌ Error: gear_items_v2 table does not exist. Run migration 050 first.")
            sys.exit(1)

        for table_name, column_name, new_constraint_name in TARGET_COLUMNS:
            print(f"Checking {table_name}.{column_name}...")
            await reconcile_column(conn, table_name, column_name, new_constraint_name)

    print("✓ Foreign key reconciliation complete")


async def downgrade() -> None:
    """Revert item_promotions/content_reports to their pre-058 V1-only FK.

    Does NOT restore the double-FK on item_images/container_ratings (that was a bug, not a
    feature) and does NOT touch container_share_tokens. True rollback is the Phase 0 backup.
    """
    print("Reverting item_promotions/content_reports foreign keys to V1 tables...")

    async with engine.begin() as conn:
        for table_name, (column_name, v1_table, v1_constraint_name) in DOWNGRADE_V1_TARGETS.items():
            if not await table_exists(conn, table_name):
                print(f"  ⚠️  {table_name} does not exist, skipping")
                continue

            fks = await get_fk_constraints_on_column(conn, table_name, column_name)
            for name, ref in fks:
                if ref == "gear_items_v2":
                    await conn.execute(text(f'ALTER TABLE {table_name} DROP CONSTRAINT "{name}";'))  # noqa: S608
                    print(f"  ✓ Dropped {name} ({table_name}.{column_name} -> gear_items_v2)")

            if await table_exists(conn, v1_table):
                await conn.execute(text(f"""
                        ALTER TABLE {table_name}
                        ADD CONSTRAINT "{v1_constraint_name}"
                            FOREIGN KEY ({column_name})
                            REFERENCES {v1_table}(id)
                            ON DELETE CASCADE;
                    """))  # noqa: S608
                print(f"  ✓ Restored {v1_constraint_name} ({table_name}.{column_name} -> {v1_table})")
            else:
                print(f"  ⚠️  {v1_table} no longer exists, cannot restore V1 FK on {table_name}")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python migrations/058_reconcile_gear_v2_foreign_keys.py [upgrade|downgrade]")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrations/058_reconcile_gear_v2_foreign_keys.py [upgrade|downgrade]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
