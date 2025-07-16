"""
Console utilities for enhanced terminal experience
"""

import os
import sys
from rich.console import Console

def clear_console() -> None:
    """Clear the console for an immersive experience"""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Unix/Linux/MacOS
    else:
        os.system('clear')

def enter_immersive_mode() -> None:
    """Clear console and enter immersive mode like Claude Code"""
    clear_console()
    # Optional: Hide cursor for cleaner experience (can be added later)
    # sys.stdout.write('\033[?25l')
    # sys.stdout.flush()

def exit_immersive_mode() -> None:
    """Exit immersive mode and restore normal console"""
    # Optional: Show cursor again
    # sys.stdout.write('\033[?25h')
    # sys.stdout.flush()
    pass

def add_bottom_padding(console: Console, lines: int = 3) -> None:
    """Add bottom padding to prevent input from being stuck to terminal edge"""
    for _ in range(lines):
        console.print()

def ensure_breathing_room(console: Console) -> None:
    """Add dynamic spacing based on terminal size"""
    try:
        terminal_height = os.get_terminal_size().lines
        # Add 5% of terminal height as padding, minimum 2 lines
        padding = max(2, terminal_height // 20)
        add_bottom_padding(console, padding)
    except OSError:
        # Fallback if terminal size can't be determined
        add_bottom_padding(console, 3)