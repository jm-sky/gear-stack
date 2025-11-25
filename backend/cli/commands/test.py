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

    try:
        import sentry_sdk

        # Capture exception with Sentry
        sentry_sdk.capture_exception(RuntimeError("Test exception for Sentry integration - this is intentional!"))

        # Flush events to ensure they are sent before CLI exits
        console.print("[blue]Flushing Sentry events...[/blue]")
        sentry_sdk.flush(timeout=5.0)

        console.print("[green]✓ Test exception sent to Sentry successfully![/green]")
        console.print("[dim]Check your Sentry dashboard at: https://sentry.io/[/dim]")
    except ImportError:
        console.print("[red]✗ Sentry SDK not installed![/red]")
        console.print("[dim]Install with: pip install sentry-sdk[fastapi][/dim]")
    except Exception as e:
        console.print(f"[red]✗ Failed to send test exception to Sentry: {e}[/red]")
