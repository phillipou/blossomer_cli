"""
Show command implementation - Display generated GTM assets with Rich formatting
"""

import json
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from cli.services.gtm_generation_service import gtm_service
from cli.utils.domain import normalize_domain

console = Console()


def show_assets(asset: str = "all", json_output: bool = False, domain: Optional[str] = None) -> None:
    """Display generated assets with rich formatting"""
    
    # If no domain specified, try to detect from current project
    if not domain:
        projects = gtm_service.storage.list_projects()
        if not projects:
            console.print("[red]No GTM projects found.[/red]")
            console.print("→ Create one with: [bold cyan]blossomer init[/bold cyan]")
            return
        elif len(projects) == 1:
            domain = projects[0]["domain"]
        else:
            console.print("[red]Multiple projects found. Please specify domain:[/red]")
            for project in projects[:5]:  # Show first 5
                console.print(f"  • {project['domain']}")
            console.print("→ Use: [bold cyan]blossomer show <asset> --domain <domain>[/bold cyan]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        normalized_domain = normalized.domain  # Use clean domain name, not full URL
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    # Check if project exists
    status = gtm_service.get_project_status(normalized_domain)
    if not status["exists"]:
        console.print(f"[red]No GTM project found for {normalized_domain}[/red]")
        console.print("→ Create one with: [bold cyan]blossomer init[/bold cyan]")
        return
    
    if asset == "all":
        show_all_assets(normalized_domain, json_output)
    elif asset in ["overview", "account", "persona", "email", "plan"]:
        show_single_asset(normalized_domain, asset, json_output)
    else:
        console.print(f"[red]Unknown asset: {asset}[/red]")
        console.print("Available assets: [bold cyan]all, overview, account, persona, email, plan[/bold cyan]")


def show_all_assets(domain: str, json_output: bool = False) -> None:
    """Show overview of all assets for a project"""
    
    if json_output:
        show_all_json(domain)
        return
    
    # Project header
    status = gtm_service.get_project_status(domain)
    
    console.print()
    console.print(Panel.fit(
        f"[bold blue]GTM Project: {domain}[/bold blue]\n\n"
        f"Progress: {status['progress_percentage']:.0f}% complete\n"
        f"Available steps: {', '.join(status['available_steps'])}\n"
        f"Last updated: {status.get('updated_at', 'Unknown')}",
        title="[bold]Project Overview[/bold]",
        border_style="blue"
    ))
    
    # Show each available asset
    available_steps = status["available_steps"] 
    step_names = {
        "overview": "🏢 Company Overview",
        "account": "🎯 Target Account Profile", 
        "persona": "👤 Buyer Persona",
        "email": "📧 Email Campaign",
        "plan": "📋 GTM Plan",
        "strategic_plan": "🎯 Strategic Plan"
    }
    
    for step in available_steps:
        console.print()
        show_asset_summary(domain, step, step_names.get(step, step.title()))
    
    # Show stale warnings
    if status.get("has_stale_data"):
        console.print()
        console.print(Panel.fit(
            f"[yellow]⚠️  Some data may be outdated[/yellow]\n\n"
            f"Stale steps: {', '.join(status.get('stale_steps', []))}\n"
            "These steps should be regenerated after editing dependencies.",
            title="[bold]Data Status[/bold]",
            border_style="yellow"
        ))
    
    # Next steps
    console.print()
    console.print("[bold]Commands:[/bold]")
    console.print(f"  • View details: [bold cyan]blossomer show <asset>[/bold cyan]")
    console.print(f"  • Edit content: [bold cyan]blossomer edit <asset>[/bold cyan]")
    console.print(f"  • Export report: [bold cyan]blossomer export[/bold cyan]")


def show_single_asset(domain: str, step: str, json_output: bool = False) -> None:
    """Show detailed view of a single asset"""
    
    # Map user-friendly step names to internal step keys
    step_mapping = {
        "plan": "advisor"  # 'plan' maps to 'advisor' step
    }
    
    # Use mapped step name if available
    actual_step = step_mapping.get(step, step)
    
    # Load step data for JSON output and metadata
    step_data = gtm_service.storage.load_step_data(domain, actual_step)
    
    if json_output:
        if not step_data:
            console.print(f"[red]{step.title()} not found for {domain}[/red]")
            console.print(f"→ Generate with: [bold cyan]blossomer generate {step}[/bold cyan]")
            return
        # Output raw JSON
        syntax = Syntax(
            json.dumps(step_data, indent=2), 
            "json", 
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)
        return
    
    # Rich formatted display based on step type
    step_titles = {
        "overview": "🏢 Company Overview",
        "account": "🎯 Target Account Profile",
        "persona": "👤 Buyer Persona", 
        "email": "📧 Email Campaign",
        "plan": "📋 GTM Strategic Plan"
    }
    
    title = step_titles.get(step, step.title())
    console.print()
    console.print(f"[bold blue]{title}[/bold blue]")
    console.print()
    
    # Check if data is stale
    if step_data and step_data.get("_stale"):
        console.print(Panel.fit(
            f"[yellow]⚠️  This data may be outdated[/yellow]\n\n"
            f"Reason: {step_data.get('_stale_reason', 'Unknown')}\n"
            "Consider regenerating this step.",
            border_style="yellow"
        ))
        console.print()
    
    # Display markdown file for the step
    show_markdown_file(domain, actual_step, step)
    
    # Metadata
    console.print()
    if step_data:
        console.print(f"[dim]Generated: {step_data.get('_generated_at', 'Unknown')}[/dim]")
    else:
        console.print("[dim]Generated: Unknown (JSON data not found)[/dim]")


def show_asset_summary(domain: str, step: str, title: str) -> None:
    """Show a compact summary of an asset"""
    
    step_data = gtm_service.storage.load_step_data(domain, step)
    if not step_data:
        return
    
    # Create summary based on step type
    if step == "overview":
        summary = step_data.get("description", step_data.get("company_description", "No description available"))[:100] + "..."
    elif step == "account":
        # Use target_account_name and firmographics
        account_name = step_data.get("target_account_name", "N/A")
        firmographics = step_data.get("firmographics", {})
        industry = firmographics.get("industry", "N/A") 
        company_size = firmographics.get("company_size", "N/A")
        summary = f"{account_name} | Industry: {industry}, Size: {company_size}"
    elif step == "persona":
        # Use target_persona_name and demographics
        persona_name = step_data.get("target_persona_name", "N/A")
        demographics = step_data.get("demographics", {})
        job_title = demographics.get("job_title", "N/A")
        summary = f"{persona_name} | Role: {job_title}"
    elif step == "email":
        # Use the correct schema fields
        subjects = step_data.get("subjects", {})
        primary_subject = subjects.get("primary", "N/A")
        
        # Check extras
        follow_up = step_data.get("follow_up_email", {})
        variation = step_data.get("email_variation", {})
        
        extras = []
        if follow_up:
            extras.append("Follow-up: ✓")
        if variation:
            extras.append("Variation: ✓")
        
        if extras:
            summary = f"Subject: {primary_subject} | {' | '.join(extras)}"
        else:
            summary = f"Subject: {primary_subject}"
    elif step == "plan":
        summary = "30-day GTM execution plan"
    else:
        summary = "Generated content available"
    
    # Show with stale indicator
    status_indicator = "[yellow]⚠️[/yellow]" if step_data.get("_stale") else "[green]✓[/green]"
    
    console.print(Panel.fit(
        f"{summary}",
        title=f"{status_indicator} {title}",
        border_style="green" if not step_data.get("_stale") else "yellow"
    ))


def show_company_overview(data: dict) -> None:
    """Format company overview data"""
    
    # Basic info
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    
    if "company_name" in data:
        table.add_row("Company", data["company_name"])
    if "industry" in data:
        table.add_row("Industry", data["industry"])
    if "company_size" in data:
        table.add_row("Size", data["company_size"])
    if "website_url" in data:
        table.add_row("Website", data["website_url"])
    
    console.print(table)
    
    if "company_description" in data:
        console.print()
        console.print(Panel(
            data["company_description"],
            title="[bold]Description[/bold]",
            border_style="blue"
        ))
    
    # Products/services
    if "products_services" in data:
        console.print()
        console.print("[bold]Products & Services:[/bold]")
        for item in data["products_services"]:
            console.print(f"  • {item}")


def show_target_account(data: dict) -> None:
    """Format target account data"""
    
    profile = data.get("target_account_profile", {})
    
    # Basic profile info
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    
    fields = [
        ("Industry", "industry"),
        ("Company Size", "company_size"), 
        ("Revenue Range", "revenue_range"),
        ("Geographic Focus", "geographic_focus"),
        ("Technology Stack", "technology_preferences")
    ]
    
    for label, key in fields:
        if key in profile:
            value = profile[key]
            if isinstance(value, list):
                value = ", ".join(value)
            table.add_row(label, str(value))
    
    console.print(table)
    
    # Pain points
    if "pain_points" in profile:
        console.print()
        console.print("[bold]Pain Points:[/bold]")
        for pain_point in profile["pain_points"]:
            console.print(f"  • {pain_point}")


def show_buyer_persona(data: dict) -> None:
    """Format buyer persona data"""
    
    persona = data.get("target_persona", {})
    
    # Basic info
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    
    fields = [
        ("Name", "name"),
        ("Job Title", "job_title"),
        ("Department", "department"),
        ("Seniority", "seniority_level"),
        ("Experience", "years_of_experience"),
        ("Education", "education_level")
    ]
    
    for label, key in fields:
        if key in persona:
            table.add_row(label, str(persona[key]))
    
    console.print(table)
    
    # Goals and challenges
    if "goals" in persona:
        console.print()
        console.print("[bold]Goals:[/bold]")
        for goal in persona["goals"]:
            console.print(f"  • {goal}")
    
    if "challenges" in persona:
        console.print()
        console.print("[bold]Challenges:[/bold]")
        for challenge in persona["challenges"]:
            console.print(f"  • {challenge}")


def show_email_campaign(data: dict) -> None:
    """Format email campaign data using markdown formatter"""
    from cli.utils.markdown_formatter import get_formatter
    from rich.markdown import Markdown
    
    # Use markdown formatter for consistent display
    formatter = get_formatter('email')
    preview_markdown = formatter.format(data, preview=True, max_chars=800)
    console.print(Markdown(preview_markdown))


def show_gtm_plan(data: dict) -> None:
    """Format GTM plan data"""
    
    # This would be implemented when GTM plan generation is added
    console.print("[yellow]GTM Plan display coming soon...[/yellow]")
    
    # For now, show raw structure
    for key, value in data.items():
        if not key.startswith("_"):
            console.print(f"[bold]{key.replace('_', ' ').title()}:[/bold] {value}")


def show_markdown_file(domain: str, actual_step: str, original_step: str) -> None:
    """Display the markdown file for any step"""
    from pathlib import Path
    
    project_dir = Path("gtm_projects") / domain
    
    # Map actual step to markdown filename
    step_to_filename = {
        "overview": "overview.md",
        "account": "account.md", 
        "persona": "persona.md",
        "email": "email.md",
        "advisor": "strategic_plan.md"  # advisor step maps to strategic_plan.md
    }
    
    filename = step_to_filename.get(actual_step, f"{actual_step}.md")
    markdown_path = project_dir / "plans" / filename
    
    if not markdown_path.exists():
        console.print(f"[red]{original_step.title()} markdown file not found[/red]")
        console.print(f"→ Generate with: [bold cyan]blossomer generate {original_step} --domain {domain}[/bold cyan]")
        return
    
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Display the markdown content with syntax highlighting
        syntax = Syntax(
            content,
            "markdown",
            theme="monokai",
            line_numbers=False,
            word_wrap=True
        )
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[red]Error reading {original_step} file: {e}[/red]")


def show_strategic_plan(domain: str) -> None:
    """Display the strategic plan markdown file (legacy function)"""
    show_markdown_file(domain, "advisor", "strategic plan")


def show_all_json(domain: str) -> None:
    """Output all assets as JSON"""
    
    all_data = {}
    available_steps = gtm_service.storage.get_available_steps(domain)
    
    for step in available_steps:
        step_data = gtm_service.storage.load_step_data(domain, step)
        if step_data:
            all_data[step] = step_data
    
    console.print(json.dumps(all_data, indent=2))