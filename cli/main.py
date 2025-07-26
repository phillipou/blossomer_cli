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
    no_args_is_help=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]Blossomer GTM CLI[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


def create_main_welcome_panel() -> Panel:
    """Create a rich welcome panel for the main blossomer command"""
    welcome_text = Text()
    welcome_text.append("🚀 Welcome to ", style="bold")
    welcome_text.append("Blossomer CLI", style="bold #0066CC")
    welcome_text.append("!\n\n", style="bold")
    welcome_text.append("Generate complete go-to-market packages from domain analysis.\n\n", style="")
    welcome_text.append("Available Commands:\n", style="bold")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("init [domain]", style="bold #0066CC")
    welcome_text.append(" - Start new GTM project\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("show [step]", style="bold #0066CC")
    welcome_text.append(" - Display generated content\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("edit [step]", style="bold #0066CC")
    welcome_text.append(" - Open content in editor\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("list", style="bold #0066CC")
    welcome_text.append(" - Show all GTM projects\n\n", style="")
    welcome_text.append("Quick Start:\n", style="bold")
    welcome_text.append("  ", style="dim")
    welcome_text.append("blossomer init acme.com", style="#0066CC")
    welcome_text.append("\n\n", style="")
    welcome_text.append("Use ", style="dim italic")
    welcome_text.append("--help", style="#0066CC")
    welcome_text.append(" with any command for more details.", style="dim italic")
    
    return Panel(
        welcome_text,
        title="[bold #0066CC]Blossomer Command Line Tool[/bold #0066CC]",
        border_style="#0066CC",
        padding=(1, 2),
        expand=False
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
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
      blossomer show plan
      blossomer show overview --domain acme.com
      blossomer show --step email --domain acme.com
      blossomer edit plan
      blossomer edit overview --domain acme.com
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
    
    # If no command was invoked, show the welcome panel
    if ctx.invoked_subcommand is None:
        console.print()
        console.print(create_main_welcome_panel())
        console.print()


@app.command()
def init(
    domain: Optional[str] = typer.Argument(None, help="Company domain to analyze (e.g., acme.com)"),
    context: Optional[str] = typer.Option(None, "--context", help="Additional context about the company"),
    yolo: bool = typer.Option(False, "--yolo", help="Skip all interactions (one-shot mode)"),
) -> None:
    """🚀 Start new GTM project (interactive by default)."""
    from cli.commands.init import init_flow
    
    try:
        init_flow(domain, context, yolo)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(130)  # Standard exit code for Ctrl+C


@app.command()
def show(
    step: Optional[str] = typer.Argument("strategy", help="Step to display: overview, account, persona, email, strategy"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Specify domain (auto-detected if only one project)"),
    step_option: Optional[str] = typer.Option(None, "--step", help="Step to display: overview, account, persona, email, strategy"),
) -> None:
    """📊 Display generated step with formatting."""
    from cli.commands.show import show_assets
    
    # Use --step option if provided, otherwise use argument
    actual_step = step_option if step_option is not None else step
    show_assets(actual_step, json_output, domain)




@app.command()
def edit(
    step: str = typer.Argument("strategy", help="Step to edit: overview, account, persona, email, strategy (default: strategy)"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Specify domain (auto-detected if only one project)"),
) -> None:
    """✏️ Open generated markdown file in system editor."""
    from cli.commands.edit_step import edit_step_command
    
    edit_step_command(step, domain)


@app.command()
def list(
    domain: Optional[str] = typer.Option(None, "--domain", help="Show files for specific domain only")
) -> None:
    """📁 Show all GTM projects and their files."""
    from cli.commands.list_projects import list_projects
    
    list_projects(domain)






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