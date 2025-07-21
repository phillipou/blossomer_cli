"""
Centralized loading animation system with step-specific text arrays
Provides animated loading messages with progressive dots that cycle through text states
"""

import time
import threading
from typing import Dict, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

class LoadingAnimator:
    """
    Manages animated loading messages for different GTM generation steps using Rich Progress
    Each step gets its own array of messages that cycle every 3 seconds
    Dots animate every second: "Text." -> "Text.." -> "Text..." -> "Next Text."
    """
    
    # Step-specific loading messages
    STEP_MESSAGES: Dict[str, List[str]] = {
        "overview": [
            "→ Fetching website content",
            "→ Analyzing business model", 
            "→ Understanding value proposition",
            "→ Mapping product features",
            "→ Finalizing company overview"
        ],
        "account": [
            "→ Analyzing target market",
            "→ Identifying ideal customer profiles",
            "→ Researching market segments", 
            "→ Building account criteria",
            "→ Finalizing target account profile"
        ],
        "persona": [
            "→ Researching buyer personas",
            "→ Analyzing decision makers",
            "→ Understanding pain points",
            "→ Mapping buying process",
            "→ Finalizing buyer persona"
        ],
        "email": [
            "→ Crafting personalized messaging",
            "→ Optimizing email structure",
            "→ Incorporating talking poitns",
            "→ Refining call-to-action",
            "→ Finalizing email campaign"
        ],
        "plan": [
            "→ Synthesizing GTM strategy",
            "→ Building scoring frameworks",
            "→ Recommending tool stack",
            "→ Creating implementation plan",
            "→ Finalizing strategic plan"
        ]
    }
    
    def __init__(self, console: Console):
        self.console = console
        self.progress = None
        self.task_id = None
        self.stop_animation = False
        self.animation_thread = None
        
    def start_animation(self, step_key: str) -> None:
        """Start animated loading for a specific step using Rich Progress"""
        if step_key not in self.STEP_MESSAGES:
            step_key = "overview"  # Fallback
            
        # Create Rich Progress with spinner and timer
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False
        )
        
        self.progress.start()
        self.task_id = self.progress.add_task("", total=None)
        
        # Start animation thread
        self.stop_animation = False
        self.animation_thread = threading.Thread(
            target=self._animate_messages, 
            args=(self.STEP_MESSAGES[step_key],)
        )
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
    def stop(self) -> None:
        """Stop the animation and progress"""
        self.stop_animation = True
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
        if self.progress:
            self.progress.stop()
            
    def _animate_messages(self, messages: List[str]) -> None:
        """Animate through messages with progressive dots"""
        message_index = 0
        dot_count = 1
        message_start_time = time.time()
        
        while not self.stop_animation:
            # Current message
            current_msg = messages[message_index]
            
            # Add progressive dots
            dots = "." * dot_count
            animated_message = f"{current_msg}{dots}"
            
            # Update the progress task description
            if self.progress and self.task_id is not None:
                self.progress.update(self.task_id, description=animated_message)
            
            # Wait 1 second
            time.sleep(1)
            
            # Update dot count
            dot_count += 1
            if dot_count > 3:
                dot_count = 1
                
                # Check if we should move to next message (every 3 seconds)
                if time.time() - message_start_time >= 3:
                    message_index += 1
                    message_start_time = time.time()
                    
                    # If we've reached the end of messages, stay on last message
                    if message_index >= len(messages):
                        message_index = len(messages) - 1

# Convenience function for quick usage
def create_step_animator(console: Console, step_key: str) -> LoadingAnimator:
    """Create and start animator for a specific step"""
    animator = LoadingAnimator(console)
    animator.start_animation(step_key)
    return animator

# Export the step keys for validation
AVAILABLE_STEPS = list(LoadingAnimator.STEP_MESSAGES.keys())