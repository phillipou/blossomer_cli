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
from cli.utils.guided_email_builder import GuidedEmailBuilder
from cli.utils.markdown_formatter import get_formatter
from rich.markdown import Markdown

console = Console()


def init_sync_flow(domain: Optional[str], context: Optional[str] = None, yolo: bool = False) -> None:
    """Run the synchronous GTM generation flow with proper loading animations"""
    
    # Prompt for domain if not provided
    if domain is None:
        domain = questionary.text(
            "Enter the company domain to analyze:",
            placeholder="e.g., acme.com"
        ).ask()
        
        if not domain:
            console.print("[yellow]No domain provided. Exiting.[/yellow]")
            raise typer.Exit(1)
    
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
        run_email_generation_step(
            domain=normalized_domain,
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
        console.print(f"→ Resume with: [cyan]blossomer init[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("→ Try again: [cyan]blossomer init[/cyan]")
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
        console.print("[blue]YOLO mode: Updating all steps with fresh data[/blue]")
        start_from_step = "overview"
    else:
        console.print(f"Project '{domain}' already exists.")
        
        # Offer step selection menu
        choices = [
            "🔄 Start from beginning (all steps)",
            "📊 Start from Company Overview", 
            "🎯 Start from Target Account Profile",
            "👤 Start from Buyer Persona",
            "📧 Start from Email Campaign",
            "❌ Cancel (view existing results)"
        ]
        
        choice = questionary.select(
            "Where would you like to start updating?",
            choices=choices
        ).ask()
        
        if choice == "❌ Cancel (view existing results)":
            console.print("Operation cancelled.")
            console.print(f"→ View current results: [cyan]blossomer show all[/cyan]")
            return
        elif choice == "🔄 Start from beginning (all steps)":
            start_from_step = "overview"
        elif choice == "📊 Start from Company Overview":
            start_from_step = "overview"
        elif choice == "🎯 Start from Target Account Profile":
            start_from_step = "account"
        elif choice == "👤 Start from Buyer Persona":
            start_from_step = "persona"
        elif choice == "📧 Start from Email Campaign":
            start_from_step = "email"
    
    console.print()
    console.print(f"[blue]→ Starting from {start_from_step} step and running all subsequent steps[/blue]")
    console.print()
    
    # Continue with generation flow - start from selected step and run all subsequent steps
    try:
        step_order = ["overview", "account", "persona", "email"]
        start_index = step_order.index(start_from_step)
        steps_to_run = step_order[start_index:]
        
        step_counter = 1
        
        # Step 1: Company Overview
        if "overview" in steps_to_run:
            run_generation_step(
                step_name="Company Overview",
                step_number=step_counter,
                explanation="Analyzing your website to understand your business, products, and value proposition",
                generate_func=lambda: run_async_generation(
                    gtm_service.generate_company_overview(domain, None, True)
                ),
                domain=domain,
                step_key="overview",
                yolo=yolo
            )
            step_counter += 1
        
        # Step 2: Target Account
        if "account" in steps_to_run:
            run_generation_step(
                step_name="Target Account Profile",
                step_number=step_counter,
                explanation="Identifying your ideal customer companies based on your business analysis",
                generate_func=lambda: run_async_generation(
                    gtm_service.generate_target_account(domain, force_regenerate=True)
                ),
                domain=domain,
                step_key="account",
                yolo=yolo
            )
            step_counter += 1
        
        # Step 3: Buyer Persona
        if "persona" in steps_to_run:
            run_generation_step(
                step_name="Buyer Persona",
                step_number=step_counter,
                explanation="Creating detailed profiles of decision-makers at your target companies",
                generate_func=lambda: run_async_generation(
                    gtm_service.generate_target_persona(domain, force_regenerate=True)
                ),
                domain=domain,
                step_key="persona",
                yolo=yolo
            )
            step_counter += 1
        
        # Step 4: Email Campaign
        if "email" in steps_to_run:
            run_email_generation_step(
                domain=domain,
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
        console.print("→ Resume with: [cyan]blossomer init[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("→ Try again: [cyan]blossomer init[/cyan]")


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
        # Show preview for each step - preview functions handle user choices internally
        if step_key == "overview":
            show_company_overview_preview(domain)
        elif step_key == "account":
            show_target_account_preview(domain)
        elif step_key == "persona":
            show_buyer_persona_preview(domain)
        elif step_key == "email":
            show_email_campaign_preview(domain)
        
        console.print(f"[green]✓[/green] {step_name} completed!")
        
        # No additional confirmation needed - preview functions handle user choices


def run_email_generation_step(domain: str, yolo: bool = False) -> None:
    """Run the email generation step with guided mode choice"""
    
    console.print(f"[bold][4/4] Email Campaign[/bold]")
    console.print(f"[dim]Crafting personalized outreach emails based on your analysis[/dim]")
    console.print()
    
    # Ask for mode choice (unless in YOLO mode)
    if not yolo:
        console.print("Generate email automatically or go through guided email builder?")
        mode_choice = questionary.select(
            "Choose mode:",
            choices=[
                "Guided (interactive email builder)",
                "Automatic (generate based on analysis)"
            ]
        ).ask()
        
        is_guided = mode_choice.startswith("Guided")
    else:
        is_guided = False
    
    console.print()
    
    if is_guided:
        # Load persona and account data for guided builder
        persona_data = gtm_service.storage.load_step_data(domain, "persona")
        account_data = gtm_service.storage.load_step_data(domain, "account")
        
        # Run the guided email builder
        builder = GuidedEmailBuilder(persona_data, account_data)
        guided_preferences = builder.run_guided_flow()
        
        console.print()
        console.print("Generating your personalized email campaign... ", end="")
        
        # Generate email with guided preferences
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            task = progress.add_task("→ Processing guided choices...", total=None)
            start_time = time.time()
            
            try:
                result = run_async_generation(
                    gtm_service.generate_email_campaign(domain, preferences=guided_preferences, force_regenerate=True)
                )
                elapsed = time.time() - start_time
                
                progress.update(task, description=f"→ completed in {elapsed:.1f}s")
                progress.stop()
                
                console.print(f"   [green]✓[/green] Email Campaign generated successfully")
                
            except Exception as e:
                progress.stop()
                console.print(f"   [red]✗[/red] Failed to generate Email Campaign: {e}")
                raise
    else:
        # Use the original automatic generation
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
        return  # Return early since run_generation_step handles the preview
    
    console.print()
    
    # Show preview for guided mode (automatic mode handled by run_generation_step)
    if not yolo:
        show_guided_email_campaign_preview(domain)
        console.print(f"[green]✓[/green] Email Campaign completed!")


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
        
        # Use markdown formatter for preview
        formatter = get_formatter('account')
        preview_markdown = formatter.format(account_data, preview=True, max_chars=400)
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("TARGET ACCOUNT - PREVIEW")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Display raw markdown content without Rich's markdown rendering
        console.print(preview_markdown)
        
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "account.json").stat().st_size / 1024
        console.print(f"✓ Full profile saved to: account.json ({file_size:.1f}KB)")
        console.print()
        print()  # Add extra space before menu
        print()  # Add more space before menu  
        
        # Get user choice
        choice = questionary.select(
            "What would you like to do?",
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


def show_company_overview_preview(domain: str) -> None:
    """Show company overview preview with 3 options"""
    try:
        # Load the generated overview data
        overview_data = gtm_service.storage.load_step_data(domain, "overview")
        if not overview_data:
            return
        
        # Use markdown formatter for preview (same as before)
        formatter = get_formatter('overview')
        preview_markdown = formatter.format(overview_data, preview=True, max_chars=400)
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("COMPANY OVERVIEW - Quick Summary")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Display raw markdown content without Rich's markdown rendering
        console.print(preview_markdown)
        
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "overview.json").stat().st_size / 1024
        console.print(f"✓ Full overview saved to: overview.json ({file_size:.1f}KB)")
        console.print()
        print()  # Add extra space before menu
        print()  # Add more space before menu  
        
        # Get user choice
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Continue to next step",
                "Edit full analysis in editor", 
                "Abort"
            ]
        ).ask()
        
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full analysis in editor":
            edit_step_content(domain, "overview", "Company Overview")
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            if not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to next step", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")


