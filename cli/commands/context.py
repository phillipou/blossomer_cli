"""
Context management commands for the GTM CLI
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

app = typer.Typer(help="Manage dynamic context store")
console = Console()


@app.command()
def init_db(
    db_url: Optional[str] = typer.Option(
        None, 
        "--db-url", 
        help="PostgreSQL connection URL (default: postgresql://localhost/blossomer_context)"
    ),
    redis_url: Optional[str] = typer.Option(
        None,
        "--redis-url", 
        help="Redis connection URL (default: redis://localhost:6379)"
    )
):
    """Initialize the context store database"""
    async def _init():
        try:
            from app.services.context_store import ContextStore
            
            store = ContextStore(db_url=db_url, redis_url=redis_url)
            await store.initialize()
            
            console.print("✅ Context store initialized successfully!", style="green")
            console.print(f"Database: {store.db_url}")
            if store.redis_client:
                console.print(f"Redis cache: {store.redis_url}")
            else:
                console.print("Redis cache: [yellow]Not available[/yellow]")
            
            await store.close()
            
        except ImportError as e:
            console.print(f"❌ Missing dependencies: {e}", style="red")
            console.print("Install with: pip install asyncpg redis", style="yellow")
        except Exception as e:
            console.print(f"❌ Initialization failed: {e}", style="red")
    
    asyncio.run(_init())


@app.command()
def status(
    client_id: str = typer.Argument(..., help="Client ID to check"),
):
    """Show context status for a client"""
    async def _status():
        try:
            from app.services.context_store import get_context_store
            
            store = await get_context_store()
            
            # Get context for each agent type
            agent_types = ["product_overview", "target_account", "target_persona", "email_generation"]
            
            table = Table(title=f"Context Status for Client: {client_id}")
            table.add_column("Agent Type", style="cyan")
            table.add_column("Context Size", justify="right")
            table.add_column("Cross-Client Patterns", justify="right")
            table.add_column("Performance Metrics", justify="right")
            
            for agent_type in agent_types:
                context = await store.get_context_for_agent(client_id, agent_type)
                
                context_size = len(str(context))
                patterns_count = len(context.get('_cross_client_patterns', []))
                metrics_count = len(context.get('_performance_metrics', {}))
                
                table.add_row(
                    agent_type,
                    f"{context_size} chars",
                    str(patterns_count),
                    str(metrics_count)
                )
            
            console.print(table)
            
            await store.close()
            
        except Exception as e:
            console.print(f"❌ Status check failed: {e}", style="red")
    
    asyncio.run(_status())


@app.command()
def pending_approvals():
    """Show context updates pending approval"""
    async def _pending():
        try:
            from app.services.context_store import get_context_store
            
            store = await get_context_store()
            updates = await store.get_pending_approvals(limit=20)
            
            if not updates:
                console.print("✅ No pending approvals", style="green")
                return
            
            table = Table(title="Pending Context Updates")
            table.add_column("ID", style="cyan")
            table.add_column("Client", style="blue")
            table.add_column("Agent", style="yellow")
            table.add_column("Source", style="magenta")
            table.add_column("Confidence", justify="right")
            table.add_column("Created", style="dim")
            
            for update in updates:
                table.add_row(
                    str(update['id']),
                    update['client_id'],
                    update['agent_type'] or "general",
                    update['source'],
                    f"{update['confidence']:.2f}",
                    update['created_at'].strftime("%m/%d %H:%M")
                )
            
            console.print(table)
            
            await store.close()
            
        except Exception as e:
            console.print(f"❌ Failed to get pending approvals: {e}", style="red")
    
    asyncio.run(_pending())


@app.command()
def approve(
    update_id: int = typer.Argument(..., help="Update ID to approve"),
    approved_by: str = typer.Option("cli-user", "--by", help="Who is approving this update")
):
    """Approve a pending context update"""
    async def _approve():
        try:
            from app.services.context_store import get_context_store
            
            store = await get_context_store()
            success = await store.approve_update(update_id, approved_by)
            
            if success:
                console.print(f"✅ Update {update_id} approved by {approved_by}", style="green")
            else:
                console.print(f"❌ Update {update_id} not found or already approved", style="red")
            
            await store.close()
            
        except Exception as e:
            console.print(f"❌ Approval failed: {e}", style="red")
    
    asyncio.run(_approve())


@app.command()
def demo_update(
    client_id: str = typer.Argument(..., help="Client ID"),
    agent_type: str = typer.Option("product_overview", "--agent", help="Agent type"),
):
    """Demo: Add a sample context update"""
    async def _demo():
        try:
            from app.services.context_store import get_context_store, ContextUpdate, ContextUpdateSource
            from datetime import datetime
            
            store = await get_context_store()
            
            # Create a demo update
            update = ContextUpdate(
                client_id=client_id,
                source=ContextUpdateSource.HUMAN_UPLOAD,
                agent_type=agent_type,
                update_data={
                    "demo_insight": "This is a demo context update",
                    "industry_focus": "technology",
                    "target_company_size": "100-500 employees"
                },
                confidence=0.9,
                requires_approval=True,
                created_at=datetime.now()
            )
            
            await store.update_context(update)
            console.print(f"✅ Demo context update created for {client_id}/{agent_type}", style="green")
            console.print("Use 'gtm context pending-approvals' to see it", style="blue")
            
            await store.close()
            
        except Exception as e:
            console.print(f"❌ Demo failed: {e}", style="red")
    
    asyncio.run(_demo())


if __name__ == "__main__":
    app()