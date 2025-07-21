"""
Init command implementation - Interactive GTM project creation
"""

import asyncio
import os
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
from cli.utils.console import enter_immersive_mode, exit_immersive_mode, ensure_breathing_room, clear_console
from cli.utils.guided_email_builder import GuidedEmailBuilder
from cli.utils.markdown_formatter import get_formatter
from cli.utils.colors import Colors, format_project_status, format_step_flow
from cli.utils.constants import MenuChoices, EmailGenerationMode
from cli.utils.step_config import step_manager
from cli.utils.panel_utils import create_step_panel_by_key, create_welcome_panel, create_status_panel, create_completion_panel
from cli.utils.preview_utils import show_step_preview, show_guided_email_preview
from cli.utils.loading_animation import LoadingAnimator
from rich.markdown import Markdown

console = Console()

# Questionary styling for better UX - using brand blue theme
MENU_STYLE = questionary.Style([
    ('question', 'bold #01A0E4'),           # Question text - brand blue
    ('pointer', 'bold #01A0E4'),            # Arrow pointer - brand blue
    ('highlighted', 'bold #01A0E4'),        # Currently selected item - brand blue
    ('selected', 'bold #01A0E4'),           # After selection - brand blue
    ('answer', 'bold #01A0E4')              # Final answer display - brand blue
])

# Text input styling for cyan user inputs
TEXT_INPUT_STYLE = questionary.Style([
    ('question', 'bold #01A0E4'),           # Question text - brand blue
    ('text', '#00BFFF'),                    # Text input - cyan
    ('answer', '#00BFFF')                   # Answer display - cyan
])

def show_menu_with_separator(question: str, choices: list, add_separator: bool = True):
    """Show a questionary menu with visual separator and consistent styling"""
    from cli.utils.menu_utils import show_menu_with_numbers
    
    result = show_menu_with_numbers(
        question,
        choices=choices,
        add_separator=add_separator
    )
    
    return result


def capture_hypotheses() -> dict:
    """Capture optional user hypotheses for target account and persona"""
    console.print()
    console.print("🎯 [bold #01A0E4]Optional Context (press Enter to skip)[/bold #01A0E4]")
    
    account_hypothesis = questionary.text(
        "💡 Target Account Hypothesis (optional - helps focus our analysis):",
        placeholder="e.g., Mid-market SaaS companies with 50-500 employees experiencing rapid growth",
        style=TEXT_INPUT_STYLE
    ).ask()
    
    # Handle CTRL+C (questionary returns None when interrupted)
    if account_hypothesis is None:
        raise KeyboardInterrupt()
    
    persona_hypothesis = questionary.text(
        "👤 Target Persona Hypothesis (optional - helps focus our analysis):",
        placeholder="e.g., CTOs and VP Engineering at fast-growing tech companies",
        style=TEXT_INPUT_STYLE
    ).ask()
    
    # Handle CTRL+C (questionary returns None when interrupted)
    if persona_hypothesis is None:
        raise KeyboardInterrupt()
    
    # Build context object
    context = {}
    if account_hypothesis and account_hypothesis.strip():
        context["account_hypothesis"] = account_hypothesis.strip()
    if persona_hypothesis and persona_hypothesis.strip():
        context["persona_hypothesis"] = persona_hypothesis.strip()
    
    if context:
        console.print()
        console.print("✓ Context captured.")
    
    return context if context else None


