"""Test commands for development and debugging.

This module provides test commands for various purposes like testing Sentry integration
and storage adapters (local and S3).
"""

import asyncio
from datetime import datetime

import typer
from rich.console import Console

from app.core.config import settings
from app.core.storage.factory import get_storage_adapter

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


@test_app.command("storage")
def test_storage(
    skip_cleanup: bool = typer.Option(False, "--skip-cleanup", help="Skip cleanup after test"),
) -> None:
    """Test storage adapter connectivity and operations.

    Performs a full test of the configured storage adapter:
    1. Uploads a test file
    2. Verifies file exists
    3. Downloads and verifies content
    4. Cleans up test file (unless --skip-cleanup)

    Examples:
        python -m cli test storage
        python -m cli test storage --skip-cleanup
    """
    asyncio.run(_test_storage_async(skip_cleanup))


async def _test_storage_async(skip_cleanup: bool) -> None:
    """Async implementation of storage test."""
    console.print("\n[bold cyan]Testing Storage Adapter[/bold cyan]")
    console.print("=" * 50)

    # Show config
    console.print(f"[dim]Storage Type:[/dim] {settings.storage.type}")
    if settings.storage.type == "s3":
        console.print(f"[dim]S3 Bucket:[/dim] {settings.storage.s3_bucket}")
        console.print(f"[dim]S3 Region:[/dim] {settings.storage.s3_region}")
        console.print(f"[dim]S3 Endpoint:[/dim] {settings.storage.s3_endpoint_url or 'Default (AWS)'}")
    console.print()

    try:
        # Initialize storage adapter
        console.print("[1/5] [cyan]Initializing storage adapter...[/cyan]")
        adapter = get_storage_adapter()
        console.print("    [green]✓ Storage adapter initialized[/green]")

        # Prepare test data
        test_file_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_path = f"cli-test/{test_file_name}"
        test_content = f"Storage test from CLI at {datetime.now().isoformat()}".encode()

        # Upload test file
        console.print(f"[2/5] [cyan]Uploading test file: {test_path}...[/cyan]")
        uploaded_path = await adapter.upload(
            file_content=test_content,
            destination_path=test_path,
            content_type="text/plain",
            metadata={"test": "true", "source": "cli"},
        )
        console.print(f"    [green]✓ File uploaded: {uploaded_path}[/green]")

        # Check if file exists
        console.print("[3/5] [cyan]Checking if file exists...[/cyan]")
        exists = await adapter.exists(test_path)
        if exists:
            console.print("    [green]✓ File exists[/green]")
        else:
            console.print("    [red]✗ File not found![/red]")
            raise Exception("Uploaded file not found")

        # Download and verify
        console.print("[4/5] [cyan]Downloading and verifying content...[/cyan]")
        downloaded_content = await adapter.download(test_path)
        if downloaded_content == test_content:
            console.print("    [green]✓ Content verified successfully[/green]")
        else:
            console.print("    [red]✗ Content mismatch![/red]")
            raise Exception("Downloaded content doesn't match uploaded content")

        # Get URL (if supported)
        try:
            url = await adapter.get_url(test_path)
            console.print(f"    [dim]File URL: {url[:80]}...[/dim]")
        except NotImplementedError:
            console.print("    [dim]URL generation not supported for this adapter[/dim]")

        # Cleanup
        if not skip_cleanup:
            console.print(f"[5/5] [cyan]Cleaning up test file...[/cyan]")
            deleted = await adapter.delete(test_path)
            if deleted:
                console.print("    [green]✓ Test file deleted[/green]")
            else:
                console.print("    [yellow]⚠ Failed to delete test file[/yellow]")
        else:
            console.print(f"[5/5] [yellow]Skipping cleanup (file kept): {test_path}[/yellow]")

        # Success summary
        console.print()
        console.print("[bold green]✓ All storage tests passed successfully![/bold green]")
        console.print()

    except ImportError as e:
        console.print()
        console.print(f"[bold red]✗ Storage adapter dependencies missing![/bold red]")
        console.print(f"[dim]Error: {e}[/dim]")
        if settings.storage.type == "s3":
            console.print()
            console.print("[yellow]To use S3 storage, install required dependencies:[/yellow]")
            console.print("[cyan]  pip install aioboto3[/cyan]")
        console.print()
        raise typer.Exit(1)

    except Exception as e:
        console.print()
        console.print(f"[bold red]✗ Storage test failed![/bold red]")
        console.print(f"[dim]Error: {e}[/dim]")
        console.print()

        # Provide helpful troubleshooting tips
        if settings.storage.type == "s3":
            console.print("[yellow]Troubleshooting tips:[/yellow]")
            console.print("  • Verify S3 credentials are correct")
            console.print("  • Check bucket exists and is accessible")
            console.print("  • Verify network connectivity to S3 endpoint")
            console.print("  • Check IAM permissions for the access key")

        console.print()
        raise typer.Exit(1)
