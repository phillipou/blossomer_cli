"""
Export command implementation - Generate markdown reports from GTM assets
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain
from cli.utils.markdown_formatter import get_formatter

console = Console()


def export_assets(step: str = "all", output: Optional[str] = None, domain: Optional[str] = None) -> None:
    """Export GTM assets as formatted markdown reports"""
    
    # If no domain specified, try to detect from current project
    if not domain:
        projects = gtm_service.storage.list_projects()
        if not projects:
            console.print("[red]No GTM projects found.[/red]")
            console.print("→ Create one with: [cyan]blossomer init[/cyan]")
            return
        elif len(projects) == 1:
            domain = projects[0]["domain"]
        else:
            console.print("[red]Multiple projects found. Please specify domain:[/red]")
            for project in projects[:5]:  # Show first 5
                console.print(f"  • {project['domain']}")
            console.print("→ Use: [cyan]blossomer export <step> --domain <domain>[/cyan]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        normalized_domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    # Check if project exists
    status = gtm_service.get_project_status(normalized_domain)
    if not status["exists"]:
        console.print(f"[red]No GTM project found for {normalized_domain}[/red]")
        console.print("→ Create one with: [cyan]blossomer init[/cyan]")
        return
    
    # Get clean domain name for filenames
    domain_name = normalized_domain.replace("https://", "").replace("http://", "").replace("www.", "").replace("/", "")
    
    console.print(f"📄 Exporting GTM assets for {domain_name}...")
    
    if step == "all":
        export_all_assets(normalized_domain, domain_name, output)
    elif step in ["overview", "account", "persona", "email"]:
        export_single_asset(normalized_domain, domain_name, step, output)
    else:
        console.print(f"[red]Unknown asset: {step}[/red]")
        console.print("Available assets: [cyan]all, overview, account, persona, email[/cyan]")


def export_single_asset(domain: str, domain_name: str, step: str, output: Optional[str] = None) -> None:
    """Export a single asset as markdown"""
    
    # Load step data
    step_data = gtm_service.storage.load_step_data(domain, step)
    if not step_data:
        console.print(f"[red]{step.title()} not found for {domain}[/red]")
        console.print(f"→ Generate with: [cyan]blossomer generate {step}[/cyan]")
        return
    
    # Get formatter and generate markdown
    formatter = get_formatter(step)
    if not formatter:
        console.print(f"[red]No formatter available for {step}[/red]")
        return
    
    markdown_content = formatter.format(step_data, preview=False)
    
    # Determine output filename
    if output:
        output_path = Path(output)
    else:
        # Default filename pattern: {STEP}-{domain}-{date}.md
        today = datetime.now().strftime("%Y-%m-%d")
        step_name = step.upper()
        filename = f"{step_name}-{domain_name}-{today}.md"
        
        # Create export directory in project folder
        project_dir = Path("gtm_projects") / domain_name / "export"
        project_dir.mkdir(parents=True, exist_ok=True)
        output_path = project_dir / filename
    
    # Write markdown file
    output_path.write_text(markdown_content, encoding='utf-8')
    
    # Show success message
    file_size = output_path.stat().st_size / 1024  # KB
    console.print(f"✅ {step.title()} exported: [cyan]{output_path}[/cyan] ({file_size:.1f}KB)")
    
    # Show file preview path
    console.print(f"   Preview: [dim]file://{output_path.absolute()}[/dim]")


def export_all_assets(domain: str, domain_name: str, output: Optional[str] = None) -> None:
    """Export all available assets as a complete report"""
    
    # Get available steps
    available_steps = gtm_service.storage.get_available_steps(domain)
    if not available_steps:
        console.print("[red]No assets available to export[/red]")
        return
    
    # Build complete markdown report
    all_markdown_sections = []
    exported_files = []
    
    # Project metadata
    metadata = gtm_service.storage.load_metadata(domain)
    
    # Report header
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    domain_display = domain.replace("https://", "").replace("http://", "")
    
    last_updated = metadata.updated_at.strftime("%Y-%m-%d %H:%M") if metadata and metadata.updated_at else 'Unknown'
    
    report_header = f"""# GTM Intelligence Report
## {domain_display}

**Generated:** {today}  
**Completed Steps:** {len(available_steps)}/4  
**Last Updated:** {last_updated}

---

"""
    all_markdown_sections.append(report_header)
    
    # Export each available step
    step_order = ["overview", "account", "persona", "email", "plan"]
    
    for step in step_order:
        if step in available_steps:
            step_data = gtm_service.storage.load_step_data(domain, step)
            if step_data:
                formatter = get_formatter(step)
                if formatter:
                    markdown_content = formatter.format(step_data, preview=False)
                    all_markdown_sections.append(markdown_content)
                    all_markdown_sections.append("\n---\n")  # Section separator
                    
                    # Also export individual file
                    today_short = datetime.now().strftime("%Y-%m-%d")
                    step_name = step.upper()
                    individual_filename = f"{step_name}-{domain_name}-{today_short}.md"
                    
                    # Create export directory
                    project_dir = Path("gtm_projects") / domain_name / "export"
                    project_dir.mkdir(parents=True, exist_ok=True)
                    individual_path = project_dir / individual_filename
                    
                    # Write individual file
                    individual_path.write_text(markdown_content, encoding='utf-8')
                    individual_size = individual_path.stat().st_size / 1024
                    
                    exported_files.append({
                        'step': step,
                        'path': individual_path,
                        'size': individual_size
                    })
    
    # Combine all sections
    complete_report = "\n\n".join(all_markdown_sections)
    
    # Determine output filename for complete report
    if output:
        output_path = Path(output)
    else:
        today_short = datetime.now().strftime("%Y-%m-%d")
        filename = f"REPORT-{domain_name}-{today_short}.md"
        
        project_dir = Path("gtm_projects") / domain_name / "export"
        project_dir.mkdir(parents=True, exist_ok=True)
        output_path = project_dir / filename
    
    # Write complete report
    output_path.write_text(complete_report, encoding='utf-8')
    report_size = output_path.stat().st_size / 1024
    
    # Show success messages
    for file_info in exported_files:
        console.print(f"✅ {file_info['step'].title()} exported: {file_info['path'].name} ({file_info['size']:.1f}KB)")
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]📋 Complete report saved to:[/bold green]\n"
        f"[cyan]{output_path}[/cyan] ({report_size:.1f}KB)\n\n"
        f"Preview: [dim]file://{output_path.absolute()}[/dim]",
        title="[bold]Export Complete[/bold]",
        border_style="green"
    ))
    
    # Show usage suggestions
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print("  • Open in editor for customization")
    console.print("  • Share with stakeholders")
    console.print("  • Import into documentation system")
    console.print("  • Use for client presentations")