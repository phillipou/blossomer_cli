"""
Menu utilities for CLI interactions with numbered selections
"""

from typing import List, Optional
import questionary
from questionary import Style
import sys

# Import consistent styling
MENU_STYLE = Style([
    ('question', 'bold blue_violet'),
    ('pointer', 'bold blue_violet'),
    ('highlighted', 'bold blue_violet'),
    ('selected', 'bold blue_violet'),
    ('answer', 'bold blue_violet')
])

def numbered_menu_with_keys(question: str, choices: List[str]) -> Optional[str]:
    """
    Show a menu with true number key support (1, 2, 3, etc.)
    Returns the selected choice, or None if cancelled
    """
    from rich.console import Console
    from rich.prompt import Prompt
    
    console = Console()
    
    # Display the question and choices
    console.print(f"[bold blue_violet]? {question}[/bold blue_violet]")
    for i, choice in enumerate(choices, 1):
        console.print(f"  [dim]{i}.[/dim] {choice}")
    console.print()
    
    # Get numeric input
    while True:
        try:
            choice_input = Prompt.ask(
                "[dim]Enter choice (1-{}) or press Ctrl+C to cancel[/dim]".format(len(choices)),
                default=""
            ).strip()
            
            if not choice_input:
                continue
                
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                console.print(f"[red]Please enter a number between 1 and {len(choices)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
        except KeyboardInterrupt:
            return None

def numbered_menu(question: str, choices: List[str], style: Optional[Style] = None) -> Optional[str]:
    """
    Show a menu with numbered options that supports both arrow keys AND number key shortcuts
    Number keys immediately select (no need to press Enter)
    Returns the selected choice, or None if cancelled
    """
    import questionary
    from prompt_toolkit.key_binding import KeyBindings
    
    # Use questionary's built-in shortcut system (removes duplicate numbering)
    choice_objects = []
    for i, choice in enumerate(choices):
        if i < 9:  # Only first 9 get shortcuts
            choice_obj = questionary.Choice(
                title=choice,  # Clean title - questionary will add the shortcut number
                value=choice,
                shortcut_key=str(i+1)
            )
        else:
            choice_obj = questionary.Choice(
                title=f"{i+1}) {choice}",  # Manual numbering for 10+
                value=choice
            )
        choice_objects.append(choice_obj)
    
    # Use questionary's built-in shortcuts (focuses, doesn't immediately select)
    result = questionary.select(
        question,
        choices=choice_objects,
        style=style or MENU_STYLE,
        use_shortcuts=True,
        instruction="(Use arrow keys or shortcuts + Enter)"
    ).ask()
    
    return result

def show_menu_with_numbers(question: str, choices: List[str], add_separator: bool = True, use_number_keys: bool = True) -> str:
    """
    Show a menu with numbered options and visual separator
    Supports both arrow key navigation AND number key shortcuts (1, 2, 3, etc.)
    Raises KeyboardInterrupt if user cancels
    """
    from cli.utils.console import ensure_breathing_room
    from rich.console import Console
    
    console = Console()
    
    if add_separator:
        console.print()
        console.print("─" * 60)
        console.print()
    
    # Use the enhanced numbered menu with both arrow keys and number shortcuts
    result = numbered_menu(question, choices)
    
    ensure_breathing_room(console)
    
    # Handle CTRL+C (questionary returns None when interrupted)
    if result is None:
        raise KeyboardInterrupt()
    
    return result