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
