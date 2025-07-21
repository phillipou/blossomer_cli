"""
Panel utilities for consistent UI components
Reusable panel functions to eliminate duplicate code
"""

from rich.console import Console
from rich.panel import Panel
from typing import Optional
from cli.utils.step_config import StepConfig, step_manager

def create_step_panel(step: StepConfig, step_number: int, total_steps: int) -> Panel:
    """Create a standardized step panel"""
    return Panel(
        f"{step.get_step_panel_title(step_number, total_steps)}\n"
        f"\n"
        f"{step.explanation}",
        border_style="blue_violet",
        expand=False,
        padding=(1, 2)
    )

def create_step_panel_by_key(step_key: str) -> Panel:
    """Create a step panel by step key"""
    step = step_manager.get_step(step_key)
    if not step:
        raise ValueError(f"Unknown step key: {step_key}")
    
    step_number = step_manager.get_step_number(step_key)
    total_steps = step_manager.get_total_steps()
    
    return create_step_panel(step, step_number, total_steps)

def create_welcome_panel(domain: str) -> Panel:
    """Create the welcome panel for new projects"""
    step_names = [step.name for step in step_manager.steps]
    steps_text = " → ".join([f"[green]{name}[/green]" for name in step_names])
    
    content = (
        f"🚀 [bold blue_violet]Starting GTM Generation for {domain}[/bold blue_violet]\n"
        f"\n"
        f"[bold]Creating:[/bold] {steps_text}"
    )
    
    return Panel(
        content,
        border_style="blue_violet",
        expand=False,
        padding=(1, 2)
    )

def create_status_panel(domain: str, status: dict) -> Panel:
    """Create the status panel for existing projects"""
    from cli.utils.colors import Colors
    
    content = (
        f"[bold blue_violet]Project: {domain}[/bold blue_violet]\n"
        f"\n"
        f"[bold]Status:[/bold] {Colors.format_success(', '.join(status['available_steps']))} | "
        f"[bold blue_violet]{status['progress_percentage']:.0f}%[/bold blue_violet] complete\n"
        f"[dim]Last updated: {status.get('last_updated', 'Unknown')}[/dim]"
    )
    
    if status.get('has_stale_data'):
        content += f"\n{Colors.format_warning('Some data may need updates')}"
    
    return Panel(
        content,
        border_style="blue_violet",
        expand=False,
        padding=(1, 2)
    )

def create_completion_panel() -> Panel:
    """Create the completion panel"""
    from cli.utils.colors import Colors
    
    content = (
        "[bold green]✅ GTM Generation Complete![/bold green]\n"
        "\n"
        "[bold]Your go-to-market package is ready:[/bold]\n"
        f"• View results: {Colors.format_command('blossomer show plan')}\n"
        f"• Edit content: {Colors.format_command('blossomer edit [overview|account|persona|email|plan]')}"
    )
    
    return Panel(
        content,
        border_style="green",
        expand=False,
        padding=(1, 2)
    )

def create_preview_header(step_key: str) -> str:
    """Create the preview header for a step"""
    step = step_manager.get_step(step_key)
    if not step:
        return f"[bold]PREVIEW[/bold]"
    
    return f"{step.icon} [bold]{step.preview_title}[/bold]"