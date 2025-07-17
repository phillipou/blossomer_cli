"""
Main CLI application entry point.
"""

# Suppress urllib3 OpenSSL warning for system Python compatibility - must be first
import warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+", category=UserWarning)

import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cli import __version__

# Initialize Typer app with rich markup support
app = typer.Typer(
    name="blossomer",
    help="🚀 Blossomer CLI - Generate complete GTM assets from domain analysis",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]Blossomer GTM CLI[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v",
        callback=version_callback,
        help="Show version and exit"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Enable verbose output with detailed timing"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug output (cache hits, timing details)"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", 
        "-q",
        help="Minimal output mode"
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output"
    ),
) -> None:
    """
    🚀 Blossomer GTM CLI - Generate complete go-to-market packages from domain analysis.
    
    Analyzes company domains and generates:
    • Company Overview
    • Target Account Profile
    • Buyer Persona  
    • Email Campaign
    • GTM Execution Plan
    
    Examples:
      blossomer init acme.com
      blossomer init acme.com --context "Series A startup"
      blossomer show all
      blossomer export
    """
    # Store global options in app state for access by commands
    app.state = {
        "verbose": verbose,
        "debug": debug,
        "quiet": quiet, 
        "no_color": no_color,
    }
    
    # Set debug mode for debug utilities
    if debug:
        from cli.utils.debug import set_debug_mode
        set_debug_mode(True)
    
    # Configure console for no-color mode
    if no_color:
        console._color_system = None


@app.command()
def init(
    domain: Optional[str] = typer.Argument(None, help="Company domain to analyze (e.g., acme.com)"),
    context: Optional[str] = typer.Option(None, "--context", help="Additional context about the company"),
    yolo: bool = typer.Option(False, "--yolo", help="Skip all interactions (one-shot mode)"),
) -> None:
    """🚀 Start new GTM project (interactive by default)."""
    from cli.commands.init_sync import init_sync_flow
    
    try:
        init_sync_flow(domain, context, yolo)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(130)  # Standard exit code for Ctrl+C


@app.command()
def show(
    asset: str = typer.Argument("all", help="Asset to display: all, overview, account, persona, email, plan"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Specify domain (auto-detected if only one project)"),
) -> None:
    """📊 Display generated assets with formatting."""
    from cli.commands.show import show_assets
    
    show_assets(asset, json_output, domain)


@app.command()
def export(
    step: str = typer.Argument("all", help="Step to export: all, overview, account, persona, email"),
    output: Optional[str] = typer.Option(None, "--output", help="Custom output file path"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Specify domain (auto-detected if only one project)"),
) -> None:
    """📄 Export GTM assets as formatted markdown reports."""
    from cli.commands.export import export_assets
    
    export_assets(step, output, domain)


@app.command()
def generate(
    step: str = typer.Argument(..., help="Step to generate: overview, account, persona, email, plan"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Specify domain (auto-detected if only one project)"),
    force: bool = typer.Option(False, "--force", help="Force regeneration even if data exists"),
) -> None:
    """⚙️ Manually run or re-run a specific step."""
    from cli.commands.generate import generate_step
    
    try:
        asyncio.run(generate_step(step, domain, force))
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(130)


@app.command()
def edit(
    file: str = typer.Argument(..., help="File to edit: overview, account, persona, email, plan"),
) -> None:
    """✏️ Open generated file in system editor."""
    console.print("[red]Command not yet implemented[/red]")
    console.print(f"Would edit: {file}")


@app.command()
def list() -> None:
    """📁 Show all GTM projects."""
    console.print("[red]Command not yet implemented[/red]")


@app.command()
def status() -> None:
    """📈 Quick overview of all projects."""
    console.print("[red]Command not yet implemented[/red]")


# Add eval subcommand
from cli.commands.eval import app as eval_app
app.add_typer(eval_app, name="eval", help="🧪 Run evaluations on prompt templates")


# Demo function to test Rich formatting
@app.command(hidden=True)
def demo() -> None:
    """Demo Rich formatting capabilities."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]🚀 Blossomer GTM CLI[/bold blue]\n\n"
        "Rich formatting test:\n"
        "• [green]✓[/green] Colors working\n"
        "• [blue]✓[/blue] Emojis working\n" 
        "• [yellow]✓[/yellow] Panels working",
        title="[bold]Demo[/bold]",
        border_style="blue"
    ))
    console.print()
    
    # Test progress indicator style
    console.print("[1/5] 🔍 Analyzing company...")
    console.print("   → Fetching website content... ✓")
    console.print("   → Processing with AI... ✓")
    console.print("   → done (8s)")
    console.print()


def main():
    """Entry point for console script"""
    app()

if __name__ == "__main__":
    main()