def create_init_welcome_panel() -> Panel:
    """Create a rich welcome panel for the init command"""
    welcome_text = Text()
    welcome_text.append("🚀 Welcome to ", style="bold")
    welcome_text.append("Blossomer CLI", style="bold #01A0E4")
    welcome_text.append("!\n\n", style="bold")
    welcome_text.append("Generate a complete go-to-market plan using our internal AI workflow.\n\n", style="")
    welcome_text.append("What you'll get:\n", style="bold")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Company Overview", style="bold #01A0E4")
    welcome_text.append(" - Deep business analysis\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Target Account Profile", style="bold #01A0E4")
    welcome_text.append(" - Ideal customer identification\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Buyer Persona", style="bold #01A0E4")
    welcome_text.append(" - Decision-maker profiles\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Email Campaign", style="bold #01A0E4")
    welcome_text.append(" - Personalized outreach\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("GTM Strategic Plan", style="bold #01A0E4")
    welcome_text.append(" - Execution framework\n\n", style="")
    welcome_text.append("Takes ~60 seconds. Let's get started!", style="dim italic")
    
    return Panel(
        welcome_text,
        title="[bold #01A0E4]Blossomer Command Line Tool[/bold #01A0E4]",
        border_style="#01A0E4",
        padding=(1, 2),
        expand=False
    )


def check_api_keys() -> tuple[bool, list[str]]:
    """Check if required API keys are configured.
    
    Returns:
        tuple: (all_keys_present: bool, missing_keys: list[str])
    """
    missing_keys = []
    
    # Check FIRECRAWL_API_KEY
    if not os.getenv("FIRECRAWL_API_KEY"):
        missing_keys.append("FIRECRAWL_API_KEY")
    
    # Check FORGE_API_KEY
    if not os.getenv("FORGE_API_KEY"):
        missing_keys.append("FORGE_API_KEY")
    
    return len(missing_keys) == 0, missing_keys


def create_api_key_setup_panel(missing_keys: list[str]) -> Panel:
    """Create a panel showing how to set up missing API keys"""
    setup_text = Text()
    setup_text.append("🔑 API Keys Required\n\n", style="bold red")
    setup_text.append("To use Blossomer CLI, you'll need the following API keys:\n\n", style="")
    
    for key in missing_keys:
        if key == "FIRECRAWL_API_KEY":
            setup_text.append("• ", style="dim")
            setup_text.append("FIRECRAWL_API_KEY", style="bold yellow")
            setup_text.append(" - For website analysis\n", style="")
            setup_text.append("  Get it from: ", style="dim")
            setup_text.append("https://firecrawl.dev\n\n", style="cyan underline")
        elif key == "FORGE_API_KEY":
            setup_text.append("• ", style="dim")
            setup_text.append("FORGE_API_KEY", style="bold yellow")
            setup_text.append(" - For AI processing\n", style="")
            setup_text.append("  Get it from: ", style="dim")
            setup_text.append("https://tensorblock.co\n\n", style="cyan underline")
    
    setup_text.append("Set them up:\n", style="bold")
    setup_text.append("1. Add to your shell profile (~/.bashrc or ~/.zshrc):\n", style="")
    for key in missing_keys:
        setup_text.append(f"   export {key}=your_key_here\n", style="cyan")
    setup_text.append("\n2. Then reload your shell:\n", style="")
    setup_text.append("   source ~/.bashrc  # or ~/.zshrc\n", style="cyan")
    setup_text.append("\n3. Or set temporarily for this session:\n", style="")
    for key in missing_keys:
        setup_text.append(f"   export {key}=your_key_here\n", style="cyan")
    
    return Panel(
        setup_text,
        title="[bold red]⚠️  Setup Required[/bold red]",
        border_style="red",
        padding=(1, 2),
        expand=False
    )


def init_flow(domain: Optional[str], context: Optional[str] = None, yolo: bool = False) -> None:
    """Run the interactive GTM generation flow"""
    
    # Check API keys first
    keys_present, missing_keys = check_api_keys()
    
    if not keys_present:
        # Show API key setup instructions
        console.print()
        console.print(create_api_key_setup_panel(missing_keys))
        console.print("[yellow]Please set up the required API keys and try again.[/yellow]")
        raise typer.Exit(1)
    
    # Show welcome panel first (unless domain is provided and we're going straight to generation)
    if domain is None and not yolo:
        enter_immersive_mode()
        console.print()
        console.print(create_init_welcome_panel())
    
    # Prompt for domain if not provided
    if domain is None:
        domain = questionary.text(
            "🔍 Enter your company's website to get started:",
            placeholder="e.g.,  stripe.com",
            style=TEXT_INPUT_STYLE
        ).ask()
        
        ensure_breathing_room(console)
        
        # Handle CTRL+C (questionary returns None when interrupted)
        if domain is None:
            raise KeyboardInterrupt()
        
        if not domain:
            console.print("[yellow]No domain provided. Exiting.[/yellow]")
            raise typer.Exit(1)
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        normalized_domain = normalized.url
    except Exception as e:
        console.print(Colors.format_error(f"Invalid domain format: {e}"))
        console.print("💡 Domain should be in format: company.com, https://company.com, or www.company.com")
        console.print(f"→ Try: {Colors.format_command('acme.com')} or {Colors.format_command('https://acme.com')}")
        console.print(f"→ Or get help: {Colors.format_command('blossomer --help')}")
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
    console.print(create_welcome_panel(normalized_domain))
    
    # Capture hypotheses (if not in YOLO mode and context not provided)
    hypothesis_context = None
    if not yolo and context is None:
        hypothesis_context = capture_hypotheses()
    elif context:
        hypothesis_context = {"general_context": context}
    
    if not yolo:
        ready = typer.confirm("🚀 Ready to start? (This will analyze your website and generate 4 GTM assets in ~60 seconds)", default=True)
        ensure_breathing_room(console)
        # Handle CTRL+C (typer.confirm returns None when interrupted)
        if ready is None:
            raise KeyboardInterrupt()
        if not ready:
            console.print("Operation cancelled.")
            return
    
    console.print()
    console.print("[dim]⏱️  Analyzing your website and generating insights - this takes about 30-60 seconds[/dim]")
    
    try:
        # Step 1: Company Overview
        # Convert hypothesis context to string format for company overview
        context_str = None
        if context:
            context_str = context
        elif hypothesis_context:
            context_parts = []
            if hypothesis_context.get("account_hypothesis"):
                context_parts.append(f"Target Account: {hypothesis_context['account_hypothesis']}")
            if hypothesis_context.get("persona_hypothesis"):
                context_parts.append(f"Target Persona: {hypothesis_context['persona_hypothesis']}")
            if hypothesis_context.get("general_context"):
                context_parts.append(hypothesis_context["general_context"])
            context_str = " | ".join(context_parts) if context_parts else None
        
        run_generation_step(
            step_name="Company Overview",
            step_number=1,
            explanation="Analyzing your website to understand your business, products, and value proposition",
            generate_func=lambda: run_async_generation(
                gtm_service.generate_company_overview(normalized_domain, context_str, True)
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
                gtm_service.generate_target_account(
                    normalized_domain, 
                    hypothesis=hypothesis_context.get("account_hypothesis") if hypothesis_context else None,
                    additional_context=hypothesis_context.get("general_context") if hypothesis_context else None,
                    force_regenerate=True
                )
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
                gtm_service.generate_target_persona(
                    normalized_domain, 
                    hypothesis=hypothesis_context.get("persona_hypothesis") if hypothesis_context else None,
                    additional_context=hypothesis_context.get("general_context") if hypothesis_context else None,
                    force_regenerate=True
                )
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
        
        # Step 5: GTM Strategic Plan
        plan_success = True
        try:
            run_generation_step(
                step_name="GTM Strategic Plan",
                step_number=5,
                explanation="Synthesizing comprehensive go-to-market strategy from your analysis",
                generate_func=lambda: run_async_generation(run_async_advisor_generation(normalized_domain)),
                domain=normalized_domain,
                step_key="plan",
                yolo=yolo
            )
        except Exception:
            plan_success = False
            # Don't re-raise - let the user see partial results
        
        # Success message - only if all steps succeeded
        console.print()
        console.print(create_completion_panel())
        
        # Next steps message - only show if plan step succeeded
        if plan_success:
            console.print()
            console.print("[bold #01A0E4]Next Steps[/bold #01A0E4]")
            console.print("This is of course just the tip of the iceberg! There's so much more to dive into including:")
            console.print("• How to incorporate other channels (LinkedIn, inbound leads, paid advertising)?")
            console.print("• How to analyze data and iterate on these campaigns?")
            console.print("• How to integrate this into your CRM and workflows?")
            console.print()
            console.print("If you need any additional help or want us to work with you hands-on, reach out to us at")
            console.print("[cyan]blossomer.io[/cyan] or contact our founder Phil ([cyan]phil@blossomer.io[/cyan]).")
        
        # Interactive completion - wait for user to press Enter
        console.print()
        try:
            input("Press Enter to finish and return to your terminal...")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print(f"\n{Colors.format_meta('Goodbye! 👋')}")
        
        # Exit immersive mode
        exit_immersive_mode()
        
    except KeyboardInterrupt:
        console.print(f"\n{Colors.format_warning('Operation Stopped. Progress saved 💾')}")
        console.print(f"→ Resume with: [bold #01A0E4]blossomer init {normalized_domain}[/bold #01A0E4]")
        console.print(f"→ Or view progress: [bold #01A0E4]blossomer show all[/bold #01A0E4]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("💡 Common issues: network connectivity, invalid domain, or API limits")
        console.print(f"→ Try again: [bold #01A0E4]blossomer init {normalized_domain}[/bold #01A0E4]")
        console.print(f"→ Check status: [bold #01A0E4]blossomer show all[/bold #01A0E4]")
        raise typer.Exit(1)


def handle_existing_project(domain: str, status: dict, yolo: bool) -> None:
    """Handle existing project confirmation"""
    
    # Enter immersive mode for existing projects too
    enter_immersive_mode()
    
    metadata = gtm_service.storage.load_metadata(domain)
    last_updated = metadata.updated_at if metadata else "Unknown"
    
    console.print()
    # Show project status in bordered panel
    status_with_metadata = dict(status)
    status_with_metadata['last_updated'] = last_updated
    console.print(create_status_panel(domain, status_with_metadata))
    
    if yolo:
        console.print(Colors.format_section("YOLO mode: Updating all steps with fresh data", "⚡"))
        start_from_step = "overview"
    else:
        console.print(f"Project '{domain}' already exists.")
        
        # Offer step selection menu
        choices = [
            MenuChoices.START_FRESH,
            MenuChoices.START_FROM_COMPANY,
            MenuChoices.START_FROM_ACCOUNT,
            MenuChoices.START_FROM_PERSONA,
            MenuChoices.START_FROM_EMAIL,
            MenuChoices.START_FROM_PLAN,
            MenuChoices.CANCEL
        ]
        
        choice = show_menu_with_separator(
            "🚀 Choose your starting point (we'll run all subsequent steps automatically):",
            choices=choices
        )
        
        if choice is None or choice == MenuChoices.CANCEL:
            console.print("Operation cancelled.")
            console.print(f"→ View current results: {Colors.format_command('blossomer show all')}")
            return
        else:
            # Get starting step from menu choice
            start_from_step = MenuChoices.get_starting_step(choice)
    
    console.print()
    console.print(f"→ Starting from {Colors.format_command(start_from_step)} step and running all subsequent steps")
    console.print()
    
    # Continue with generation flow - start from selected step and run all subsequent steps
    try:
        step_order = step_manager.get_step_keys()
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
            step_counter += 1
        
        # Step 5: GTM Strategic Plan
        plan_success = True
        if "plan" in steps_to_run:
            plan_success = run_plan_generation_step(
                domain=domain,
                yolo=yolo,
                step_counter=5  # Always show as step 5/5
            )
            step_counter += 1
        
        # Success message
        console.print()
        console.print(create_completion_panel())
        
        # Next steps message - only show if plan step succeeded
        if plan_success:
            console.print()
            console.print("[bold #01A0E4]Next Steps[/bold #01A0E4]")
            console.print("This is of course just the tip of the iceberg! There's so much more to dive into including:")
            console.print("• How to incorporate other channels (LinkedIn, inbound leads, paid advertising)?")
            console.print("• How to analyze data and iterate on these campaigns?")
            console.print("• How to integrate this into your CRM and workflows?")
            console.print()
            console.print("If you need any additional help or want us to work with you hands-on, reach out to us at")
            console.print("[cyan]blossomer.io[/cyan] or contact our founder Phil ([cyan]phil@blossomer.io[/cyan]).")
        
        # Interactive completion - wait for user to press Enter
        console.print()
        try:
            input("Press Enter to finish and return to your terminal...")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print(f"\n{Colors.format_meta('Goodbye! 👋')}")
        
        # Exit immersive mode
        exit_immersive_mode()
        
    except KeyboardInterrupt:
        console.print(f"\n{Colors.format_meta('Operation Stopped. Progress saved 💾')}")
        console.print(f"→ Resume with: [bold #01A0E4]blossomer init {domain}[/bold #01A0E4]")
        console.print(f"→ Or view progress: [bold #01A0E4]blossomer show all[/bold #01A0E4]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("💡 Common issues: network connectivity, invalid domain, or API limits")
        console.print(f"→ Try again: [bold #01A0E4]blossomer init {domain}[/bold #01A0E4]")
        console.print(f"→ Check status: [bold #01A0E4]blossomer show all[/bold #01A0E4]")


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
    
    # Clear screen before showing step panel for clean UX
    clear_console()
    
    # Create a bordered panel for each step using step manager
    console.print()
    # Find step config to use proper panel
    step_config = None
    for step in step_manager.steps:
        if step.name == step_name:
            step_config = step
            break
    
    if step_config:
        console.print(create_step_panel_by_key(step_config.key))
    else:
        # Fallback for unknown steps
        console.print(Panel(
            f"[bold #01A0E4][{step_number}/{step_manager.get_total_steps()}] {step_name}[/bold #01A0E4]\n"
            f"\n"
            f"{explanation}",
            border_style="#01A0E4",
            expand=False,
            padding=(1, 2)
        ))
    
    # Show animated loading messages during generation
    animator = LoadingAnimator(console)
    animator.start_animation(step_key)
    
    start_time = time.time()
    
    try:
        result = generate_func()
        elapsed = time.time() - start_time
        
        # Stop animation and show completion
        animator.stop()
        console.print(f"   {Colors.format_success(f'{step_name} generated successfully')} ({elapsed:.1f}s)")
        
    except Exception as e:
        animator.stop()
        console.print(f"   {Colors.format_error(f'Failed to generate {step_name}: {e}')}")
        raise
    
    console.print()
    
    # Post-generation choices (if not in YOLO mode)
    if not yolo:
        # Show preview for each step using generic preview function
        show_step_preview(domain, step_key)
        
        console.print(f"[green]✓[/green] {step_name} completed!")
        
        # No additional confirmation needed - preview functions handle user choices


def run_email_generation_step(domain: str, yolo: bool = False) -> None:
    """Run the email generation step with guided mode choice"""
    
    # Clear screen before showing step panel for clean UX
    clear_console()
    
    console.print()
    console.print(create_step_panel_by_key("email"))
    
    # Ask for mode choice (unless in YOLO mode)
    if not yolo:
        mode_choice = show_menu_with_separator(
            "📧 How would you like to create your email campaign?",
            choices=[
                MenuChoices.EMAIL_MODE_GUIDED,
                MenuChoices.EMAIL_MODE_AUTOMATIC
            ]
        )
        
        email_mode = MenuChoices.get_email_mode(mode_choice)
        is_guided = email_mode == EmailGenerationMode.GUIDED
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
        
        # Clear screen and show all completed steps before generation
        clear_console()
        builder._show_previous_steps()
        
        console.print()
        console.print("Generating your personalized email campaign... ", end="")
        
        # Generate email with guided preferences using animated loading
        animator = LoadingAnimator(console)
        animator.start_animation("email")
        
        start_time = time.time()
        
        try:
            result = run_async_generation(
                gtm_service.generate_email_campaign(domain, preferences=guided_preferences, force_regenerate=True)
            )
            elapsed = time.time() - start_time
            
            # Stop animation and show completion
            animator.stop()
            console.print(f"   {Colors.format_success('Email Campaign generated successfully')} ({elapsed:.1f}s)")
            
            # Show preview after guided generation
            if not yolo:
                show_step_preview(domain, "email")
            
        except Exception as e:
            animator.stop()
            console.print(f"   {Colors.format_error(f'Failed to generate Email Campaign: {e}')}")
            raise
        
        return  # Important: return here to avoid running automatic generation
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
        show_guided_email_preview(domain)
        console.print(f"[green]✓[/green] Email Campaign completed!")


# edit_step_content moved to preview_utils.py


def run_plan_generation_step(domain: str, yolo: bool = False, step_counter: int = 5) -> bool:
    """Run the GTM Strategic Plan generation step
    
    Returns:
        bool: True if generation succeeded, False if it failed
    """
    
    # Clear screen before showing step panel for clean UX (unless in YOLO mode)
    if not yolo:
        clear_console()
    
    console.print()
    console.print(create_step_panel_by_key("plan"))
    
    # In YOLO mode, skip the prompt and generate automatically
    if not yolo:
        generate_plan = show_menu_with_separator(
            "🎯 Would you like to generate a comprehensive GTM strategic plan?",
            choices=[
                "Yes, create strategic plan",
                "Skip for now"
            ]
        )
        
        if generate_plan == "Skip for now":
            console.print()
            console.print("[yellow]Skipping strategic plan generation.[/yellow]")
            console.print("→ You can generate it later with: [bold #01A0E4]blossomer advisor {domain}[/bold #01A0E4]")
            return False  # Return False when skipped
    
    console.print()
    
    # Generate the strategic plan directly (not using run_generation_step)
    try:
        from cli.services.llm_service import LLMClient
        from app.services.gtm_advisor_service import GTMAdvisorService
        
        # Create step panel
        step_name = "GTM Strategic Plan"
        console.print()
        console.print(f"[bold #01A0E4][{step_counter}/5] {step_name}[/bold #01A0E4]")
        console.print("Creating comprehensive go-to-market execution plan with scoring frameworks and tool recommendations")
        console.print()
        
        # Show animated loading for strategic plan generation
        animator = LoadingAnimator(console)
        animator.start_animation("plan")
        
        start_time = time.time()
        
        try:
            strategic_plan_content = run_async_generation(run_async_advisor_generation(domain))
            elapsed = time.time() - start_time
            
            # Stop animation and show completion
            animator.stop()
            console.print(f"   {Colors.format_success('GTM Strategic Plan generated successfully')} ({elapsed:.1f}s)")
            
        except Exception as e:
            animator.stop()
            console.print(f"   {Colors.format_error(f'Failed to generate GTM Strategic Plan: {e}')}")
            raise
        
        # Show strategic plan summary and preview (unless in YOLO mode)
        if not yolo:
            console.print()
            console.print("─" * 60)
            console.print()
            console.print("[bold #01A0E4]Strategic Plan Generated![/bold #01A0E4]")
            console.print()
            console.print("Your comprehensive GTM execution plan includes:")
            console.print("  • Lead scoring frameworks (account + contact)")
            console.print("  • Tool stack recommendations (9 categories)")
            console.print("  • Email methodology framework")
            console.print("  • Metrics interpretation guide")
            console.print("  • Implementation timeline")
            console.print()
            
            # Show 1600 character preview
            if strategic_plan_content and len(strategic_plan_content.strip()) > 0:
                preview = strategic_plan_content[:1600]
                if len(strategic_plan_content) > 1600:
                    preview += "..."
                console.print("[bold]Preview (first 1600 characters):[/bold]")
                console.print("─" * 40)
                console.print(preview)
                console.print("─" * 40)
                console.print()
            
            console.print("→ View your full plan in plans/gtm_plan.md")
        
        console.print()
        console.print(f"[green]✓[/green] {step_name} completed!")
        return True  # Return True on success
        
    except Exception as e:
        console.print(f"[red]Failed to generate strategic plan:[/red] {e}")
        console.print("→ You can try again later with: [bold #01A0E4]blossomer advisor {domain}[/bold #01A0E4]")
        return False  # Return False on failure


async def run_async_advisor_generation(domain: str):
    """Async wrapper for advisor generation"""
    from app.services.gtm_advisor_service import GTMAdvisorService
    from cli.utils.domain import normalize_domain
    
    # Normalize domain to ensure consistent format
    normalized = normalize_domain(domain)
    normalized_domain = normalized.domain  # Use just the domain part, not the full URL
    
    advisor_service = GTMAdvisorService()
    
    return await advisor_service.generate_strategic_plan(normalized_domain)


def run_async_generation(coro):
    """Run async generation function synchronously with 40s timeout"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Add 40-second timeout to all generation operations
        return loop.run_until_complete(asyncio.wait_for(coro, timeout=40.0))
    except asyncio.TimeoutError:
        raise TimeoutError("Operation timed out after 40 seconds. This may be due to high API load or network issues.")
    finally:
        loop.close()


# All preview functions have been replaced with generic show_step_preview and show_guided_email_preview