def show_buyer_persona_preview(domain: str) -> None:
    """Show buyer persona preview with 3 options"""
    try:
        # Load the generated persona data
        persona_data = gtm_service.storage.load_step_data(domain, "persona")
        if not persona_data:
            return
        
        # Use markdown formatter for preview
        formatter = get_formatter('persona')
        preview_markdown = formatter.format(persona_data, preview=True, max_chars=400)
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("BUYER PERSONA - PREVIEW")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Display raw markdown content without Rich's markdown rendering
        console.print(preview_markdown)
        
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "persona.json").stat().st_size / 1024
        console.print(f"✓ Full persona saved to: persona.json ({file_size:.1f}KB)")
        console.print()
        print()  # Add extra space before menu
        print()  # Add more space before menu  
        
        # Get user choice
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Continue to next step",
                "Edit full analysis in editor", 
                "Abort"
            ]
        ).ask()
        
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full analysis in editor":
            edit_step_content(domain, "persona", "Buyer Persona")
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            if not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to next step", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")


def show_email_campaign_preview(domain: str) -> None:
    """Show email campaign preview with 3 options"""
    try:
        # Load the generated email data
        email_data = gtm_service.storage.load_step_data(domain, "email")
        if not email_data:
            return
        
        # Use markdown formatter for preview
        formatter = get_formatter('email')
        preview_markdown = formatter.format(email_data, preview=True, max_chars=400)
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("EMAIL CAMPAIGN - PREVIEW")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Display raw markdown content without Rich's markdown rendering
        console.print(preview_markdown)
        
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "email.json").stat().st_size / 1024
        console.print(f"✓ Full campaign saved to: email.json ({file_size:.1f}KB)")
        console.print()
        
        
        # Get user choice
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Complete generation",
                "Edit full campaign in editor", 
                "Abort"
            ]
        ).ask()
        
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full campaign in editor":
            edit_step_content(domain, "email", "Email Campaign")
            # After editing, just continue to completion
            console.print()
        # If "Complete generation", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")


