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

# Delay imports that might trigger client initialization
# from cli.services.gtm_generation_service import gtm_service
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

console = Console()

# Questionary styling for better UX - using brand blue theme with bold black selection
MENU_STYLE = questionary.Style([
    ('question', 'bold #0066CC'),           # Question text - brand blue
    ('pointer', 'bold #0066CC'),            # Arrow pointer - brand blue
    ('highlighted', 'bold black'),          # Currently focused item - bold black
    ('selected', 'bold black'),             # Selected item - bold black
    ('answer', 'bold #0066CC'),             # Final answer display - brand blue
    ('instruction', '#0066CC'),             # Instruction text
])

# Text input styling for brand blue user inputs
TEXT_INPUT_STYLE = questionary.Style([
    ('question', 'bold #0066CC'),        # Question text - brand blue
    ('text', 'bold black'),              # Text input - bold black for visibility
    ('answer', 'bold black')             # Answer display - bold black
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
    console.print("🧠 [bold #0066CC]Gathering Context (press Enter to skip)[/bold #0066CC]")
    console.print("Let's learn more about your business and your users. Provide anything you think will be relevant developing your go-to-market strategy.")
    console.print()
    
    account_hypothesis = questionary.text(
        "💼 What types of businesses buy your product/service? (press Enter to skip):",
        placeholder="e.g., Mid-market enterprises with complex procurement processes",
        style=TEXT_INPUT_STYLE
    ).ask()
    console.print()
    
    # Handle CTRL+C (questionary returns None when interrupted)
    if account_hypothesis is None:
        raise KeyboardInterrupt()
    
    persona_hypothesis = questionary.text(
        "👤 Who would most likely champion your product? (press Enter to skip):",
        placeholder="e.g., CTOs and VP Engineering with large teams",
        style=TEXT_INPUT_STYLE
    ).ask()
    console.print()

    extra_context = questionary.text(
        "💡 Is there anything else you'd like to add? (press Enter to skip):",
        placeholder="e.g. current plans, product roadmap, previous challenges, etc.",
        style=TEXT_INPUT_STYLE
    ).ask()
    console.print() 
    # Handle CTRL+C (questionary returns None when interrupted)
    if persona_hypothesis is None:
        raise KeyboardInterrupt()
    
    # Build context object
    context = {}
    if account_hypothesis and account_hypothesis.strip():
        context["account_hypothesis"] = account_hypothesis.strip()
    if persona_hypothesis and persona_hypothesis.strip():
        context["persona_hypothesis"] = persona_hypothesis.strip()
    if extra_context and extra_context.strip():
        context["extra_context"] = extra_context.strip()

    if context:
        console.print()
        console.print("✓ Context captured.")
    
    return context if context else None


def create_init_welcome_panel() -> Panel:
    """Create a rich welcome panel for the init command"""
    welcome_text = Text()
    welcome_text.append("🚀 Welcome to ", style="bold")
    welcome_text.append("Blossomer CLI", style="bold #0066CC")
    welcome_text.append("!\n\n", style="bold")
    welcome_text.append("Generate a complete go-to-market plan using our internal AI workflow.\n\n", style="")
    welcome_text.append("What you'll get:\n", style="bold")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Company Overview", style="bold #0066CC")
    welcome_text.append(" - An overview of your business and product\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Target Account Profile", style="bold #0066CC")
    welcome_text.append(" - A detailed hypothesis of businesses you should sell to\n", style="") 
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Buyer Persona", style="bold #0066CC")
    welcome_text.append(" - A detaield hypothesis of persona profiles who would champion your product\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("Email Campaign", style="bold #0066CC")
    welcome_text.append(" - A multi-step email campaign built using our best practices\n", style="")
    welcome_text.append("  • ", style="dim")
    welcome_text.append("GTM Strategic Plan", style="bold #0066CC")
    welcome_text.append(" - A complete plan to execute your go-to-market strategy\n\n", style="")
    welcome_text.append("Let's get started!", style="dim italic")
    
    return Panel(
        welcome_text,
        title="[bold #0066CC]Blossomer Command Line Tool[/bold #0066CC]",
        border_style="#0066CC",
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
    setup_text.append("👋 Welcome to Blossomer GTM CLI!\n\n", style="bold cyan")
    setup_text.append("It looks like you're missing some API keys. Let's get you set up!\n\n", style="")
    setup_text.append("Required API Keys:\n\n", style="bold")
    
    for key in missing_keys:
        if key == "FIRECRAWL_API_KEY":
            setup_text.append("🔥 ", style="")
            setup_text.append("Firecrawl API Key", style="bold #0066CC")
            setup_text.append(" - For website scraping\n", style="")
            setup_text.append("   Get yours at: ", style="dim")
            setup_text.append("https://firecrawl.dev", style="#0066CC underline")
            setup_text.append("\n\n")
        elif key == "FORGE_API_KEY":
            setup_text.append("📦 ", style="")
            setup_text.append("TensorBlock Forge API Key", style="bold #0066CC")
            setup_text.append(" - For AI model access (GPT-4, Claude, etc.)\n", style="")
            setup_text.append("   Get yours at: ", style="dim")
            setup_text.append("https://tensorblock.co", style="#0066CC underline")
            setup_text.append("\n\n")
    
    return Panel(
        setup_text,
        title="[bold #0066CC]First Time Setup[/bold #0066CC]",
        border_style="#0066CC",
        padding=(1, 2),
        expand=False
    )


def setup_api_keys_interactively(missing_keys: list[str]) -> bool:
    """Interactive API key setup. Returns True if setup completed."""
    console.print()
    console.print(create_api_key_setup_panel(missing_keys))
    
    # Ask if they want to set up now
    if not questionary.confirm(
        "Would you like to set up your API keys now?",
        default=True,
        style=questionary.Style([('question', 'bold #0066CC')])
    ).ask():
        console.print("\n[yellow]No problem! When you're ready:[/yellow]")
        console.print("\n  1. Get your API keys from the links above")
        console.print("  2. Set them as environment variables:")
        for key in missing_keys:
            console.print(f"     export {key}='your-key-here'")
        console.print("\n  3. Run [bold cyan]blossomer init[/bold cyan] again\n")
        return False
    
    # Collect missing keys
    console.print("\n[bold]Let's set up your keys:[/bold]\n")
    
    env_vars = []
    
    for key in missing_keys:
        if key == "FIRECRAWL_API_KEY":
            api_key = questionary.password(
                "🔥 Enter your Firecrawl API key:",
                validate=lambda x: len(x) > 0 or "API key cannot be empty"
            ).ask()
        elif key == "FORGE_API_KEY":
            api_key = questionary.password(
                "📦 Enter your TensorBlock API key:",
                validate=lambda x: len(x) > 0 or "API key cannot be empty"
            ).ask()
        
        if not api_key:
            console.print("[red]Setup cancelled.[/red]")
            return False
        
        # Set for current session
        os.environ[key] = api_key
        env_vars.append(f"export {key}='{api_key}'")
    
    # Success message
    console.print("\n[green]✅ API keys configured for this session![/green]\n")
    
    # Ask about .env file
    if questionary.confirm(
        "Would you like me to create a .env file to save these keys?",
        default=True,
        style=questionary.Style([('question', 'bold #0066CC')])
    ).ask():
        create_env_file(env_vars)
        console.print("[green]✅ Created .env file![/green]\n")
    else:
        console.print("[bold]To save permanently, add these to your shell config:[/bold]\n")
        for var in env_vars:
            console.print(f"  {var}")
        console.print()
    
    console.print("[bold #0066CC]🚀 You're all set! Let's continue...[/bold #0066CC]\n")
    return True


def create_env_file(env_vars: list) -> None:
    """Create or update .env file with API keys."""
    env_path = ".env"
    
    # Read existing content if file exists
    existing_content = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            existing_content = f.readlines()
    
    # Update or add new vars
    updated_content = []
    keys_to_add = {var.split('=')[0].replace('export ', ''): var for var in env_vars}
    
    for line in existing_content:
        key = line.split('=')[0].strip()
        if key in keys_to_add:
            # Update existing key
            updated_content.append(keys_to_add[key].replace('export ', '') + '\n')
            del keys_to_add[key]
        else:
            updated_content.append(line)
    
    # Add remaining new keys
    for var in keys_to_add.values():
        updated_content.append(var.replace('export ', '') + '\n')
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_content)


def init_flow(domain: Optional[str], context: Optional[str] = None, yolo: bool = False) -> None:
    """Run the interactive GTM generation flow"""
    
    # Check API keys first
    keys_present, missing_keys = check_api_keys()
    
    if not keys_present:
        # Try interactive setup
        if not setup_api_keys_interactively(missing_keys):
            raise typer.Exit(0)
    
    # Import gtm_service after API keys are confirmed
    from cli.services.gtm_generation_service import gtm_service
    
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
    console.print(create_welcome_panel(domain))
    
    # Capture hypotheses (if not in YOLO mode and context not provided)
    hypothesis_context = None
    if not yolo and context is None:
        hypothesis_context = capture_hypotheses()
    elif context:
        hypothesis_context = {"general_context": context}
    
    if not yolo:
        ready = typer.confirm("🚀 Ready to start? We're going to analyze your website to learn more about you", default=True)
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
                step_key="strategy",
                yolo=yolo
            )
        except Exception:
            plan_success = False
            # Don't re-raise - let the user see partial results
        
        # Success message - only if all steps succeeded
        console.print()
        console.print(create_completion_panel())
        
        # Next steps message removed - now shown after guided email builder completion
        
        # Interactive completion menu
        console.print()
        try:
            final_choice = show_menu_with_separator(
                "What would you like to do?",
                choices=[
                    "View plan",
                    "Edit plan", 
                    "Finish"
                ],
                add_separator=False
            )
            
            if final_choice == "View plan":
                # Open the plan file in the editor
                plan_path = gtm_service.storage.get_file_path(normalized_domain, "strategy")
                if plan_path.exists():
                    open_file_in_editor(str(plan_path))
                    console.print()
                    console.print("[green]✓[/green] Opened plan in your editor")
                    console.print()
                    # Show menu again
                    input("Press Enter to finish and return to your terminal...")
                else:
                    console.print("[yellow]Plan file not found[/yellow]")
                    input("Press Enter to finish and return to your terminal...")
                    
            elif final_choice == "Edit plan":
                # Edit the plan content
                from cli.utils.preview_utils import edit_step_content
                edit_step_content(normalized_domain, "strategy", "GTM Strategic Plan")
                console.print()
                # Show menu again
                input("Press Enter to finish and return to your terminal...")
                
            # If "Finish" is selected, just continue to exit
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print(f"\n{Colors.format_meta('Goodbye! 👋')}")
        
        # Exit immersive mode
        exit_immersive_mode()
        
    except KeyboardInterrupt:
        console.print(f"\n{Colors.format_warning('Operation Stopped. Progress saved 💾')}")
        console.print(f"→ Resume with: [bold #0066CC]blossomer init {domain}[/bold #0066CC]")
        console.print(f"→ Or view progress: [bold #0066CC]blossomer show all[/bold #0066CC]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("💡 Common issues: network connectivity, invalid domain, or API limits")
        console.print(f"→ Try again: [bold #0066CC]blossomer init {domain}[/bold #0066CC]")
        console.print(f"→ Check status: [bold #0066CC]blossomer show all[/bold #0066CC]")
        raise typer.Exit(1)


def handle_existing_project(domain: str, status: dict, yolo: bool) -> None:
    """Handle existing project confirmation"""
    
    # Enter immersive mode for existing projects too
    enter_immersive_mode()
    
    # Import gtm_service when needed
    from cli.services.gtm_generation_service import gtm_service
    
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
        console.print(f"Project already exists.")
        
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
            "🚀 Choose your starting point:",
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
        if "strategy" in steps_to_run:
            # Skip the prompt if we're only running the plan step (user selected "Jump to Step 5")
            # or if email step was just completed
            coming_from_email = "email" in steps_to_run or steps_to_run == ["strategy"]
            plan_success = run_plan_generation_step(
                domain=domain,
                yolo=yolo,
                step_counter=5,  # Always show as step 5/5
                coming_from_email=coming_from_email
            )
            step_counter += 1
        
        # Success message
        console.print()
        console.print(create_completion_panel())
        
        # Next steps message removed - now shown after guided email builder completion
        
        # Interactive completion menu
        console.print()
        try:
            final_choice = show_menu_with_separator(
                "What would you like to do?",
                choices=[
                    "View plan",
                    "Edit plan", 
                    "Finish"
                ],
                add_separator=False
            )
            
            if final_choice == "View plan":
                # Open the plan file in the editor
                plan_path = gtm_service.storage.get_file_path(domain, "strategy")
                if plan_path.exists():
                    open_file_in_editor(str(plan_path))
                    console.print()
                    console.print("[green]✓[/green] Opened plan in your editor")
                    console.print()
                    # Show menu again
                    input("Press Enter to finish and return to your terminal...")
                else:
                    console.print("[yellow]Plan file not found[/yellow]")
                    input("Press Enter to finish and return to your terminal...")
                    
            elif final_choice == "Edit plan":
                # Edit the plan content
                from cli.utils.preview_utils import edit_step_content
                edit_step_content(domain, "strategy", "GTM Strategic Plan")
                console.print()
                # Show menu again
                input("Press Enter to finish and return to your terminal...")
                
            # If "Finish" is selected, just continue to exit
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print(f"\n{Colors.format_meta('Goodbye! 👋')}")
        
        # Exit immersive mode
        exit_immersive_mode()
        
    except KeyboardInterrupt:
        console.print(f"\n{Colors.format_meta('Operation Stopped. Progress saved 💾')}")
        console.print(f"→ Resume with: [bold #0066CC]blossomer init {domain}[/bold #0066CC]")
        console.print(f"→ Or view progress: [bold #0066CC]blossomer show all[/bold #0066CC]")
    except Exception as e:
        console.print(f"\n[red]Error during generation:[/red] {e}")
        console.print("💡 Common issues: network connectivity, invalid domain, or API limits")
        console.print(f"→ Try again: [bold #0066CC]blossomer init {domain}[/bold #0066CC]")
        console.print(f"→ Check status: [bold #0066CC]blossomer show all[/bold #0066CC]")


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
            f"[bold #0066CC][{step_number}/{step_manager.get_total_steps()}] {step_name}[/bold #0066CC]\n"
            f"\n"
            f"{explanation}",
            border_style="#0066CC",
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
    
    # Import gtm_service when needed
    from cli.services.gtm_generation_service import gtm_service
    
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
    
    # Initialize guided preferences (will be set if guided mode is used)
    guided_preferences = None
    
    if is_guided:
        # Load persona and account data for guided builder
        persona_data = gtm_service.storage.load_step_data(domain, "persona")
        account_data = gtm_service.storage.load_step_data(domain, "account")
        
        # Check for missing dependencies and offer to generate them
        missing_steps = []
        if not account_data:
            missing_steps.append(("account", "Target Account Profile", 2))
        if not persona_data:
            missing_steps.append(("persona", "Buyer Persona", 3))
            
        if missing_steps:
            console.print()
            console.print(f"[yellow]⚠️  Guided email builder requires some previous steps to be completed first:[/yellow]")
            for step_key, step_name, step_num in missing_steps:
                console.print(f"   • Step {step_num}: {step_name}")
            console.print()
            
            import questionary
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    f"Generate missing steps first (recommended)",
                    f"Continue with automatic mode instead", 
                    f"Cancel and choose different starting point"
                ]
            ).ask()
            
            if choice == f"Generate missing steps first (recommended)":
                # Start from the earliest missing step
                earliest_step = missing_steps[0][0]  # Get step key
                console.print(f"→ Starting from {earliest_step} step to generate missing dependencies...")
                console.print()
                start_from_step = earliest_step
                is_guided = False  # We'll come back to guided mode after dependencies are generated
            elif choice == f"Continue with automatic mode instead":
                console.print("→ Switching to automatic email generation...")
                console.print()
                is_guided = False
            else:  # Cancel
                console.print("Operation cancelled.")
                console.print(f"→ Try: {Colors.format_command('blossomer init ' + domain)}")
                return
        
        # If we have all dependencies, run the guided email builder
        if is_guided:
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


def run_plan_generation_step(domain: str, yolo: bool = False, step_counter: int = 5, coming_from_email: bool = False) -> bool:
    """Run the GTM Strategic Plan generation step
    
    Args:
        domain: The domain being analyzed
        yolo: Whether in YOLO mode (auto-generate)
        step_counter: The step number for display
        coming_from_email: If True, skip the prompt and generate directly
    
    Returns:
        bool: True if generation succeeded, False if it failed
    """
    
    # Clear screen before showing step panel for clean UX
    clear_console()
    
    console.print()
    console.print(create_step_panel_by_key("strategy"))
    
    # In YOLO mode or when coming from email step, skip the prompt and generate automatically
    if not yolo and not coming_from_email:
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
            console.print("→ You can generate it later with: [bold #0066CC]blossomer advisor {domain}[/bold #0066CC]")
            return False  # Return False when skipped
    
    console.print()
    
    # Generate the strategic plan directly (not using run_generation_step)
    try:
        from cli.services.llm_service import LLMClient
        from app.services.gtm_advisor_service import GTMAdvisorService
        
        # Show animated loading for strategic plan generation (panel already shown above)
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
            console.print("[bold #0066CC]Strategic Plan Generated![/bold #0066CC]")
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
            
            console.print("→ View your full plan in plans/strategy.md")
        
        console.print()
        return True  # Return True on success
        
    except Exception as e:
        console.print(f"[red]Failed to generate strategic plan:[/red] {e}")
        console.print("→ You can try again later with: [bold #0066CC]blossomer advisor {domain}[/bold #0066CC]")
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