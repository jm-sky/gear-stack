"""Test commands for development and debugging.

This module provides test commands for various purposes like testing Sentry integration.
"""

import typer
from rich.console import Console

# Create test subcommand app
test_app = typer.Typer(
    name="test",
    help="Test commands for development and debugging",
    no_args_is_help=True,
)

console = Console()


@test_app.command("sentry")
def test_sentry() -> None:
    """Throw an unhandled exception to test Sentry error reporting.

    This command intentionally raises an unhandled exception that should
    be caught and reported by Sentry if it's properly configured.

    Examples:
        python -m cli test sentry
    """
    console.print("[yellow]Throwing unhandled exception to test Sentry...[/yellow]")
    console.print("[red]This exception should be caught by Sentry if configured correctly.[/red]\n")

    # Raise an unhandled exception
    raise RuntimeError("Test exception for Sentry integration - this is intentional!")
