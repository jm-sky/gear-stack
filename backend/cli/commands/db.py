"""Database management CLI commands."""

import asyncio
import importlib.util
import sys
from importlib import import_module
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

db_app = typer.Typer(
    name="db",
    help="Database management commands",
    no_args_is_help=True,
)

console = Console()

MODEL_MODULES = [
    "app.modules.auth.db_models",
    "app.modules.users.db_models",
    "app.modules.logs.db_models",
    "app.modules.settings.db_models",
    "app.modules.tenants.db_models",
    "app.modules.two_factor.db_models",
]


def _import_model_modules() -> None:
    """Ensure all SQLAlchemy models are imported before create_all."""
    for module_path in MODEL_MODULES:
        try:
            import_module(module_path)
        except ModuleNotFoundError:
            console.print(f"[yellow]Skipping missing module:[/yellow] {module_path}")


@db_app.command("init")
def init_database(force: bool = typer.Option(False, "--force", "-f", help="Recreate database file if it already exists")) -> None:
    """Initialize application database (run SQLAlchemy metadata create_all)."""

    async def _init() -> None:
        _import_model_modules()

        # Import SchemaMigration model to ensure it's included in metadata
        from app.core.migrations import SchemaMigration  # noqa: F401

        from app.core.database import Base, engine, init_db

        if force:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

        await init_db()

        # Mark migration 000 as applied if it wasn't already
        from app.core.migrations import ensure_schema_migrations_table, is_migration_applied, mark_migration_as_applied

        await ensure_schema_migrations_table()
        if not await is_migration_applied("000"):
            await mark_migration_as_applied("000", "create_schema_migrations")
            console.print("[green]✓ Migration 000 marked as applied[/green]")

    db_path = Path(__file__).resolve().parents[2] / "data" / "app.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists() and not force:
        console.print(f"[yellow]Database already exists at[/yellow] {db_path}")
        if not Confirm.ask("Re-run initialization anyway?", default=True):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit()

    console.print("[bold green]Initializing database...[/bold green]")
    asyncio.run(_init())
    console.print(f"[bold green]✓ Database ready:[/bold green] {db_path}")


@db_app.command("migrate")
def migrate_database(
    fake: bool = typer.Option(False, "--fake", help="Mark migrations as applied without running them"),
    skip_init_check: bool = typer.Option(False, "--skip-init-check", help="Skip automatic init if database is not initialized"),
) -> None:
    """Run all pending migrations in order.

    Automatically runs 'db init' if database is not initialized.
    """

    async def _migrate() -> None:
        from app.core.migrations import (
            discover_migrations,
            ensure_schema_migrations_table,
            get_applied_migrations,
            is_database_initialized,
            is_migration_applied,
            mark_migration_as_applied,
        )

        # Check if database is initialized, if not run init first
        if not skip_init_check:
            if not await is_database_initialized():
                console.print("[yellow]Database is not initialized. Running 'db init' first...[/yellow]")
                # Run init logic
                _import_model_modules()
                from app.core.migrations import SchemaMigration  # noqa: F401
                from app.core.database import Base, engine, init_db

                await init_db()

                # Mark migration 000 as applied
                await ensure_schema_migrations_table()
                if not await is_migration_applied("000"):
                    await mark_migration_as_applied("000", "create_schema_migrations")
                    console.print("[green]✓ Migration 000 marked as applied[/green]")

                console.print("[bold green]✓ Database initialized[/bold green]\n")

        # Ensure schema_migrations table exists
        await ensure_schema_migrations_table()

        # Get migrations directory
        migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
        if not migrations_dir.exists():
            console.print(f"[red]Migrations directory not found:[/red] {migrations_dir}")
            raise typer.Exit(1)

        # Discover all migrations
        all_migrations = discover_migrations(migrations_dir)
        if not all_migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Get applied migrations
        applied_versions = set(await get_applied_migrations())

        # Find pending migrations
        pending_migrations = [(version, name, filepath) for version, name, filepath in all_migrations if version not in applied_versions]

        if not pending_migrations:
            console.print("[bold green]✓ All migrations are already applied[/bold green]")
            return

        console.print(f"[bold]Found {len(pending_migrations)} pending migration(s)[/bold]")

        # Run pending migrations in order
        for version, name, filepath in pending_migrations:
            console.print(f"\n[bold cyan]Running migration {version}: {name}[/bold cyan]")

            if fake:
                # Just mark as applied without running
                await mark_migration_as_applied(version, name)
                console.print(f"[yellow]Fake: Marked {version} as applied[/yellow]")
                continue

            try:
                # Import and run migration
                spec = importlib.util.spec_from_file_location(f"migration_{version}", filepath)
                if spec is None or spec.loader is None:
                    console.print(f"[red]Failed to load migration:[/red] {filepath}")
                    raise typer.Exit(1)

                migration_module = importlib.util.module_from_spec(spec)
                sys.modules[f"migration_{version}"] = migration_module
                spec.loader.exec_module(migration_module)

                # Run upgrade function
                if not hasattr(migration_module, "upgrade"):
                    console.print(f"[red]Migration {version} does not have upgrade() function[/red]")
                    raise typer.Exit(1)

                await migration_module.upgrade()

                # Mark as applied
                await mark_migration_as_applied(version, name)
                console.print(f"[bold green]✓ Migration {version} applied successfully[/bold green]")

            except Exception as e:
                console.print(f"[red]✗ Migration {version} failed:[/red] {e}")
                raise typer.Exit(1)

        console.print("\n[bold green]✓ All pending migrations completed[/bold green]")

    asyncio.run(_migrate())


