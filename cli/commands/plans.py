"""
Plans Command - Bidirectional JSON ↔ Markdown Sync

This module provides CLI commands for managing editable markdown files (plans)
that sync bidirectionally with JSON data, enabling user-friendly editing while
maintaining structured data for the CLI.
"""

import os
import subprocess
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from cli.utils.sync_manager import SyncManager, SyncDirection
from cli.utils.domain import normalize_domain

app = typer.Typer(help="Manage editable markdown plans that sync with JSON data")
console = Console()


@app.command()
def generate(
    step: str = typer.Argument(..., help="Step to generate (overview/account/persona/email/all)"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing plans files")
):
    """Generate editable markdown files from JSON data (json → plans)."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            console.print("→ Use: [bold #0066CC]blossomer plans generate overview --domain example.com[/bold #0066CC]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    
    console.print(f"📝 Generating plans for {domain}...")
    
    if step == "all":
        steps = ['overview', 'account', 'persona', 'email']
    else:
        steps = [step]
    
    results = []
    for step_name in steps:
        # Check if plans file already exists
        plans_file = sync_manager.get_plans_path(domain) / f"{step_name}.md"
        if plans_file.exists() and not force:
            console.print(f"⚠️  {step_name}.md already exists (use --force to overwrite)")
            continue
        
        result = sync_manager.sync_json_to_plans(domain, step_name)
        results.append((step_name, result))
        
        if 'error' in result:
            console.print(f"❌ {step_name}: {result['error']}")
        else:
            console.print(f"✅ {step_name}: Generated {step_name}.md ({result.get('fields_synced', 0)} fields)")
    
    if results:
        _show_plans_summary(domain, [r[0] for r in results if 'error' not in r[1]])


@app.command()
def update(
    step: str = typer.Argument(..., help="Step to update (overview/account/persona/email/all)"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be updated without making changes")
):
    """Update JSON data from edited markdown files (plans → json)."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            console.print("→ Use: [bold #0066CC]blossomer plans update overview --domain example.com[/bold #0066CC]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    
    if dry_run:
        console.print(f"🔍 Dry run: Checking what would be updated for {domain}...")
    else:
        console.print(f"🔄 Updating JSON from plans for {domain}...")
    
    if step == "all":
        steps = ['overview', 'account', 'persona', 'email']
    else:
        steps = [step]
    
    for step_name in steps:
        plans_file = sync_manager.get_plans_path(domain) / f"{step_name}.md"
        if not plans_file.exists():
            console.print(f"⚠️  {step_name}.md not found - skipping")
            continue
        
        if dry_run:
            # Just show what would be parsed
            from cli.utils.markdown_parser import create_parser
            parser = create_parser()
            content = plans_file.read_text()
            result = parser.parse_with_orphan_handling(content, step_name)
            
            console.print(f"\n📋 {step_name}.md analysis:")
            console.print(f"  Fields found: {result.success_count}")
            console.print(f"  Warnings: {len(result.warnings)}")
            console.print(f"  Orphaned: {len(result.orphaned_fields)}")
            
            if result.warnings:
                for warning in result.warnings:
                    console.print(f"    ⚠️  {warning}")
        else:
            result = sync_manager.sync_plans_to_json(domain, step_name)
            
            if 'error' in result:
                console.print(f"❌ {step_name}: {result['error']}")
            else:
                console.print(f"✅ {step_name}: Updated JSON ({result.get('fields_synced', 0)} fields)")
                
                # Show warnings
                warnings = result.get('warnings', [])
                if warnings:
                    for warning in warnings:
                        console.print(f"    ⚠️  {warning}")
                
                # Show orphaned fields
                orphaned = result.get('orphaned_fields', [])
                if orphaned:
                    console.print(f"    🔄 Orphaned fields: {', '.join(orphaned)}")
                    console.print("    💡 Tip: Run 'blossomer plans repair' to restore missing markers")


@app.command()
def sync(
    step: Optional[str] = typer.Argument(None, help="Step to sync (overview/account/persona/email), or all steps if not specified"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain"),
    auto_resolve: bool = typer.Option(True, "--auto-resolve/--no-auto-resolve", help="Automatically resolve simple conflicts")
):
    """Auto-detect changes and sync in the appropriate direction."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            console.print("→ Use: [bold #0066CC]blossomer plans sync --domain example.com[/bold #0066CC]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    
    console.print(f"🔄 Auto-syncing for {domain}...")
    
    summary = sync_manager.sync_project(domain, step, auto_resolve)
    
    # Display results
    if summary['synced_steps']:
        console.print("\n📊 Sync Results:")
        for step_result in summary['synced_steps']:
            step_name = step_result['step']
            direction = step_result['direction']
            fields = step_result['fields_synced']
            
            if direction == 'no_change':
                console.print(f"  {step_name}: No changes")
            elif direction == 'json_to_plans':
                console.print(f"  {step_name}: Generated plans from JSON ({fields} fields)")
            elif direction == 'plans_to_json':
                console.print(f"  {step_name}: Updated JSON from plans ({fields} fields)")
            elif direction == 'conflict':
                console.print(f"  {step_name}: ⚠️  Conflict detected")
            
            # Show warnings
            warnings = step_result.get('warnings', [])
            for warning in warnings:
                console.print(f"    ⚠️  {warning}")
    
    # Show conflicts
    if summary['conflicts']:
        console.print("\n⚠️  Conflicts detected:")
        for conflict in summary['conflicts']:
            console.print(f"  {conflict['step']}: {conflict['conflict'].message}")
    
    # Show errors
    if summary['errors']:
        console.print("\n❌ Errors:")
        for error in summary['errors']:
            console.print(f"  {error['step']}: {error['error']}")
    
    # Show orphaned fields summary
    if summary['orphaned_fields']:
        console.print("\n🔄 Orphaned fields detected:")
        for step_name, fields in summary['orphaned_fields'].items():
            console.print(f"  {step_name}: {', '.join(fields)}")
        console.print("💡 Tip: Run 'blossomer plans repair' to restore missing markers")


@app.command()
def edit(
    step: str = typer.Argument(..., help="Step to edit (overview/account/persona/email)"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Editor to use (default: auto-detect)")
):
    """Edit a plans file with auto-sync when done."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            console.print("→ Use: [bold #0066CC]blossomer plans edit overview --domain example.com[/bold #0066CC]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    plans_file = sync_manager.get_plans_path(domain) / f"{step}.md"
    
    # Generate plans file if it doesn't exist
    if not plans_file.exists():
        console.print(f"📝 Generating {step}.md from JSON data...")
        result = sync_manager.sync_json_to_plans(domain, step)
        if 'error' in result:
            console.print(f"❌ Failed to generate plans file: {result['error']}")
            return
        console.print(f"✅ Generated {step}.md")
    
    # Detect editor
    if not editor:
        editor = _detect_editor()
    
    console.print(f"📝 Opening {step}.md in {editor}...")
    console.print("💡 Tip: Keep the {#field_name} markers to enable syncing back to JSON")
    
    try:
        # Open editor
        subprocess.run([editor, str(plans_file)], check=True)
        
        # Auto-sync after editing
        console.print("🔄 Syncing changes back to JSON...")
        result = sync_manager.sync_plans_to_json(domain, step)
        
        if 'error' in result:
            console.print(f"❌ Sync failed: {result['error']}")
        else:
            fields_synced = result.get('fields_synced', 0)
            console.print(f"✅ Synced {fields_synced} fields back to JSON")
            
            warnings = result.get('warnings', [])
            for warning in warnings:
                console.print(f"  ⚠️  {warning}")
    
    except subprocess.CalledProcessError:
        console.print(f"❌ Failed to open editor: {editor}")
    except FileNotFoundError:
        console.print(f"❌ Editor not found: {editor}")
        console.print("💡 Try: --editor vim or --editor code or --editor nano")


@app.command()
def status(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain")
):
    """Show sync status for all plans files."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            console.print("→ Use: [bold #0066CC]blossomer plans status --domain example.com[/bold #0066CC]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    status_data = sync_manager.get_sync_status(domain)
    
    console.print(f"📊 Sync Status for {domain}")
    
    # Create status table
    table = Table(show_header=True, header_style="bold #0066CC")
    table.add_column("Step", style="#0066CC")
    table.add_column("JSON", justify="center")
    table.add_column("Plans", justify="center")
    table.add_column("Sync Needed", justify="center")
    table.add_column("Direction", style="#FDED02")
    table.add_column("Last Sync", style="#A5A2A2")
    
    for step, data in status_data.items():
        json_icon = "✅" if data['json_exists'] else "❌"
        plans_icon = "✅" if data['plans_exists'] else "❌"
        sync_icon = "⚠️" if data['sync_needed'] else "✅"
        direction = data['sync_direction'].replace('_', ' → ').title()
        last_sync = data['last_sync'][:19] if data['last_sync'] else "Never"
        
        table.add_row(step, json_icon, plans_icon, sync_icon, direction, last_sync)
    
    console.print(table)
    
    # Show orphaned fields if any
    orphaned_total = 0
    for step, data in status_data.items():
        orphaned_fields = data.get('orphaned_fields', [])
        if orphaned_fields:
            orphaned_total += len(orphaned_fields)
            console.print(f"🔄 {step}: {len(orphaned_fields)} orphaned fields")
    
    if orphaned_total > 0:
        console.print(f"\n💡 Total orphaned fields: {orphaned_total}")
        console.print("💡 Run 'blossomer plans repair' to restore missing markers")


@app.command()
def repair(
    step: str = typer.Argument(..., help="Step to repair (overview/account/persona/email)"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Project domain")
):
    """Repair missing field markers in plans files."""
    
    # Auto-detect domain if not provided
    if not domain:
        domain = _get_current_domain()
        if not domain:
            console.print("[red]No domain specified and no current project found.[/red]")
            return
    
    # Normalize domain
    try:
        normalized = normalize_domain(domain)
        domain = normalized.url
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid domain format: {e}")
        return
    
    sync_manager = SyncManager()
    
    console.print(f"🔧 Repairing {step}.md for {domain}...")
    console.print("⚠️  This will regenerate the plans file from current JSON data")
    console.print("⚠️  Any custom content without markers will be lost")
    
    confirm = typer.confirm("Continue?")
    if not confirm:
        console.print("Cancelled.")
        return
    
    # Create backup
    backups = sync_manager.create_backup(domain, step)
    if backups:
        console.print(f"✅ Backup created: {backups}")
    
    # Regenerate plans file
    result = sync_manager.sync_json_to_plans(domain, step)
    
    if 'error' in result:
        console.print(f"❌ Repair failed: {result['error']}")
    else:
        console.print(f"✅ Repaired {step}.md ({result.get('fields_synced', 0)} fields)")
        console.print("💡 Field markers restored - you can now edit and sync safely")


def _get_current_domain() -> Optional[str]:
    """Try to auto-detect current project domain."""
    # Look for projects in current directory or parent directories
    # This is a simplified version - could be enhanced to check git remotes, etc.
    current_dir = Path.cwd()
    gtm_projects = current_dir / "gtm_projects"
    
    if gtm_projects.exists():
        projects = [d.name for d in gtm_projects.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if len(projects) == 1:
            return projects[0]
    
    return None


def _detect_editor() -> str:
    """Detect available editor."""
    editors = ['code', 'vim', 'nano', 'emacs', 'subl', 'atom']
    
    # Check EDITOR environment variable
    editor_env = os.environ.get('EDITOR')
    if editor_env:
        return editor_env
    
    # Check for available editors
    for editor in editors:
        try:
            subprocess.run([editor, '--version'], capture_output=True, check=True)
            return editor
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Fallback
    return 'vim'


def _show_plans_summary(domain: str, steps: list):
    """Show summary of generated plans."""
    sync_manager = SyncManager()
    plans_path = sync_manager.get_plans_path(domain)
    
    console.print(f"\n📁 Plans directory: {plans_path}")
    console.print(f"📝 Generated files:")
    
    for step in steps:
        plans_file = plans_path / f"{step}.md"
        if plans_file.exists():
            size = plans_file.stat().st_size
            console.print(f"  {step}.md ({size:,} bytes)")
    
    console.print(f"\n💡 Edit with: [bold #0066CC]blossomer plans edit <step> --domain {domain}[/bold #0066CC]")
    console.print(f"💡 Sync back: [bold #0066CC]blossomer plans sync --domain {domain}[/bold #0066CC]")


if __name__ == "__main__":
    app()