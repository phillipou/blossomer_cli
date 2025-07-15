"""
Logging and error handling utilities for the CLI.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.text import Text
from rich.panel import Panel


class CLILogger:
    """Centralized logging for the CLI application."""
    
    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet
        self.console = Console()
        
        # Set up Python logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up Python logging configuration."""
        level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gtm_projects/.cli.log', mode='a'),
                logging.StreamHandler(sys.stderr) if self.verbose else logging.NullHandler()
            ]
        )
        
        # Reduce noise from external libraries
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if not self.quiet:
            self.console.print(message, **kwargs)
        logging.info(message)
    
    def success(self, message: str, **kwargs) -> None:
        """Log success message."""
        if not self.quiet:
            self.console.print(f"[green]✓[/green] {message}", **kwargs)
        logging.info(f"SUCCESS: {message}")
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if not self.quiet:
            self.console.print(f"[yellow]⚠️[/yellow] {message}", **kwargs)
        logging.warning(message)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.console.print(f"[red]❌[/red] {message}", **kwargs)
        logging.error(message)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        if self.verbose:
            self.console.print(f"[dim]DEBUG: {message}[/dim]", **kwargs)
        logging.debug(message)
    
    def progress(self, step: int, total: int, message: str, **kwargs) -> None:
        """Log progress message."""
        if not self.quiet:
            self.console.print(f"[{step}/{total}] {message}", **kwargs)
        logging.info(f"PROGRESS [{step}/{total}]: {message}")
    
    def micro_progress(self, message: str, status: str = "...", **kwargs) -> None:
        """Log micro-progress message."""
        if not self.quiet:
            if status == "done":
                self.console.print(f"   → {message} ✓", **kwargs)
            else:
                self.console.print(f"   → {message} {status}", **kwargs)
        logging.debug(f"MICRO: {message} {status}")


class CLIError(Exception):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, suggestions: Optional[list] = None, exit_code: int = 1):
        self.message = message
        self.suggestions = suggestions or []
        self.exit_code = exit_code
        super().__init__(message)


class DomainError(CLIError):
    """Error related to domain processing."""
    pass


class FileError(CLIError):
    """Error related to file operations."""
    pass


class APIError(CLIError):
    """Error related to API calls."""
    
    def __init__(self, message: str, retry_possible: bool = True, **kwargs):
        self.retry_possible = retry_possible
        super().__init__(message, **kwargs)


class GenerationError(CLIError):
    """Error during content generation."""
    pass


def handle_cli_error(error: Exception, logger: CLILogger) -> int:
    """
    Handle CLI errors with user-friendly messages and suggestions.
    
    Args:
        error: The exception that occurred
        logger: Logger instance for output
        
    Returns:
        Exit code for the application
    """
    if isinstance(error, CLIError):
        # Display the main error
        logger.error(error.message)
        
        # Show suggestions if available
        if error.suggestions:
            logger.console.print()
            for suggestion in error.suggestions:
                logger.console.print(f"   → {suggestion}")
        
        return error.exit_code
    
    elif isinstance(error, KeyboardInterrupt):
        logger.console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130  # Standard exit code for Ctrl+C
    
    elif isinstance(error, FileNotFoundError):
        logger.error(f"File not found: {error.filename}")
        logger.console.print("   → Check the file path and try again")
        return 2
    
    elif isinstance(error, PermissionError):
        logger.error(f"Permission denied: {error.filename}")
        logger.console.print("   → Check file permissions")
        return 2
    
    else:
        # Unexpected error
        logger.error(f"Unexpected error: {str(error)}")
        if logger.verbose:
            import traceback
            logger.console.print(traceback.format_exc())
        else:
            logger.console.print("   → Run with --verbose for more details")
        return 1


def create_error_panel(title: str, message: str, suggestions: list) -> Panel:
    """Create a rich panel for error display."""
    content = [message]
    
    if suggestions:
        content.append("")
        for suggestion in suggestions:
            content.append(f"→ {suggestion}")
    
    return Panel(
        "\n".join(content),
        title=f"[red]{title}[/red]",
        border_style="red"
    )


# Example usage and testing
if __name__ == "__main__":
    # Test the logger
    logger = CLILogger(verbose=True)
    
    logger.info("Testing CLI logger")
    logger.success("Operation completed successfully")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")
    logger.progress(1, 5, "🔍 Analyzing company...")
    logger.micro_progress("Fetching website content", "...")
    logger.micro_progress("Fetching website content", "done")
    
    # Test error handling
    try:
        raise DomainError(
            "Invalid domain format: invalid..domain",
            suggestions=[
                "Try: acme.com",
                "Or: https://example.com"
            ]
        )
    except Exception as e:
        exit_code = handle_cli_error(e, logger)
        print(f"Would exit with code: {exit_code}")