@db_app.command("migrate-status")
def migrate_status() -> None:
    """Show status of all migrations."""

    async def _status() -> None:
        from app.core.migrations import (
            discover_migrations,
            ensure_schema_migrations_table,
            get_applied_migrations,
        )

        # Ensure schema_migrations table exists
        await ensure_schema_migrations_table()

        # Get migrations directory
        migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
        if not migrations_dir.exists():
            console.print(f"[red]Migrations directory not found:[/red] {migrations_dir}")
            raise typer.Exit(1)

        # Discover all migrations
        all_migrations = discover_migrations(migrations_dir)
        if not all_migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Get applied migrations
        applied_versions = set(await get_applied_migrations())

        # Create table
        table = Table(title="Migration Status")
        table.add_column("Version", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")

        pending_count = 0
        applied_count = 0

        for version, name, _ in all_migrations:
            if version in applied_versions:
                status = "[green]✓ Applied[/green]"
                applied_count += 1
            else:
                status = "[yellow]○ Pending[/yellow]"
                pending_count += 1

            table.add_row(version, name, status)

        console.print(table)
        console.print(f"\n[bold]Total: {len(all_migrations)}[/bold] | [green]Applied: {applied_count}[/green] | [yellow]Pending: {pending_count}[/yellow]")

    asyncio.run(_status())


@db_app.command("migrate-graceful")
def migrate_graceful(
    from_version: str | None = typer.Option(None, "--from", help="Start from specific migration version (e.g., '020')"),
    skip_init_check: bool = typer.Option(False, "--skip-init-check", help="Skip automatic init if database is not initialized"),
) -> None:
    """Run migrations gracefully, ignoring errors and continuing.

    This command is useful when migrations were created in wrong order or
    filenames were changed. It will attempt to run migrations but continue
    even if errors occur.

    If --from is provided, it will unmark that migration and all subsequent
    ones, then re-run them. If --from is not provided, it will run all
    pending migrations.

    Examples:
        cli db migrate-graceful                    # Run all pending migrations
        cli db migrate-graceful --from 020         # Re-run from migration 020 onwards
    """

    async def _migrate_graceful() -> None:
        from app.core.migrations import (
            discover_migrations,
            ensure_schema_migrations_table,
            get_applied_migrations,
            is_database_initialized,
            is_migration_applied,
            mark_migration_as_applied,
            unmark_migration,
        )

        # Check if database is initialized, if not run init first
        if not skip_init_check:
            if not await is_database_initialized():
                console.print("[yellow]Database is not initialized. Running 'db init' first...[/yellow]")
                # Run init logic
                _import_model_modules()
                from app.core.migrations import SchemaMigration  # noqa: F401
                from app.core.database import Base, engine, init_db

                await init_db()

                # Mark migration 000 as applied
                await ensure_schema_migrations_table()
                if not await is_migration_applied("000"):
                    await mark_migration_as_applied("000", "create_schema_migrations")
                    console.print("[green]✓ Migration 000 marked as applied[/green]")

                console.print("[bold green]✓ Database initialized[/bold green]\n")

        # Ensure schema_migrations table exists
        await ensure_schema_migrations_table()

        # Get migrations directory
        migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
        if not migrations_dir.exists():
            console.print(f"[red]Migrations directory not found:[/red] {migrations_dir}")
            raise typer.Exit(1)

        # Discover all migrations
        all_migrations = discover_migrations(migrations_dir)
        if not all_migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        # Get applied migrations
        applied_versions = set(await get_applied_migrations())

        # If --from is provided, unmark that migration and all subsequent ones
        if from_version:
            console.print(f"[bold yellow]Unmarking migrations from {from_version} onwards...[/bold yellow]")
            unmarked_count = 0
            for version, _, _ in all_migrations:
                try:
                    # Compare versions numerically
                    version_float = float(version)
                    from_float = float(from_version)
                    if version_float >= from_float:
                        if await is_migration_applied(version):
                            await unmark_migration(version)
                            console.print(f"[yellow]Unmarked migration {version}[/yellow]")
                            unmarked_count += 1
                            applied_versions.discard(version)
                except ValueError:
                    # If version comparison fails, use string comparison
                    if version >= from_version:
                        if await is_migration_applied(version):
                            await unmark_migration(version)
                            console.print(f"[yellow]Unmarked migration {version}[/yellow]")
                            unmarked_count += 1
                            applied_versions.discard(version)

            if unmarked_count > 0:
                console.print(f"[bold yellow]✓ Unmarked {unmarked_count} migration(s)[/bold yellow]\n")
            else:
                console.print(f"[yellow]No migrations found to unmark from version {from_version}[/yellow]\n")

        # Find migrations to run
        # If --from was provided, we want to run from that version onwards
        # Otherwise, run all pending migrations
        migrations_to_run: list[tuple[str, str, Path]] = []
        for version, name, filepath in all_migrations:
            if from_version:
                # Check if this migration should be run (>= from_version)
                try:
                    version_float = float(version)
                    from_float = float(from_version)
                    if version_float >= from_float:
                        migrations_to_run.append((version, name, filepath))
                except ValueError:
                    if version >= from_version:
                        migrations_to_run.append((version, name, filepath))
            else:
                # Run all pending migrations
                if version not in applied_versions:
                    migrations_to_run.append((version, name, filepath))

        if not migrations_to_run:
            console.print("[bold green]✓ No migrations to run[/bold green]")
            return

        console.print(f"[bold]Found {len(migrations_to_run)} migration(s) to run gracefully[/bold]")

        # Run migrations gracefully (ignore errors)
        success_count = 0
        error_count = 0
        skipped_count = 0

        for version, name, filepath in migrations_to_run:
            console.print(f"\n[bold cyan]Running migration {version}: {name}[/bold cyan]")

            try:
                # Import and run migration
                spec = importlib.util.spec_from_file_location(f"migration_{version}", filepath)
                if spec is None or spec.loader is None:
                    console.print(f"[red]Failed to load migration:[/red] {filepath}")
                    error_count += 1
                    continue

                migration_module = importlib.util.module_from_spec(spec)
                sys.modules[f"migration_{version}"] = migration_module
                spec.loader.exec_module(migration_module)

                # Run upgrade function
                if not hasattr(migration_module, "upgrade"):
                    console.print(f"[red]Migration {version} does not have upgrade() function[/red]")
                    error_count += 1
                    continue

                await migration_module.upgrade()

                # Mark as applied (even if it was already applied, this is safe)
                await mark_migration_as_applied(version, name)
                console.print(f"[bold green]✓ Migration {version} applied successfully[/bold green]")
                success_count += 1

            except Exception as e:
                console.print(f"[yellow]⚠ Migration {version} failed (continuing):[/yellow] {e}")
                error_count += 1
                # Don't mark as applied if it failed
                # But check if it was already applied before
                if await is_migration_applied(version):
                    console.print(f"[yellow]  Note: Migration {version} was already marked as applied in database[/yellow]")
                    skipped_count += 1

        console.print("\n[bold]Migration summary:[/bold]")
        console.print(f"  [green]✓ Success: {success_count}[/green]")
        if error_count > 0:
            console.print(f"  [yellow]⚠ Errors (ignored): {error_count}[/yellow]")
        if skipped_count > 0:
            console.print(f"  [yellow]○ Skipped (already applied): {skipped_count}[/yellow]")
        console.print(f"\n[bold green]✓ Graceful migration completed[/bold green]")

    asyncio.run(_migrate_graceful())


@db_app.command("migrate-unmark")
def migrate_unmark(
    version: str = typer.Argument(..., help="Migration version to unmark (e.g., '020')"),
) -> None:
    """Remove a migration from schema_migrations table.

    This allows re-running a migration that was already marked as applied.
    Useful when migration files were renamed or need to be re-executed.

    Example:
        cli db migrate-unmark 020
    """

    async def _unmark() -> None:
        from app.core.migrations import (
            ensure_schema_migrations_table,
            is_migration_applied,
            unmark_migration,
        )

        # Ensure schema_migrations table exists
        await ensure_schema_migrations_table()

        # Check if migration is applied
        if not await is_migration_applied(version):
            console.print(f"[yellow]Migration {version} is not marked as applied[/yellow]")
            return

        # Unmark migration
        await unmark_migration(version)
        console.print(f"[bold green]✓ Migration {version} unmarked successfully[/bold green]")
        console.print(f"[yellow]You can now re-run it with:[/yellow] cli db migrate-graceful --from {version}")

    asyncio.run(_unmark())


@db_app.command("seed")
def seed_database(
    catalogue: bool = typer.Option(True, "--catalogue/--no-catalogue", help="Seed catalogue items"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-seed (delete existing data)"),
) -> None:
    """Seed database with initial data.

    This command populates the database with predefined seed data.
    Currently supports:
    - Catalogue items (global gear catalogue)
    """

    async def _seed() -> None:
        from app.core.database import get_db

        # Get database session
        async for db in get_db():
            # Seed catalogue items
            if catalogue:
                from app.modules.gear.db_models import CatalogueItemImageDB, GlobalCatalogueItemDB
                from app.seeders import CATALOGUE_ITEM_IMAGES, CATALOGUE_ITEMS
                from sqlalchemy import delete, select

                console.print("[bold cyan]Seeding catalogue items...[/bold cyan]")

                # Check existing items
                result = await db.execute(select(GlobalCatalogueItemDB))
                existing_items = result.scalars().all()

                if existing_items and not force:
                    console.print(f"[yellow]Found {len(existing_items)} existing catalogue items[/yellow]")
                    if not Confirm.ask("Delete existing items and re-seed?", default=False):
                        console.print("[yellow]Skipping catalogue seed[/yellow]")
                        return

                if existing_items and force:
                    console.print(f"[yellow]Deleting {len(existing_items)} existing items...[/yellow]")
                    # Delete images first (CASCADE should handle this, but let's be explicit)
                    await db.execute(delete(CatalogueItemImageDB))
                    await db.execute(delete(GlobalCatalogueItemDB))
                    await db.commit()

                # Create system user for seeded items (use first admin or create placeholder)
                from app.modules.auth.db_models import UserDB
                result = await db.execute(select(UserDB).where(UserDB.is_admin == True).limit(1))
                admin_user = result.scalar_one_or_none()

                if not admin_user:
                    console.print("[yellow]No admin user found. Creating placeholder 'system' user...[/yellow]")
                    system_user = UserDB(
                        email="system@gearstack.local",
                        is_admin=True,
                        is_active=True,
                    )
                    db.add(system_user)
                    await db.commit()
                    await db.refresh(system_user)
                    creator_id = str(system_user.id)
                else:
                    creator_id = str(admin_user.id)

                # Insert seed items
                from pathlib import Path
                from ulid import ULID

                created_count = 0
                images_count = 0
                for item_data in CATALOGUE_ITEMS:
                    item_id = str(ULID())
                    catalogue_item = GlobalCatalogueItemDB(
                        id=item_id,
                        **item_data,
                        created_by=creator_id,
                    )
                    db.add(catalogue_item)
                    created_count += 1

                    # Add image if exists for this item
                    item_name = item_data.get("name")
                    if item_name and item_name in CATALOGUE_ITEM_IMAGES:
                        image_filename = CATALOGUE_ITEM_IMAGES[item_name]
                        image_path = Path(__file__).parent.parent.parent / "images" / "global-catalogue" / image_filename

                        if image_path.exists():
                            # Get file size and MIME type
                            file_size = image_path.stat().st_size
                            mime_type = "image/jpeg" if image_filename.endswith(".jpg") else \
                                       "image/png" if image_filename.endswith(".png") else \
                                       "image/webp" if image_filename.endswith(".webp") else "image/jpeg"

                            # Create image record
                            relative_path = f"global-catalogue/{image_filename}"
                            image = CatalogueItemImageDB(
                                id=str(ULID()),
                                catalogue_item_id=item_id,
                                user_id=creator_id,
                                storage_type="local",
                                file_path=relative_path,
                                file_name=image_filename,
                                file_size=file_size,
                                mime_type=mime_type,
                                is_primary=True,
                                order=0,
                                is_processed=True,
                            )
                            db.add(image)
                            images_count += 1

                await db.commit()
                console.print(f"[bold green]✓ Created {created_count} catalogue items with {images_count} images[/bold green]")

            break  # Exit after first db session

    console.print("[bold green]Starting database seeding...[/bold green]")
    asyncio.run(_seed())
    console.print("[bold green]✓ Database seeding complete[/bold green]")
