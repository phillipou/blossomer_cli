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
        
        # Extract key information for preview
        profile_name = account_data.get("target_account_name", "Target Companies")
        description = account_data.get("target_account_description", "")
        firmographics = account_data.get("firmographics", {})
        rationale = account_data.get("target_account_rationale", [])
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("TARGET ACCOUNT - Quick Summary [DUMMY DATA⚠️]")
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
        
        # Extract key information for preview
        product_name = overview_data.get("product_name", "Company Product")
        product_category = overview_data.get("product_category", "Business Solution")
        business_model = overview_data.get("business_model", "")
        key_capabilities = overview_data.get("key_capabilities", [])
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("COMPANY OVERVIEW - Quick Summary")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        console.print(f"Product: {product_name}")
        console.print(f"Category: {product_category}")
        if business_model:
            console.print(f"Model: {business_model}")
        
        # Show key capabilities (max 3)
        if key_capabilities:
            console.print()
            console.print("Key Capabilities:")
            for capability in key_capabilities[:3]:
                console.print(f"• {capability}")
        
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
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
        
        # Extract key information for preview
        job_title = persona_data.get("job_title", "Decision Maker")
        reports_to = persona_data.get("reports_to", "")
        team_size = persona_data.get("team_size", "")
        use_cases = persona_data.get("use_cases", [])
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("BUYER PERSONA - Quick Summary [DUMMY DATA⚠️]")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        console.print(f"Title: {job_title}")
        if reports_to:
            console.print(f"Reports to: {reports_to}")
        if team_size:
            console.print(f"Team: {team_size}")
        
        # Show use cases (max 3)
        if use_cases:
            console.print()
            console.print("Key Priorities:")
            for use_case in use_cases[:3]:
                if isinstance(use_case, dict):
                    title = use_case.get("use_case", use_case.get("title", "Priority"))
                else:
                    title = str(use_case)
                console.print(f"• {title}")
        
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
        
        # Extract key information for preview
        campaign_name = email_data.get("campaign_name", "Email Campaign")
        email_count = len(email_data.get("emails", []))
        campaign_strategy = email_data.get("campaign_strategy", {})
        
        # Create compact preview
        console.print()
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("EMAIL CAMPAIGN - Quick Summary [DUMMY DATA⚠️]")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        console.print(f"Campaign: {campaign_name}")
        console.print(f"Emails: {email_count} in sequence")
        
        # Show strategy highlights
        if campaign_strategy:
            tone = campaign_strategy.get("tone", "")
            approach = campaign_strategy.get("approach", "")
            if tone:
                console.print(f"Tone: {tone}")
            if approach:
                console.print(f"Approach: {approach}")
        
        # Show first email preview
        emails = email_data.get("emails", [])
        if emails:
            first_email = emails[0]
            subject = first_email.get("subject", "")
            if subject:
                console.print()
                console.print("First Email Preview:")
                console.print(f"• Subject: {subject}")
        
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