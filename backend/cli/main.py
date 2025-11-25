"""Main CLI application.

This module configures the main Typer application and registers all command groups.
"""

import typer
from rich.console import Console

from app.core.app_factory import init_sentry

# Initialize Typer app
app = typer.Typer(
    name="cli",
    help="Management CLI for FastAPI project - Django-inspired commands",
    add_completion=True,
    no_args_is_help=True,
)

# Initialize Rich console (shared across commands)
console = Console()


def main() -> None:
    """Main entry point for the CLI."""
    # Initialize Sentry before running CLI (to catch all errors)
    init_sentry()
    
    app()


if __name__ == "__main__":
    main()
