"""
Init command implementation - Interactive GTM project creation
"""

import asyncio
import time
from typing import Optional
import typer
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text

from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain
from cli.utils.editor import detect_editor, open_file_in_editor
from cli.utils.console import enter_immersive_mode, exit_immersive_mode

console = Console()

# Import the new sync implementation
from cli.commands.init_sync import init_sync_flow

async def init_interactive_flow(
    domain: str, 
    context: Optional[str] = None, 
    yolo: bool = False
) -> None:
    """Run the interactive GTM generation flow"""
    
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
        # Enter immersive mode for existing projects
        enter_immersive_mode()
        console.print()
        
        # Get more detailed status info
        metadata = gtm_service.storage.load_metadata(normalized_domain)
        last_updated = metadata.updated_at if metadata else "Unknown"
        
        console.print(Panel.fit(
            f"[bold blue]Project already exists for {normalized_domain}[/bold blue]\n\n"
            f"[bold]Current Status:[/bold]\n"
            f"• Completed steps: [green]{', '.join(status['available_steps'])}[/green]\n"
            f"• Progress: [cyan]{status['progress_percentage']:.0f}%[/cyan] complete\n"
            f"• Last updated: [dim]{last_updated}[/dim]\n\n"
            f"{'• [yellow]Some data is stale[/yellow]' if status.get('has_stale_data') else '• [green]All data is current[/green]'}",
            title="[bold]Existing Project Found[/bold]",
            border_style="blue"
        ))
        
        if not yolo:
            try:
                update_project = questionary.confirm(
                    f"Project '{normalized_domain}' already exists. Would you like to update it with fresh data?",
                    default=None
                ).ask()
            except Exception as e:
                # Fallback to simple input when questionary fails
                console.print(f"Project '{normalized_domain}' already exists.")
                response = typer.confirm("Would you like to update it with fresh data?", default=None)
                update_project = response
            
            if not update_project:
                console.print("Operation cancelled.")
                return
            
            force_regenerate = True
        else:
            # In YOLO mode, default to regenerating all for fresh data
            console.print("[blue]YOLO mode: Will update with fresh website data[/blue]")
            force_regenerate = True
    else:
        force_regenerate = False
    
    # Welcome message
    if not yolo:
        # Enter immersive mode for new projects
        enter_immersive_mode()
        console.print()
        console.print(Panel.fit(
            f"[bold blue]🚀 Starting GTM Generation for {normalized_domain}[/bold blue]\n\n"
            "This will create a complete go-to-market package:\n"
            "• [green]1/5[/green] Company Overview\n"
            "• [green]2/5[/green] Target Account Profile\n" 
            "• [green]3/5[/green] Buyer Persona\n"
            "• [green]4/5[/green] Email Campaign\n"
            "• [dim]5/5[/dim] GTM Plan (coming soon)",
            title="[bold]GTM Generation Flow[/bold]",
            border_style="blue"
        ))
    
    try:
        # Step 1: Company Overview
        await run_step_with_choices(
            step_name="Company Overview",
            step_number=1,
            total_steps=4,
            generate_func=lambda: gtm_service.generate_company_overview(
                normalized_domain, context, force_regenerate
            ),
            domain=normalized_domain,
            step_key="overview",
            yolo=yolo
        )
        
        # Step 2: Target Account
        await run_step_with_choices(
            step_name="Target Account Profile", 
            step_number=2,
            total_steps=4,
            generate_func=lambda: gtm_service.generate_target_account(
                normalized_domain, force_regenerate=force_regenerate
            ),
            domain=normalized_domain,
            step_key="account",
            yolo=yolo
        )
        
        # Step 3: Buyer Persona
        await run_step_with_choices(
            step_name="Buyer Persona",
            step_number=3, 
            total_steps=4,
            generate_func=lambda: gtm_service.generate_target_persona(
                normalized_domain, force_regenerate=force_regenerate
            ),
            domain=normalized_domain,
            step_key="persona",
            yolo=yolo
        )
        
        # Step 4: Email Campaign
        await run_step_with_choices(
            step_name="Email Campaign",
            step_number=4,
            total_steps=4,
            generate_func=lambda: gtm_service.generate_email_campaign(
                normalized_domain, force_regenerate=force_regenerate
            ),
            domain=normalized_domain,
            step_key="email",
            yolo=yolo
        )
        
        # Completion message
        console.print()
        console.print(Panel.fit(
            "[bold green]✓ GTM Generation Complete![/bold green]\n\n"
            "[bold]Next steps:[/bold]\n"
            f"• View results: [cyan]blossomer show all[/cyan]\n"
            f"• Export report: [cyan]blossomer export[/cyan]\n"
            f"• Edit content: [cyan]blossomer edit <step>[/cyan]",
            title="[bold]Success[/bold]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted. Progress has been saved.[/yellow]")
        console.print("→ Resume with: [cyan]blossomer init " + domain + "[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("→ Try: [cyan]blossomer init " + domain + "[/cyan] to resume")
        raise typer.Exit(1)


async def run_step_with_choices(
    step_name: str,
    step_number: int, 
    total_steps: int,
    generate_func,
    domain: str,
    step_key: str,
    yolo: bool = False
) -> None:
    """Run a single step with user choice handling"""
    
    # Check if step already exists and is not stale
    existing_data = gtm_service.storage.load_step_data(domain, step_key)
    if existing_data and not existing_data.get("_stale") and not yolo:
        console.print(f"\n[{step_number}/4] [blue]{step_name}[/blue] - [green]Already exists[/green]")
        
        try:
            action = questionary.select(
                f"What would you like to do with existing {step_name.lower()}?",
                choices=[
                    "Continue (use existing)",
                    "Edit in system editor", 
                    "Regenerate",
                    "Abort"
                ]
            ).ask()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        
        if action == "Abort":
            raise KeyboardInterrupt()
        elif action == "Edit in system editor":
            await edit_step_data(domain, step_key, step_name)
            return
        elif action == "Continue (use existing)":
            return
        # If "Regenerate", continue to generation
    
    # Generate step with progress indicator
    console.print(f"\n[{step_number}/4] [blue]Generating {step_name}...[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        # Micro-progress indicators
        task = progress.add_task("→ Fetching website content...", total=None)
        await asyncio.sleep(0.1)  # Small delay for visual feedback
        
        progress.update(task, description="→ Processing with AI...")
        start_time = time.time()
        
        try:
            result = await generate_func()
            elapsed = time.time() - start_time
            
            progress.update(task, description=f"→ done ({elapsed:.1f}s)")
            progress.stop()
            
            # Success indicator
            console.print(f"   [green]✓[/green] {step_name} generated successfully")
            
        except Exception as e:
            progress.stop()
            console.print(f"   [red]✗[/red] Failed to generate {step_name}: {e}")
            
            if not yolo:
                retry = questionary.confirm("Would you like to retry this step?", default=None).ask()
                if retry:
                    await run_step_with_choices(
                        step_name, step_number, total_steps, 
                        generate_func, domain, step_key, yolo
                    )
                    return
            
            raise
    
    # Post-generation choices (if not in YOLO mode)
    if not yolo:
        try:
            action = questionary.select(
                f"What would you like to do with the generated {step_name.lower()}?",
                choices=[
                    "Continue to next step",
                    "Edit in system editor",
                    "Regenerate this step", 
                    "Abort"
                ]
            ).ask()
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        
        if action == "Abort":
            raise KeyboardInterrupt()
        elif action == "Edit in system editor":
            await edit_step_data(domain, step_key, step_name)
        elif action == "Regenerate this step":
            await run_step_with_choices(
                step_name, step_number, total_steps,
                generate_func, domain, step_key, yolo
            )


async def edit_step_data(domain: str, step_key: str, step_name: str) -> None:
    """Open step data in system editor for editing"""
    try:
        project_dir = gtm_service.storage.get_project_dir(domain)
        step_file = project_dir / f"{step_key}.json"
        
        if not step_file.exists():
            console.print(f"[red]Error:[/red] {step_name} file not found")
            return
        
        # Detect system editor
        editor = detect_editor()
        console.print(f"   [blue]→[/blue] Opening in {editor}...")
        
        # Open in editor
        success = open_file_in_editor(step_file, editor)
        
        if success:
            console.print(f"   [green]✓[/green] {step_name} updated")
            
            # Mark dependent steps as stale
            stale_steps = gtm_service.storage.mark_steps_stale(domain, step_key)
            if stale_steps:
                console.print(f"   [yellow]⚠️[/yellow] Marked dependent steps as stale: {', '.join(stale_steps)}")
        else:
            console.print(f"   [yellow]⚠️[/yellow] Editor closed without confirmation")
            
    except Exception as e:
        console.print(f"   [red]✗[/red] Failed to edit {step_name}: {e}")