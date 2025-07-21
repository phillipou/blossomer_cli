"""
Color system for Blossomer CLI - Consistent semantic color usage
Following CLI UX best practices from https://clig.dev/#output
"""

from typing import Dict, Any
from rich.console import Console
import os

class Colors:
    """
    Centralized color definitions following semantic meaning
    Based on CLI UX best practices - use color with intention
    """
    
    # Core semantic colors - unified brand theme
    SUCCESS = "green"           # ✓ Completed tasks, positive outcomes
    ERROR = "#DB2D20"           # ✗ Failures, missing data, critical issues  
    WARNING = "#FDED02"         # ⚠ Stale data, non-critical issues
    PRIMARY = "bold #01A0E4"    # Section headers, current process - brand blue
    ACTION = "bold #01A0E4"     # Commands, actionable items - brand blue
    META = "#A5A2A2"            # Timestamps, file info, secondary details
    EMPHASIS = "bold"           # Important labels (use sparingly)
    USER_INPUT = "#00BFFF"      # User input, interactive elements - cyan for contrast
    
    # Compound styles for common patterns - all using brand blue
    SECTION_HEADER = "bold #01A0E4"    # Main section titles 
    SUCCESS_MESSAGE = "green"          # ✓ Success indicators
    ERROR_MESSAGE = "#DB2D20"          # ✗ Error indicators  
    WARNING_MESSAGE = "#FDED02"        # ⚠ Warning indicators
    COMMAND_SUGGESTION = "bold #01A0E4"  # → Try: command
    PROCESS_INDICATOR = "bold #01A0E4"   # [1/4] Step name 
    FILE_INFO = "#A5A2A2"             # Generated: timestamp
    
    @classmethod
    def should_use_color(cls) -> bool:
        """
        Check if colors should be used based on CLI best practices
        Disable colors when:
        - NO_COLOR environment variable is set
        - TERM is 'dumb' 
        - Output is not interactive terminal
        """
        if os.environ.get('NO_COLOR'):
            return False
        if os.environ.get('TERM') == 'dumb':
            return False
        # Could add more terminal detection here
        return True
    
    @classmethod
    def format_success(cls, text: str) -> str:
        """Format success message with consistent styling"""
        if not cls.should_use_color():
            return f"✓ {text}"
        return f"✓ [{cls.SUCCESS}]{text}[/{cls.SUCCESS}]"
    
    @classmethod
    def format_error(cls, text: str) -> str:
        """Format error message with consistent styling"""
        if not cls.should_use_color():
            return f"✗ {text}"
        return f"✗ [{cls.ERROR}]{text}[/{cls.ERROR}]"
    
    @classmethod
    def format_warning(cls, text: str) -> str:
        """Format warning message with consistent styling"""
        if not cls.should_use_color():
            return f"⚠ {text}"
        return f"⚠ [{cls.WARNING}]{text}[/{cls.WARNING}]"
    
    @classmethod
    def format_section(cls, text: str, icon: str = "") -> str:
        """Format section header with consistent styling"""
        if not cls.should_use_color():
            return f"{icon} {text}".strip()
        return f"{icon} [{cls.SECTION_HEADER}]{text}[/{cls.SECTION_HEADER}]".strip()
    
    @classmethod
    def format_command(cls, text: str) -> str:
        """Format command suggestion with consistent styling"""
        if not cls.should_use_color():
            return text
        return f"[{cls.COMMAND_SUGGESTION}]{text}[/{cls.COMMAND_SUGGESTION}]"
    
    @classmethod
    def format_process(cls, step: int, total: int, name: str) -> str:
        """Format process indicator with consistent styling"""
        if not cls.should_use_color():
            return f"[{step}/{total}] {name}"
        return f"[{step}/{total}] [{cls.PROCESS_INDICATOR}]{name}[/{cls.PROCESS_INDICATOR}]"
    
    @classmethod
    def format_meta(cls, text: str) -> str:
        """Format metadata with consistent styling"""
        if not cls.should_use_color():
            return text
        return f"[{cls.META}]{text}[/{cls.META}]"

def format_project_status(domain: str, steps: list, progress: float, has_stale: bool = False) -> str:
    """Format compact project status line"""
    parts = [
        f"📁 {domain}",
        Colors.format_success(", ".join(steps)),
        f"[{Colors.PRIMARY}]{progress:.0f}%[/{Colors.PRIMARY}]"
    ]
    
    if has_stale:
        parts.append(Colors.format_warning("May need updates"))
    
    return " | ".join(parts)

def format_step_flow(steps: list) -> str:
    """Format the step flow with consistent colors"""
    formatted_steps = []
    for step in steps:
        formatted_steps.append(f"[{Colors.SUCCESS}]{step}[/{Colors.SUCCESS}]")
    
    return " → ".join(formatted_steps)

# Example usage patterns
if __name__ == "__main__":
    console = Console()
    
    print("=== Color System Demo ===")
    console.print(Colors.format_success("Company Overview generated successfully"))
    console.print(Colors.format_error("Failed to generate Target Account: API error"))
    console.print(Colors.format_warning("Some data may be outdated"))
    console.print(Colors.format_section("COMPANY OVERVIEW - Preview", "📋"))
    console.print(f"→ Try: {Colors.format_command('blossomer init domain.com')}")
    console.print(Colors.format_process(2, 4, "Target Account Profile"))
    console.print(Colors.format_meta("Generated: 2025-07-16 15:30:45"))
    
    print("\n=== Status Examples ===")
    console.print(format_project_status("blossomer.io", ["overview", "account"], 75.0, True))
    console.print(format_step_flow(["Overview", "Account Profile", "Buyer Persona", "Email Campaign"]))