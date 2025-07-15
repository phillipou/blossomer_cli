"""
Debug utility for controlling debug output based on --debug flag
"""

import os

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled via environment variable"""
    return os.getenv('CLI_DEBUG_MODE', '').lower() == 'true'

def set_debug_mode(enabled: bool) -> None:
    """Set debug mode environment variable"""
    os.environ['CLI_DEBUG_MODE'] = 'true' if enabled else 'false'

def debug_print(message: str) -> None:
    """Print debug message only if debug mode is enabled"""
    if is_debug_enabled():
        print(message)