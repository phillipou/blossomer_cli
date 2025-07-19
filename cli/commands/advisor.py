"""GTM Advisor CLI command for generating strategic plans."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from app.services.gtm_advisor_service import GTMAdvisorService

app = typer.Typer()
console = Console()


@app.command()
def advisor(
    domain: str = typer.Argument(..., help="Company domain to generate strategic plan for"),
    regenerate: bool = typer.Option(False, "--regenerate", "-r", help="Regenerate strategic plan even if it exists"),
    show_preview: bool = typer.Option(True, "--preview/--no-preview", help="Show preview of generated plan"),
) -> None:
    """Generate comprehensive GTM strategic plan from previous analysis."""
    
    asyncio.run(_advisor_async(domain, regenerate, show_preview))


async def _advisor_async(domain: str, regenerate: bool, show_preview: bool) -> None:
    """Async implementation of advisor command."""
    
    project_dir = Path("gtm_projects") / domain
    
    # Initialize service
    advisor_service = GTMAdvisorService()
    
    # Check prerequisites
    console.print(f"\n[bold]GTM Strategic Planning for {domain}[/bold]")
    console.print("─" * 50)
    
    prerequisites = advisor_service.validate_prerequisites(domain, project_dir)
    missing_files = [filename for filename, exists in prerequisites.items() if not exists]
    
    if missing_files:
        console.print("[red]Missing required analysis files:[/red]")
        for filename in missing_files:
            console.print(f"  ❌ {filename}")
        console.print(f"\n💡 Complete all previous steps first:")
        console.print(f"   • blossomer overview {domain}")
        console.print(f"   • blossomer account {domain}")
        console.print(f"   • blossomer persona {domain}")
        console.print(f"   • blossomer email {domain}")
        return
    
    # Check if strategic plan already exists
    plan_status = advisor_service.get_strategic_plan_status(domain, project_dir)
    
    if plan_status["exists"] and not regenerate:
        console.print("[yellow]Strategic plan already exists![/yellow]")
        console.print(f"📄 Location: {plan_status['path']}")
        
        if plan_status["metadata"]:
            generated_at = plan_status["metadata"].get("_generated_at", "Unknown")
            console.print(f"📅 Generated: {generated_at}")
        
        console.print(f"\n💡 Use --regenerate to create a new plan")
        console.print(f"💡 Use [bold]blossomer show {domain}[/bold] to view current plan")
        return
    
    # Show what we're about to do
    console.print("✅ All prerequisite files found:")
    for filename in prerequisites.keys():
        console.print(f"  ✅ {filename}")
    
    console.print(f"\n🎯 Generating comprehensive GTM strategic plan...")
    
    # Generate strategic plan with progress indicator
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Synthesizing strategic plan...", total=None)
            
            strategic_plan = await advisor_service.generate_strategic_plan(
                domain=domain,
                project_dir=project_dir
            )
        
        # Success message
        console.print("[green]Strategic plan generated successfully![/green]")
        
        plan_path = project_dir / "plans" / "strategic_plan.md"
        console.print(f"📄 Saved to: [bold]{plan_path}[/bold]")
        
        # Show plan summary
        _display_plan_summary(strategic_plan)
        
        # Optionally show preview
        if show_preview:
            console.print("\n" + "─" * 50)
            console.print("[bold]Strategic Plan Preview[/bold]")
            console.print("─" * 50)
            
            # Show first few sections
            lines = strategic_plan.split('\n')
            preview_lines = []
            line_count = 0
            
            for line in lines:
                if line_count > 50:  # Limit preview length
                    preview_lines.append("...")
                    preview_lines.append("(Use 'blossomer show strategic-plan' to view full plan)")
                    break
                preview_lines.append(line)
                line_count += 1
            
            console.print('\n'.join(preview_lines))
        
        # Next steps
        console.print(f"\n💡 [bold]Next Steps:[/bold]")
        console.print(f"   • Review your strategic plan: [bold]blossomer show {domain} strategic-plan[/bold]")
        console.print(f"   • Export everything: [bold]blossomer export {domain}[/bold]")
        console.print(f"   • Edit the plan: Open {plan_path}")
        
    except FileNotFoundError as e:
        console.print(f"[red]Missing required file: {str(e)}[/red]")
        console.print("\n💡 Make sure all previous analysis steps are complete")
        
    except Exception as e:
        console.print(f"[red]Failed to generate strategic plan: {str(e)}[/red]")
        console.print("\n💡 Check your LLM configuration and try again")


def _display_plan_summary(strategic_plan: str) -> None:
    """Display a summary of the generated strategic plan."""
    
    # Extract key sections for summary
    lines = strategic_plan.split('\n')
    
    # Count sections
    sections = [line for line in lines if line.startswith('## ')]
    
    # Look for key metrics/numbers
    account_signals = len([line for line in lines if 'Account Scoring' in line and '|' in line])
    contact_signals = len([line for line in lines if 'Contact Scoring' in line and '|' in line]) 
    tool_mentions = len([line for line in lines if '**Tool' in line or '| Tool' in line])
    
    # Create summary panel
    summary_text = Text()
    summary_text.append("📊 Plan Contents:\n", style="bold")
    summary_text.append(f"   • {len(sections)} strategic sections\n")
    summary_text.append(f"   • Account scoring framework\n")
    summary_text.append(f"   • Contact scoring framework\n") 
    summary_text.append(f"   • Tool stack recommendations\n")
    summary_text.append(f"   • Email methodology framework\n")
    summary_text.append(f"   • Metrics interpretation guide\n")
    
    panel = Panel(
        summary_text,
        title="Strategic Plan Generated",
        title_align="left",
        border_style="green"
    )
    
    console.print(panel)


@app.command()
def status(
    domain: str = typer.Argument(..., help="Company domain to check"),
) -> None:
    """Check status of GTM strategic plan for a domain."""
    
    advisor_service = GTMAdvisorService()
    
    project_dir = Path("gtm_projects") / domain
    
    console.print(f"\n[bold]GTM Strategic Plan Status for {domain}[/bold]")
    console.print("─" * 50)
    
    # Check prerequisites
    prerequisites = advisor_service.validate_prerequisites(domain, project_dir)
    
    console.print("📋 [bold]Prerequisites:[/bold]")
    for filename, exists in prerequisites.items():
        status_icon = "✅" if exists else "❌"
        console.print(f"   {status_icon} {filename}")
    
    # Check strategic plan status
    plan_status = advisor_service.get_strategic_plan_status(domain, project_dir)
    
    console.print(f"\n📄 [bold]Strategic Plan:[/bold]")
    if plan_status["exists"]:
        console.print(f"   ✅ Generated")
        console.print(f"   📍 Location: {plan_status['path']}")
        
        if plan_status["metadata"]:
            generated_at = plan_status["metadata"].get("_generated_at", "Unknown")
            console.print(f"   📅 Generated: {generated_at}")
        
        file_size_kb = plan_status["file_size"] / 1024
        console.print(f"   📏 Size: {file_size_kb:.1f} KB")
        
    else:
        console.print(f"   ❌ Not generated")
        
        missing_count = len([f for f, exists in prerequisites.items() if not exists])
        if missing_count > 0:
            console.print(f"   💡 Complete {missing_count} prerequisite(s) first")
        else:
            console.print(f"   💡 Run: blossomer advisor {domain}")


if __name__ == "__main__":
    app()