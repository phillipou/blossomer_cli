"""
Preview utilities for GTM generation steps
Generic preview functions to eliminate repetitive code
"""

from typing import Optional, List
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
import typer
import questionary

from cli.utils.step_config import step_manager, StepConfig
from cli.utils.panel_utils import create_step_panel_by_key, create_preview_header
from cli.utils.console import clear_console, ensure_breathing_room
from cli.utils.markdown_formatter import get_formatter
from cli.services.gtm_generation_service import gtm_service

console = Console()

# Custom Markdown style to prevent cyan numbers/URLs - use black text for all markdown elements
CUSTOM_MARKDOWN_STYLE = {
    "markdown.code": Style(color="white"),
    "markdown.code_block": Style(color="white"),
    "markdown.link": Style(color="white"),
    "markdown.link_url": Style(color="white"),
    "markdown.strong": Style(color="white", bold=True),
    "markdown.emphasis": Style(color="white", italic=True),
    "markdown.text": Style(color="white"),
    "markdown.paragraph": Style(color="white"),
    "markdown.h1": Style(color="white", bold=True),
    "markdown.h2": Style(color="white", bold=True),
    "markdown.h3": Style(color="white", bold=True),
    "markdown.h4": Style(color="white", bold=True),
    "markdown.h5": Style(color="white", bold=True),
    "markdown.h6": Style(color="white", bold=True),
}

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
        console.print(create_preview_header(step_key))
        
        # Display preview content
        console.print(Markdown(preview_markdown))
        
        # Add character count indicator
        full_content = formatter.format(step_data, preview=False)
        total_chars = len(full_content)
        preview_chars = len(preview_markdown)
        console.print()
        console.print(f"[#0066CC][Previewing {preview_chars:,} of {total_chars:,} characters][/#0066CC]")
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        markdown_file_path = project_dir / "plans" / f"{step_key}.md"
        if markdown_file_path.exists():
            console.print(f"✅ Full {step.name.lower()} saved to: plans/{step_key}.md")
        else:
            console.print(f"✓ {step.name.lower()} generated (file not yet saved)")
                
        # Show user choices
        if choices is None:
            # Map step keys to actual filenames
            edit_filename_map = {
                "advisor": "strategy.md"
            }
            edit_filename = edit_filename_map.get(step_key, f"{step_key}.md")
            
            if step_manager.is_last_step(step_key):
                choices = [
                    "Complete generation",
                    f"Edit {edit_filename}",
                    "Exit"
                ]
            else:
                next_step_name = step_manager.get_next_step_name(step_key)
                choices = [
                    f"Next Step: {next_step_name}",
                    f"Edit {edit_filename}",
                    "Exit"
                ]
        
        choice = show_menu_with_separator(
            "What would you like to do?",
            choices=choices
        )
        
        # Handle user choice
        if choice == "Exit":
            raise KeyboardInterrupt()
        elif "Edit" in choice:
            edit_step_content(domain, step_key, step.name)
            # After editing, show continuation choice
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=True)
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
        
        # Show main email content using correct schema
        subjects = email_data.get("subjects", {})
        primary_subject = subjects.get("primary", "Your personalized subject line")
        full_email_body = email_data.get("full_email_body", "Your personalized email content")
        
        console.print(f"Subject: {primary_subject}")
        console.print()
        
        # Show a preview of the body (first few lines)
        body_lines = full_email_body.split('\n')[:6]
        preview_body = "\n".join(body_lines)
        for line in body_lines:
            console.print(line)
        
        if len(full_email_body.split('\n')) > 6:
            console.print("...")
        
        # Show alternative subjects if available
        alt_subjects = subjects.get("alternatives", [])
        if alt_subjects:
            console.print()
            console.print("Alternative subjects:")
            for alt in alt_subjects[:2]:
                console.print(f'- "{alt}"')
        
        # Show follow-up email if available
        follow_up_email = email_data.get("follow_up_email", {})
        if follow_up_email:
            console.print()
            console.print(f"[bold]Follow-up email[/bold] (send after {follow_up_email.get('wait_days', 3)} days):")
            console.print(f"Subject: {follow_up_email.get('subject', '')}")
            console.print(follow_up_email.get('body', '')[:100] + "..." if len(follow_up_email.get('body', '')) > 100 else follow_up_email.get('body', ''))
            
        # Add character count indicator
        total_chars = len(primary_subject) + len(full_email_body) + 50  # Add some for template parts
        preview_chars = len(primary_subject) + len(preview_body) + 50
        console.print()
        console.print(f"[#0066CC][Previewing {preview_chars:,} of {total_chars:,} characters][/#0066CC]")
        
        console.print()
        
        # Show file save info
        project_dir = gtm_service.storage.get_project_dir(domain)
        markdown_file_path = project_dir / "plans" / f"{step_key}.md"
        if markdown_file_path.exists():
            console.print(f"[green]✓ Full campaign saved to: plans/{step_key}.md[/green]")
        else:
            console.print(f"✓ Campaign generated (file not yet saved)")
        console.print()
        
        # Get user choice with numbered menu
        from cli.utils.menu_utils import show_menu_with_numbers
        
        choice = show_menu_with_numbers(
            "What would you like to do?",
            choices=[
                "Next: Create GTM plan",
                "Edit email.md",
                "Exit"
            ],
            add_separator=False
        )
        
        if choice == "Exit":
            raise KeyboardInterrupt()
        elif choice == "Edit email.md":
            edit_step_content(domain, "email", step.name)
            # After editing, show options again
            console.print()
            continue_choice = typer.confirm("Continue to next step?", default=True)
            ensure_breathing_room(console)
            if continue_choice is None or not continue_choice:
                raise KeyboardInterrupt()
        # If "Continue to GTM plan", just return and let the flow continue
        
    except Exception as e:
        console.print(f"[yellow]Could not show preview: {e}[/yellow]")

def show_menu_with_separator(question: str, choices: List[str], add_separator: bool = True) -> str:
    """Show a questionary menu with visual separator and consistent styling"""
    from cli.utils.menu_utils import show_menu_with_numbers
    
    return show_menu_with_numbers(question, choices, add_separator)

def edit_step_content(domain: str, step_key: str, step_name: str) -> None:
    """Open step content in system editor"""
    from cli.utils.editor import detect_editor, open_file_in_editor
    
    try:
        step = step_manager.get_step(step_key)
        if not step:
            console.print(f"[red]Error:[/red] Unknown step: {step_key}")
            return
        
        project_dir = gtm_service.storage.get_project_dir(domain)
        # Look for markdown file in plans/ directory
        step_file = project_dir / "plans" / f"{step_key}.md"
        
        if not step_file.exists():
            console.print(f"[red]Error:[/red] {step_name} file not found at {step_file}")
            console.print(f"[yellow]→ Try regenerating this step to create the markdown file[/yellow]")
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