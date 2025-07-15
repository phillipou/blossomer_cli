"""
Generate command implementation - Manually run or re-run specific GTM steps
"""

import asyncio
import time
from typing import Optional
import typer
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain

console = Console()


async def generate_step(
    step: str, 
    domain: Optional[str] = None,
    force: bool = False
) -> None:
    """Generate or regenerate a specific GTM step"""
    
    # Validate step
    valid_steps = ["overview", "account", "persona", "email", "plan"]
    if step not in valid_steps:
        console.print(f"[red]Invalid step: {step}[/red]")
        console.print(f"Valid steps: {', '.join(valid_steps)}")
        raise typer.Exit(1)
    
    # Get domain
    if not domain:
        projects = gtm_service.storage.list_projects()
        if not projects:
            console.print("[red]No GTM projects found.[/red]")
            console.print("→ Create one with: [cyan]blossomer init <domain>[/cyan]")
            raise typer.Exit(1)
        elif len(projects) == 1:
            domain = projects[0]["domain"]
        else:
            console.print("[red]Multiple projects found. Please specify domain:[/red]")
            for project in projects[:5]:
                console.print(f"  • {project['domain']}")
            console.print("→ Use: [cyan]blossomer generate {step} --domain <domain>[/cyan]")
            raise typer.Exit(1)
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        normalized_domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        raise typer.Exit(1)
    
    # Check if project exists
    status = gtm_service.get_project_status(normalized_domain)
    if not status["exists"]:
        console.print(f"[red]No GTM project found for {normalized_domain}[/red]")
        console.print("→ Create one with: [cyan]blossomer init " + domain + "[/cyan]")
        raise typer.Exit(1)
    
    # Check dependencies
    dependencies = gtm_service.storage.get_dependency_chain(normalized_domain)
    required_deps = dependencies.get(step, [])
    available_steps = status["available_steps"]
    
    missing_deps = [dep for dep in required_deps if dep not in available_steps]
    if missing_deps:
        console.print(f"[red]Missing dependencies for {step}:[/red] {', '.join(missing_deps)}")
        console.print("→ Generate dependencies first or run full flow with: [cyan]blossomer init " + domain + "[/cyan]")
        raise typer.Exit(1)
    
    # Check if step already exists
    existing_data = gtm_service.storage.load_step_data(normalized_domain, step)
    if existing_data and not force:
        console.print()
        
        status_text = ""
        if existing_data.get("_stale"):
            status_text = " [yellow](outdated)[/yellow]"
        
        console.print(Panel.fit(
            f"[yellow]{step.title()} already exists{status_text}[/yellow]\n\n"
            f"Generated: {existing_data.get('_generated_at', 'Unknown')}\n"
            "Use --force to regenerate anyway.",
            title="[bold]Existing Data[/bold]",
            border_style="yellow"
        ))
        
        action = questionary.select(
            f"What would you like to do?",
            choices=[
                "Regenerate anyway",
                "View current content",
                "Abort"
            ]
        ).ask()
        
        if action == "Abort":
            return
        elif action == "View current content":
            console.print(f"→ Use: [cyan]blossomer show {step}[/cyan]")
            return
        # If "Regenerate anyway", continue
    
    # Generate the step
    console.print()
    console.print(f"[blue]Generating {step.title()}...[/blue]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            
            task = progress.add_task("→ Processing with AI...", total=None)
            start_time = time.time()
            
            # Generate based on step type
            if step == "overview":
                result = await gtm_service.generate_company_overview(
                    normalized_domain, force_regenerate=True
                )
            elif step == "account":
                result = await gtm_service.generate_target_account(
                    normalized_domain, force_regenerate=True
                )
            elif step == "persona":
                result = await gtm_service.generate_target_persona(
                    normalized_domain, force_regenerate=True
                )
            elif step == "email":
                result = await gtm_service.generate_email_campaign(
                    normalized_domain, force_regenerate=True
                )
            elif step == "plan":
                # TODO: Implement GTM plan generation
                console.print("[yellow]GTM plan generation coming soon...[/yellow]")
                return
            
            elapsed = time.time() - start_time
            progress.update(task, description=f"→ done ({elapsed:.1f}s)")
            progress.stop()
        
        console.print(f"   [green]✓[/green] {step.title()} generated successfully")
        
        # Check for dependent steps that should be regenerated
        dependent_steps = gtm_service.storage.get_dependent_steps(step)
        available_dependents = [dep for dep in dependent_steps if dep in available_steps]
        
        if available_dependents:
            console.print()
            console.print(f"[yellow]⚠️  Dependent steps may need regeneration:[/yellow] {', '.join(available_dependents)}")
            
            regen_deps = questionary.confirm(
                "Would you like to regenerate dependent steps now?",
                default=None
            ).ask()
            
            if regen_deps:
                for dep_step in available_dependents:
                    console.print(f"\n[blue]Regenerating {dep_step.title()}...[/blue]")
                    await generate_step_internal(normalized_domain, dep_step)
        
        # Success message
        console.print()
        console.print(Panel.fit(
            f"[bold green]✓ {step.title()} Generation Complete![/bold green]\n\n"
            "[bold]Next steps:[/bold]\n"
            f"• View result: [cyan]blossomer show {step}[/cyan]\n"
            f"• Edit content: [cyan]blossomer edit {step}[/cyan]\n"
            f"• View all: [cyan]blossomer show all[/cyan]",
            title="[bold]Success[/bold]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"\n[red]Generation failed:[/red] {e}")
        console.print(f"→ Try again: [cyan]blossomer generate {step}[/cyan]")
        raise typer.Exit(1)


async def generate_step_internal(domain: str, step: str) -> None:
    """Internal function to generate a step without UI prompts"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        task = progress.add_task(f"→ Regenerating {step}...", total=None)
        start_time = time.time()
        
        try:
            if step == "overview":
                await gtm_service.generate_company_overview(domain, force_regenerate=True)
            elif step == "account":
                await gtm_service.generate_target_account(domain, force_regenerate=True)
            elif step == "persona":
                await gtm_service.generate_target_persona(domain, force_regenerate=True)
            elif step == "email":
                await gtm_service.generate_email_campaign(domain, force_regenerate=True)
            
            elapsed = time.time() - start_time
            progress.update(task, description=f"→ done ({elapsed:.1f}s)")
            console.print(f"   [green]✓[/green] {step.title()} regenerated")
            
        except Exception as e:
            progress.stop()
            console.print(f"   [red]✗[/red] Failed to regenerate {step}: {e}")
            raise