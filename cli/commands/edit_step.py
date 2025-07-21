"""
Edit step command - opens markdown files in system editor
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
import typer

from cli.utils.colors import Colors
from cli.utils.editor import detect_editor, open_file_in_editor
from cli.services.project_storage import project_storage
from cli.utils.step_config import step_manager

console = Console()

def edit_step_command(step: str, domain: Optional[str] = None) -> None:
    """Edit a specific step's markdown file"""
    
    # Map user-friendly step names to internal step keys
    step_mapping = {
        "plan": "advisor"  # 'plan' maps to 'advisor' step
    }
    
    # Use mapped step name if available
    actual_step = step_mapping.get(step, step)
    
    # Validate step
    step_config = step_manager.get_step(actual_step)
    if not step_config:
        console.print(f"[red]Error:[/red] Unknown step '{step}'")
        console.print(f"→ Valid steps: {', '.join([s.key for s in step_manager.steps])}")
        raise typer.Exit(1)
    
    # Auto-detect domain if not provided
    if not domain:
        from cli.commands.show import auto_detect_current_project
        domain = auto_detect_current_project()
        if not domain:
            return
    
    # Get project directory
    project_dir = project_storage.get_project_dir(domain)
    if not project_dir.exists():
        console.print(f"[red]Error:[/red] No project found for domain '{domain}'")
        console.print(f"→ Create project: {Colors.format_command(f'blossomer init {domain}')}")
        raise typer.Exit(1)
    
    # Check if markdown file exists
    # Map actual step to correct markdown filename
    step_to_filename = {
        "overview": "overview.md",
        "account": "account.md", 
        "persona": "persona.md",
        "email": "email.md",
        "advisor": "strategic_plan.md"  # advisor step maps to strategic_plan.md
    }
    
    filename = step_to_filename.get(actual_step, f"{actual_step}.md")
    markdown_file = project_dir / "plans" / filename
    
    if not markdown_file.exists():
        # Try to generate markdown from JSON data
        json_data = project_storage.load_step_data(domain, actual_step)
        if json_data:
            console.print(f"[blue]→[/blue] Generating markdown file from data...")
            try:
                from cli.utils.markdown_formatter import get_formatter
                formatter = get_formatter(actual_step)
                markdown_content = formatter.format_with_markers(json_data, actual_step)
                
                # Ensure plans directory exists
                plans_dir = project_dir / "plans"
                plans_dir.mkdir(exist_ok=True)
                
                # Save markdown file
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
                console.print(f"[green]✓[/green] Created {actual_step}.md from existing data")
            except Exception as e:
                console.print(f"[red]Error:[/red] Could not generate markdown file: {e}")
                raise typer.Exit(1)
        else:
            console.print(f"[red]Error:[/red] No data found for {step_config.name}")
            console.print(f"→ Generate step first: {Colors.format_command(f'blossomer generate {actual_step} --domain {domain}')}")
            raise typer.Exit(1)
    
    # Open in editor
    editor = detect_editor()
    console.print(f"[blue]→[/blue] Opening {step_config.name} in {editor}...")
    
    success = open_file_in_editor(markdown_file, editor)
    
    if success:
        console.print(f"[green]✓[/green] {step_config.name} updated")
        
        # Mark dependent steps as stale if they exist
        try:
            stale_steps = project_storage.mark_steps_stale(domain, actual_step)
            if stale_steps:
                console.print(f"[yellow]⚠️[/yellow] Dependent steps marked as stale: {', '.join(stale_steps)}")
                console.print(f"→ Regenerate: {Colors.format_command(f'blossomer generate {stale_steps[0]} --domain {domain}')}")
        except Exception:
            pass  # Don't fail if this doesn't work
    else:
        console.print(f"[yellow]⚠️[/yellow] Editor closed without changes")

