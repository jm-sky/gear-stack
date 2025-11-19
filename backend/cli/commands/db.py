"""Database management CLI commands."""

import asyncio
from importlib import import_module
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

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

        from app.core.database import Base, engine, init_db

        if force:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

        await init_db()

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