def show_guided_email_campaign_preview(domain: str) -> None:
    """Show enhanced email campaign preview for guided mode"""
    try:
        # Load the generated email data
        email_data = gtm_service.storage.load_step_data(domain, "email")
        if not email_data:
            return
        
        # Create enhanced preview based on PRD spec
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("EMAIL CAMPAIGN - Preview")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Show main email content
        emails = email_data.get("emails", [])
        if emails:
            first_email = emails[0]
            subject = first_email.get("subject", "Your personalized subject line")
            body = first_email.get("body", "Your personalized email content")
            
            console.print(f"Subject: {subject}")
            console.print()
            console.print("Hi {{FirstName}},")
            console.print()
            
            # Show a preview of the body (first few lines)
            body_lines = body.split('\n')[:4]
            for line in body_lines:
                console.print(line)
            
            if len(body.split('\n')) > 4:
                console.print("...")
            
            console.print()
            console.print("Best,")
            console.print("{{Your name}}")
            
            # Show alternative subjects if available
            alt_subjects = first_email.get("alternative_subjects", [])
            if alt_subjects:
                console.print()
                console.print("Alternative subjects:")
                for alt in alt_subjects[:2]:
                    console.print(f'- "{alt}"')
        
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        file_size = (project_dir / "email.json").stat().st_size / 1024
        console.print(f"✓ Full campaign saved to: email.json ({file_size:.1f}KB)")
        console.print()
        
        # Get user choice
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Continue to GTM plan",
                "Edit full campaign in editor", 
                "Abort"
            ]
        ).ask()
        
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full campaign in editor":
            edit_step_content(domain, "email", "Email Campaign")
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            if not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to GTM plan", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")