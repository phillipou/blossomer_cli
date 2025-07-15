"""
Synchronous Init command implementation - Clean user experience without async conflicts
"""

import asyncio
import time
import warnings
from typing import Optional
import typer
import questionary

# Suppress urllib3 OpenSSL warning for system Python compatibility
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+", category=UserWarning)
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text

from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain
from cli.utils.editor import detect_editor, open_file_in_editor

console = Console()


def init_sync_flow(domain: str, context: Optional[str] = None, yolo: bool = False) -> None:
    """Run the synchronous GTM generation flow with proper loading animations"""
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        normalized_domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        console.print("→ Try: acme.com or https://acme.com")
        raise typer.Exit(1)
    
    # Check if project already exists
    status = gtm_service.get_project_status(normalized_domain)
    if status["exists"]:
        handle_existing_project(normalized_domain, status, yolo)
        return
    
    # Welcome message for new project
    console.print()
    console.print(Panel.fit(
        f"[bold blue]🚀 Starting GTM Generation for {normalized_domain}[/bold blue]\n\n"
        "This will analyze your website and create:\n"
        "• [green]1/4[/green] Company Overview & Business Analysis\n"
        "• [green]2/4[/green] Target Account Profile\n" 
        "• [green]3/4[/green] Buyer Persona\n"
        "• [green]4/4[/green] Personalized Email Campaign",
        title="[bold]GTM Generation[/bold]",
        border_style="blue"
    ))
    
    if not yolo:
        ready = typer.confirm("Ready to start generation?")
        if not ready:
            console.print("Operation cancelled.")
            return
    
    console.print()
    console.print("[dim]→ This will take about 30-60 seconds[/dim]")
    console.print()
    
    try:
        # Step 1: Company Overview
        run_generation_step(
            step_name="Company Overview",
            step_number=1,
            explanation="Analyzing your website to understand your business, products, and value proposition",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_company_overview(normalized_domain, context, True)
            ),
            domain=normalized_domain,
            step_key="overview",
            yolo=yolo
        )
        
        # Step 2: Target Account
        run_generation_step(
            step_name="Target Account Profile",
            step_number=2,
            explanation="Identifying your ideal customer companies based on your business analysis",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_target_account(normalized_domain, force_regenerate=True)
            ),
            domain=normalized_domain,
            step_key="account",
            yolo=yolo
        )
        
        # Step 3: Buyer Persona
        run_generation_step(
            step_name="Buyer Persona",
            step_number=3,
            explanation="Creating detailed profiles of decision-makers at your target companies",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_target_persona(normalized_domain, force_regenerate=True)
            ),
            domain=normalized_domain,
            step_key="persona",
            yolo=yolo
        )
        
        # Step 4: Email Campaign
        run_generation_step(
            step_name="Email Campaign",
            step_number=4,
            explanation="Crafting personalized outreach emails based on your analysis",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_email_campaign(normalized_domain, force_regenerate=True)
            ),
            domain=normalized_domain,
            step_key="email",
            yolo=yolo
        )
        
        # Success message
        console.print()
        console.print(Panel.fit(
            "[bold green]✅ GTM Generation Complete![/bold green]\n\n"
            "[bold]Your go-to-market package is ready:[/bold]\n"
            f"• View results: [cyan]gtm-cli show all[/cyan]\n"
            f"• Edit content: [cyan]gtm-cli edit <step>[/cyan]\n"
            f"• Export report: [cyan]gtm-cli export[/cyan]",
            title="[bold]Success[/bold]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted. Progress has been saved.[/yellow]")
        console.print(f"→ Resume with: [cyan]gtm-cli init {domain}[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print(f"→ Try again: [cyan]gtm-cli init {domain}[/cyan]")
        raise typer.Exit(1)


def handle_existing_project(domain: str, status: dict, yolo: bool) -> None:
    """Handle existing project confirmation"""
    
    metadata = gtm_service.storage.load_metadata(domain)
    last_updated = metadata.updated_at if metadata else "Unknown"
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]Project already exists for {domain}[/bold blue]\n\n"
        f"[bold]Current Status:[/bold]\n"
        f"• Completed steps: [green]{', '.join(status['available_steps'])}[/green]\n"
        f"• Progress: [cyan]{status['progress_percentage']:.0f}%[/cyan] complete\n"
        f"• Last updated: [dim]{last_updated}[/dim]\n\n"
        f"{'• [yellow]Some data may be outdated[/yellow]' if status.get('has_stale_data') else '• [green]All data is current[/green]'}",
        title="[bold]Existing Project[/bold]",
        border_style="blue"
    ))
    
    if yolo:
        console.print("[blue]YOLO mode: Updating with fresh data[/blue]")
        update_project = True
    else:
        console.print(f"Project '{domain}' already exists.")
        update_project = typer.confirm("Would you like to update it with fresh data?")
    
    if not update_project:
        console.print("Operation cancelled.")
        console.print(f"→ View current results: [cyan]gtm-cli show all[/cyan]")
        return
    
    console.print()
    console.print("[blue]→ Updating project with fresh website data[/blue]")
    console.print()
    
    # Continue with generation flow...
    # (Reuse the same generation steps as above)


