"""
Preview utilities for GTM generation steps
Generic preview functions to eliminate repetitive code
"""

from typing import Optional, List
from rich.console import Console
import typer
import questionary

from cli.utils.step_config import step_manager, StepConfig
from cli.utils.panel_utils import create_step_panel_by_key, create_preview_header
from cli.utils.console import clear_console, ensure_breathing_room
from cli.utils.markdown_formatter import get_formatter
from cli.services.gtm_generation_service import gtm_service

console = Console()

def show_step_preview(domain: str, step_key: str, choices: Optional[List[str]] = None) -> None:
    """
    Generic preview function for any GTM step
    
    Args:
        domain: The domain being analyzed
        step_key: The step key (overview, account, persona, email)
        choices: Optional custom choices for the menu
    """
    try:
        step = step_manager.get_step(step_key)
        if not step:
            console.print(f"[red]Error:[/red] Unknown step: {step_key}")
            return
        
        # Load the generated data
        step_data = gtm_service.storage.load_step_data(domain, step_key)
        if not step_data:
            console.print(f"[red]Error:[/red] No data found for {step.name}")
            return
        
        # Use markdown formatter for preview
        formatter = get_formatter(step_key)
        preview_markdown = formatter.format(step_data, preview=True, max_chars=1500)
        
        # Clear screen and show step panel + preview
        clear_console()
        console.print()
        console.print(create_step_panel_by_key(step_key))
        console.print()
        console.print(create_preview_header(step_key))
        console.print()
        
        # Display preview content
        console.print(preview_markdown)
        
        # Add character count indicator
        full_content = formatter.format(step_data, preview=False)
        total_chars = len(full_content)
        preview_chars = len(preview_markdown)
        console.print()
        console.print(f"[dim][Previewing {preview_chars:,} of {total_chars:,} characters][/dim]")
        
        console.print()
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        json_file_path = project_dir / "json_output" / step.file_name
        if json_file_path.exists():
            file_size = json_file_path.stat().st_size / 1024
            console.print(f"✓ Full {step.name.lower()} saved to: json_output/{step.file_name} ({file_size:.1f}KB)")
        else:
            console.print(f"✓ {step.name.lower()} generated (file not yet saved)")
        
        console.print()
        console.print()
        
        # Show user choices
        if choices is None:
            if step_manager.is_last_step(step_key):
                choices = [
                    "Complete generation",
                    f"Edit full {step.name.lower()} in editor",
                    "Abort"
                ]
            else:
                choices = [
                    "Continue to next step",
                    f"Edit full {step.name.lower()} in editor",
                    "Abort"
                ]
        
        choice = show_menu_with_separator(
            "What would you like to do?",
            choices=choices
        )
        
        # Handle user choice
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif "Edit" in choice:
            edit_step_content(domain, step_key, step.name)
            # After editing, show continuation choice
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            ensure_breathing_room(console)
            if continue_choice is None or not continue_choice:
                raise KeyboardInterrupt()
        # If continue/complete, just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")

def show_guided_email_preview(domain: str) -> None:
    """Show enhanced email campaign preview for guided mode"""
    try:
        step = step_manager.get_step("email")
        if not step:
            return
        
        # Load the generated email data
        email_data = gtm_service.storage.load_step_data(domain, "email")
        if not email_data:
            return
        
        # Clear screen and show step panel + preview
        clear_console()
        console.print()
        console.print(create_step_panel_by_key("email"))
        console.print()
        
        # Show guided steps Q&A history if available
        guided_preferences = email_data.get("guided_preferences", {})
        qa_history = guided_preferences.get("qa_history", [])
        if qa_history:
            console.print("✓ Previous guided steps:")
            for qa in qa_history:
                console.print(f"  [bold]{qa['question']}[/bold]")
                console.print(f"  → {qa['answer']}")
                console.print()
        
        console.print(create_preview_header("email"))
        
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
            preview_body = "\n".join(body_lines)
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
            
            # Add character count indicator
            full_body = body
            total_chars = len(subject) + len(full_body) + 50  # Add some for template parts
            preview_chars = len(subject) + len(preview_body) + 50
            console.print()
            console.print(f"[dim][Previewing {preview_chars:,} of {total_chars:,} characters][/dim]")
        
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        json_file_path = project_dir / "json_output" / step.file_name
        if json_file_path.exists():
            file_size = json_file_path.stat().st_size / 1024
            console.print(f"✓ Full campaign saved to: json_output/{step.file_name} ({file_size:.1f}KB)")
        else:
            console.print(f"✓ Campaign generated (file not yet saved)")
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
        
        ensure_breathing_room(console)
        
        if choice == "Abort":
            raise KeyboardInterrupt()
        elif choice == "Edit full campaign in editor":
            edit_step_content(domain, "email", step.name)
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=None)
            ensure_breathing_room(console)
            if continue_choice is None or not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to GTM plan", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")

def show_menu_with_separator(question: str, choices: List[str], add_separator: bool = True) -> str:
    """Show a questionary menu with visual separator and consistent styling"""
    import questionary
    
    # Import menu style
    MENU_STYLE = questionary.Style([
        ('question', 'bold cyan'),
        ('pointer', 'bold cyan'),
        ('highlighted', 'bold cyan'),
        ('selected', 'bold cyan'),
        ('answer', 'bold cyan')
    ])
    
    if add_separator:
        console.print()
        console.print("─" * 60)
        console.print()
    
    result = questionary.select(
        question,
        choices=choices,
        style=MENU_STYLE
    ).ask()
    
    ensure_breathing_room(console)
    
    # Handle CTRL+C (questionary returns None when interrupted)
    if result is None:
        raise KeyboardInterrupt()
    
    return result

def edit_step_content(domain: str, step_key: str, step_name: str) -> None:
    """Open step content in system editor"""
    from cli.utils.editor import detect_editor, open_file_in_editor
    
    try:
        step = step_manager.get_step(step_key)
        if not step:
            console.print(f"[red]Error:[/red] Unknown step: {step_key}")
            return
        
        project_dir = gtm_service.storage.get_project_dir(domain)
        step_file = project_dir / step.file_name
        
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