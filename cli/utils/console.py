"""
Console utilities for enhanced terminal experience
"""

import os
import sys

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