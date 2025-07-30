"""
Simple Event Bus for Context Updates
Enables loose coupling between modules
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContextEvent:
    """Event for context system communication"""
    event_type: str
    client_id: str
    agent_type: str
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContextEventBus:
    """
    Simple pub/sub event bus for context updates
    20 lines of core logic for module coordination
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable[[ContextEvent], None]):
        """Subscribe to events of a specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type}")
    
    async def publish(self, event: ContextEvent):
        """Publish event to all subscribers"""
        handlers = self.subscribers.get(event.event_type, [])
        if handlers:
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        # Wrap sync functions
                        tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, event))
                except Exception as e:
                    logger.error(f"Error calling handler for {event.event_type}: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(f"Published {event.event_type} to {len(handlers)} handlers")


# Global event bus instance
event_bus = ContextEventBus()