def run_generation_step(
    step_name: str,
    step_number: int,
    explanation: str,
    generate_func,
    domain: str,
    step_key: str,
    yolo: bool = False
) -> None:
    """Run a single generation step with proper loading and user interaction"""
    
    console.print(f"[bold][{step_number}/4] {step_name}[/bold]")
    console.print(f"[dim]{explanation}[/dim]")
    console.print()
    
    # Show loading animation during generation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        # Different phases of generation
        task = progress.add_task("→ Fetching website content...", total=None)
        time.sleep(0.5)  # Brief pause to show step
        
        progress.update(task, description="→ Analyzing with AI...")
        start_time = time.time()
        
        try:
            result = generate_func()
            elapsed = time.time() - start_time
            
            progress.update(task, description=f"→ completed in {elapsed:.1f}s")
            progress.stop()
            
            console.print(f"   [green]✓[/green] {step_name} generated successfully")
            
        except Exception as e:
            progress.stop()
            console.print(f"   [red]✗[/red] Failed to generate {step_name}: {e}")
            raise
    
    console.print()
    
    # Post-generation choices (if not in YOLO mode)
    if not yolo:
        console.print(f"[green]✓[/green] {step_name} completed!")
        
        # Simple continue confirmation instead of complex menu
        if step_number < 4:  # Not the last step
            continue_choice = typer.confirm("Continue to next step?", default=True)
            if not continue_choice:
                console.print("Generation paused. Resume with the same command.")
                raise KeyboardInterrupt()


def edit_step_content(domain: str, step_key: str, step_name: str) -> None:
    """Open step content in system editor"""
    try:
        project_dir = gtm_service.storage.get_project_dir(domain)
        step_file = project_dir / f"{step_key}.json"
        
        if not step_file.exists():
            console.print(f"[red]Error:[/red] {step_name} file not found")
            return
        
        editor = detect_editor()
        console.print(f"   [blue]→[/blue] Opening in {editor}...")
        
        success = open_file_in_editor(step_file, editor)
        
        if success:
            console.print(f"   [green]✓[/green] {step_name} updated")
            
            # Mark dependent steps as stale
            stale_steps = gtm_service.storage.mark_steps_stale(domain, step_key)
            if stale_steps:
                console.print(f"   [yellow]⚠️[/yellow] Dependent steps marked as stale: {', '.join(stale_steps)}")
        else:
            console.print(f"   [yellow]⚠️[/yellow] Editor closed")
            
    except Exception as e:
        console.print(f"   [red]✗[/red] Failed to edit {step_name}: {e}")


def run_async_generation(coro):
    """Run async generation function synchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()