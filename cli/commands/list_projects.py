"""
List GTM projects command
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
import json

from cli.services.project_storage import project_storage
from cli.utils.colors import Colors

console = Console()

def list_projects(domain_filter: Optional[str] = None) -> None:
    """List all GTM projects or files for a specific domain"""
    
    # Get gtm_projects directory
    gtm_projects_dir = Path("gtm_projects")
    
    if not gtm_projects_dir.exists():
        console.print(f"[yellow]No GTM projects found.[/yellow]")
        console.print(f"→ Create your first project: {Colors.format_command('blossomer init company.com')}")
        return
    
    # Get all project directories
    project_dirs = [d for d in gtm_projects_dir.iterdir() if d.is_dir()]
    
    if not project_dirs:
        console.print(f"[yellow]No GTM projects found.[/yellow]")
        console.print(f"→ Create your first project: {Colors.format_command('blossomer init company.com')}")
        return
    
    if domain_filter:
        # Show files for specific domain
        show_project_files(domain_filter, project_dirs)
    else:
        # Show all projects
        show_all_projects(project_dirs)

def show_all_projects(project_dirs: list[Path]) -> None:
    """Show table of all GTM projects"""
    
    console.print()
    console.print(Panel.fit(
        "[bold blue]📁 GTM Projects[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Domain", style="bold white", min_width=20)
    table.add_column("Status", min_width=12)
    table.add_column("Files", min_width=8, justify="center")
    table.add_column("Last Modified", min_width=15)
    table.add_column("Size", min_width=8, justify="right")
    
    for project_dir in sorted(project_dirs, key=lambda x: x.name):
        domain = project_dir.name
        
        # Get project metadata
        metadata_file = project_dir / ".metadata.json"
        status = "Unknown"
        last_modified = "N/A"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                # Determine status based on completed steps
                steps_completed = metadata.get('steps_completed', [])
                total_steps = 5  # overview, account, persona, email, plan
                
                if len(steps_completed) == total_steps:
                    status = "[green]Complete[/green]"
                elif len(steps_completed) > 0:
                    status = f"[yellow]Partial ({len(steps_completed)}/{total_steps})[/yellow]"
                else:
                    status = "[red]Started[/red]"
                
                # Get last modified time
                modified_at = metadata.get('modified_at')
                if modified_at:
                    try:
                        dt = datetime.fromisoformat(modified_at.replace('Z', '+00:00'))
                        last_modified = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        last_modified = "N/A"
                        
            except Exception:
                status = "[red]Error[/red]"
        
        # Count markdown files in plans directory
        plans_dir = project_dir / "plans"
        file_count = len(list(plans_dir.glob("*.md"))) if plans_dir.exists() else 0
        
        # Calculate total size
        total_size = 0
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
        
        size_str = format_size(total_size)
        
        table.add_row(
            domain,
            status,
            str(file_count),
            last_modified,
            size_str
        )
    
    console.print(table)
    console.print()
    console.print(f"→ View project files: {Colors.format_command('blossomer list --domain company.com')}")
    console.print(f"→ View specific step: {Colors.format_command('blossomer show [step]')}")
    console.print()

def show_project_files(domain: str, project_dirs: list[Path]) -> None:
    """Show files for a specific project domain"""
    
    # Find matching project
    matching_project = None
    for project_dir in project_dirs:
        if project_dir.name == domain:
            matching_project = project_dir
            break
    
    if not matching_project:
        console.print(f"[red]Error:[/red] No project found for domain '{domain}'")
        console.print(f"→ Available projects: {', '.join([d.name for d in project_dirs])}")
        return
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]📁 Project Files: {domain}[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    # Show markdown files from plans directory
    plans_dir = matching_project / "plans"
    if plans_dir.exists():
        md_files = list(plans_dir.glob("*.md"))
        
        if md_files:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("File", style="bold white", min_width=20)
            table.add_column("Step", min_width=15)
            table.add_column("Size", min_width=8, justify="right")
            table.add_column("Modified", min_width=15)
            
            # Map step names
            step_names = {
                "overview.md": "Company Overview",
                "account.md": "Target Account",
                "persona.md": "Buyer Persona", 
                "email.md": "Email Campaign",
                "strategic_plan.md": "Strategic Plan"
            }
            
            for md_file in sorted(md_files):
                file_size = format_size(md_file.stat().st_size)
                modified_time = datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                step_name = step_names.get(md_file.name, "Unknown")
                
                table.add_row(
                    md_file.name,
                    step_name,
                    file_size,
                    modified_time
                )
            
            console.print(table)
        else:
            console.print("[yellow]No markdown files found in plans/ directory[/yellow]")
    else:
        console.print("[yellow]No plans/ directory found[/yellow]")
    
    console.print()
    console.print(f"→ View step content: {Colors.format_command('blossomer show [step]')}")
    console.print(f"→ Edit step: {Colors.format_command('blossomer edit --domain {domain} --step [step]')}")
    console.print()

def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"