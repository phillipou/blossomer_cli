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
from cli.utils.console import enter_immersive_mode, exit_immersive_mode

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
    
    # Enter immersive mode - clear console for fresh experience
    enter_immersive_mode()
    
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
        ready = typer.confirm("Ready to start generation?", default=None)
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
            f"• View results: [cyan]blossomer show all[/cyan]\n"
            f"• Edit content: [cyan]blossomer edit <step>[/cyan]\n"
            f"• Export report: [cyan]blossomer export[/cyan]",
            title="[bold]Success[/bold]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted. Progress has been saved.[/yellow]")
        console.print(f"→ Resume with: [cyan]blossomer init {domain}[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print(f"→ Try again: [cyan]blossomer init {domain}[/cyan]")
        raise typer.Exit(1)


def handle_existing_project(domain: str, status: dict, yolo: bool) -> None:
    """Handle existing project confirmation"""
    
    # Enter immersive mode for existing projects too
    enter_immersive_mode()
    
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
        update_project = typer.confirm("Would you like to update it with fresh data?", default=None)
    
    if not update_project:
        console.print("Operation cancelled.")
        console.print(f"→ View current results: [cyan]blossomer show all[/cyan]")
        return
    
    console.print()
    console.print("[blue]→ Updating project with fresh website data[/blue]")
    console.print()
    
    # Continue with generation flow - run all steps with fresh data
    try:
        # Step 1: Company Overview
        run_generation_step(
            step_name="Company Overview",
            step_number=1,
            explanation="Analyzing your website to understand your business, products, and value proposition",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_company_overview(domain, None, True)
            ),
            domain=domain,
            step_key="overview",
            yolo=yolo
        )
        
        # Step 2: Target Account
        run_generation_step(
            step_name="Target Account Profile",
            step_number=2,
            explanation="Identifying your ideal customer companies based on your business analysis",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_target_account(domain, force_regenerate=True)
            ),
            domain=domain,
            step_key="account",
            yolo=yolo
        )
        
        # Step 3: Buyer Persona
        run_generation_step(
            step_name="Buyer Persona",
            step_number=3,
            explanation="Creating detailed profiles of decision-makers at your target companies",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_target_persona(domain, force_regenerate=True)
            ),
            domain=domain,
            step_key="persona",
            yolo=yolo
        )
        
        # Step 4: Email Campaign
        run_generation_step(
            step_name="Email Campaign",
            step_number=4,
            explanation="Crafting personalized outreach emails based on your analysis",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_email_campaign(domain, force_regenerate=True)
            ),
            domain=domain,
            step_key="email",
            yolo=yolo
        )
        
        # Success message
        console.print()
        console.print(Panel.fit(
            "[bold green]✅ GTM Generation Complete![/bold green]\n\n"
            "[bold]Your go-to-market package is ready:[/bold]\n"
            f"• View results: [cyan]blossomer show all[/cyan]\n"
            f"• Edit content: [cyan]blossomer edit <step>[/cyan]\n"
            f"• Export report: [cyan]blossomer export[/cyan]",
            title="[bold]Success[/bold]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted. Progress has been saved.[/yellow]")
        console.print(f"→ Resume with: [cyan]blossomer init {domain.replace('https://', '')}[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print(f"→ Try again: [cyan]blossomer init {domain.replace('https://', '')}[/cyan]")


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
        # Show preview for target account step
        if step_key == "account":
            show_target_account_preview(domain)
        
        console.print(f"[green]✓[/green] {step_name} completed!")
        
        # Simple continue confirmation instead of complex menu
        if step_number < 4:  # Not the last step
            continue_choice = typer.confirm("Continue to next step?", default=None)
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


def show_target_account_preview(domain: str) -> None:
    """Show target account preview with 3 options"""
    try:
        # Load the generated account data
        account_data = gtm_service.storage.load_step_data(domain, "account")
        if not account_data:
            return
        
        # Extract key information for preview
        profile_name = account_data.get("target_account_name", "Target Companies")
        description = account_data.get("target_account_description", "")
        firmographics = account_data.get("firmographics", {})
        rationale = account_data.get("target_account_rationale", [])
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("TARGET ACCOUNT - Quick Summary")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        console.print(f"Profile: {profile_name}")
        
        # Show size and geography if available
        size_info = []
        if "employees" in firmographics:
            size_info.append(f"{firmographics['employees']} employees")
        if "revenue" in firmographics:
            size_info.append(f"{firmographics['revenue']} revenue")
        if size_info:
            console.print(f"Size: {', '.join(size_info)}")
        
        if "geography" in firmographics and firmographics["geography"]:
            geo_list = firmographics["geography"]
            if isinstance(geo_list, list):
                console.print(f"Geography: {', '.join(geo_list)}")
        
        # Show rationale points (max 3)
        if rationale:
            console.print()
            console.print("Why this profile:")
            for point in rationale[:3]:
                console.print(f"• {point}")
        
        # Top Buying Signals placeholder
        buying_signals = account_data.get("buying_signals", [])
        if buying_signals:
            console.print()
            console.print("Top Buying Signals:")
            # Show top 3 high priority signals
            high_priority = [s for s in buying_signals if s.get("priority") == "high"]
            for signal in high_priority[:3]:
                console.print(f"• {signal.get('title', 'Signal')}")
        
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "account.json").stat().st_size / 1024
        console.print(f"✓ Full profile saved to: account.json ({file_size:.1f}KB)")
        console.print()
        
        # Options
        console.print("Options:")
        console.print("[C]ontinue to next step (or press Enter)")
        console.print("[E]dit full analysis in editor")
        console.print("[A]bort (or press Ctrl+C)")
        console.print()
        
        # Get user choice
        choice = questionary.select(
            "Choice [c/e/a]:",
            choices=[
                "Continue to next step",
                "Edit full analysis in editor", 
                "Abort"
            ]
        ).ask()
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full analysis in editor":
            edit_step_content(domain, "account", "Target Account Profile")
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            if not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to next step", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")