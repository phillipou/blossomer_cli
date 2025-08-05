"""
ASCII art utilities for Blossomer CLI
"""

from rich.text import Text
from rich.console import Console
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

def get_blossomer_ascii_art() -> str:
    """Return the Blossomer ASCII art - dynamically generated based on terminal size"""
    if PYFIGLET_AVAILABLE:
        try:
            # Get terminal width for responsive rendering
            console = Console()
            width = console.width
            
            # Use 'big' font for a clean, readable look
            # Don't use pyfiglet's justify, we'll center it manually
            fig = pyfiglet.Figlet(font='big', width=200)  # Use large width to prevent wrapping
            ascii_art = fig.renderText('BLOSSOMER')
            
            # Center each line manually
            lines = ascii_art.strip().split('\n')
            centered_lines = []
            for line in lines:
                # Strip trailing spaces and center
                line = line.rstrip()
                if line:  # Only center non-empty lines
                    padding = (width - len(line)) // 2
                    centered_lines.append(' ' * max(0, padding) + line)
                else:
                    centered_lines.append('')
            
            return '\n'.join(centered_lines)
        except Exception:
            # Fallback if pyfiglet fails
            pass
    
    # Fallback ASCII art if pyfiglet is not available
    return r"""
 ____  _                                        
| __ )| | ___  ___ ___  ___  _ __ ___   ___ _ __ 
|  _ \| |/ _ \/ __/ __|/ _ \| '_ ` _ \ / _ \ '__|
| |_) | | (_) \__ \__ \ (_) | | | | | |  __/ |   
|____/|_|\___/|___/___/\___/|_| |_| |_|\___|_|   
"""

def get_blossomer_ascii_art_styled() -> Text:
    """Return styled Blossomer ASCII art with brand blue color"""
    ascii_text = get_blossomer_ascii_art()
    # Use solid brand blue color instead of gradient for cleaner look
    styled_text = Text(ascii_text, style="bold #0066CC")
    return styled_text

def create_ascii_welcome_panel() -> Text:
    """Create a welcome panel with ASCII art"""
    # Create the ASCII art text
    ascii_text = get_blossomer_ascii_art_styled()
    
    # Get terminal width for centering the welcome message
    console = Console()
    width = console.width
    
    # Create centered welcome message
    welcome_line1 = "🚀 Welcome to Blossomer GTM CLI"
    welcome_line2 = "A Complete AI-Powered GTM System in Your Terminal"
    
    # Center each line
    padding1 = (width - len(welcome_line1)) // 2
    padding2 = (width - len(welcome_line2)) // 2
    
    welcome_msg = Text()
    welcome_msg.append("\n")
    welcome_msg.append(" " * max(0, padding1) + welcome_line1 + "\n", style="bold")
    welcome_msg.append(" " * max(0, padding2) + welcome_line2, style="dim")
    
    # Combine ASCII art and message
    combined_text = Text()
    combined_text.append(ascii_text)
    combined_text.append(welcome_msg)
    
    return combined_text

def show_init_splash_screen(console: Console) -> None:
    """Display the initialization splash screen with ASCII art"""
    console.clear()
    console.print()
    # Don't use justify="center" on the panel since we're centering manually
    console.print(create_ascii_welcome_panel())
    console.print()
    console.print("Press Enter to continue...", style="dim", justify="center")
    input()