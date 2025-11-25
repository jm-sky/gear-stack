"""Storage commands for testing and management.

This module provides commands for testing storage adapters (local and S3).
"""

import asyncio
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.core.config import settings
from app.core.storage.factory import get_storage_adapter

# Create storage subcommand app
storage_app = typer.Typer(
    name="storage",
    help="Storage management and testing commands",
    no_args_is_help=True,
)

console = Console()


@storage_app.command("info")
def storage_info() -> None:
    """Display current storage configuration.

    Shows the configured storage type and relevant settings.

    Examples:
        python -m cli storage info
    """
    console.print("\n[bold cyan]Storage Configuration[/bold cyan]")
    console.print("=" * 50)

    # Create info table
    table = Table(show_header=False, box=None)
    table.add_column("Setting", style="cyan", width=25)
    table.add_column("Value", style="yellow")

    table.add_row("Storage Type", settings.storage.type)
    table.add_row("Base URL", settings.storage.base_url or "[dim]Not set[/dim]")

    if settings.storage.type == "local":
        table.add_row("Local Path", settings.storage.local_path)
    elif settings.storage.type == "s3":
        table.add_row("S3 Bucket", settings.storage.s3_bucket)
        table.add_row("S3 Region", settings.storage.s3_region)
        table.add_row("S3 Access Key", f"{settings.storage.s3_access_key[:8]}..." if settings.storage.s3_access_key else "[dim]Not set[/dim]")
        table.add_row("S3 Endpoint", settings.storage.s3_endpoint_url or "[dim]Default (AWS)[/dim]")

    table.add_row("Max File Size", f"{settings.storage.max_file_size / 1024 / 1024:.1f} MB")
    table.add_row("Max Files/Item", str(settings.storage.max_files_per_item))
    table.add_row("Image Processing", "Enabled" if settings.storage.enable_processing else "Disabled")

    console.print(table)
    console.print()


@storage_app.command("test")
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
        python -m cli storage test
        python -m cli storage test --skip-cleanup
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
