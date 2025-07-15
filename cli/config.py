"""
Configuration management for the CLI application.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from cli.utils.file_manager import ProjectManager


@dataclass
class CLIConfig:
    """Configuration settings for the CLI."""
    
    # API Configuration
    openai_api_key: Optional[str] = None
    
    # Editor Configuration  
    default_editor: str = "auto"
    
    # Output Configuration
    color_output: bool = True
    show_timing: bool = True
    verbose: bool = False
    quiet: bool = False
    
    # Project Configuration
    auto_regenerate_deps: bool = True
    projects_path: Optional[str] = None
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CLIConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    def update(self, **kwargs) -> 'CLIConfig':
        """Return new config with updated values."""
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data)


class ConfigManager:
    """Manages CLI configuration from multiple sources."""
    
    def __init__(self):
        self.project_manager = ProjectManager()
        self._config = None
    
    def get_config(self) -> CLIConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def save_config(self, config: CLIConfig) -> None:
        """Save configuration to global state."""
        state = self.project_manager.load_global_state()
        state['config'] = config.to_dict()
        self.project_manager.save_global_state(state)
        self._config = config
    
    def update_config(self, **kwargs) -> CLIConfig:
        """Update configuration with new values."""
        config = self.get_config()
        updated_config = config.update(**kwargs)
        self.save_config(updated_config)
        return updated_config
    
    def _load_config(self) -> CLIConfig:
        """Load configuration from all sources."""
        # Start with defaults
        config_data = {}
        
        # 1. Load from global state file
        state = self.project_manager.load_global_state()
        if 'config' in state:
            config_data.update(state['config'])
        
        # 2. Override with environment variables
        env_overrides = self._get_env_overrides()
        config_data.update(env_overrides)
        
        return CLIConfig.from_dict(config_data)
    
    def _get_env_overrides(self) -> Dict[str, Any]:
        """Get configuration overrides from environment variables."""
        overrides = {}
        
        # API Keys
        if os.getenv('OPENAI_API_KEY'):
            overrides['openai_api_key'] = os.getenv('OPENAI_API_KEY')
        
        # Editor
        if os.getenv('GTM_CLI_EDITOR'):
            overrides['default_editor'] = os.getenv('GTM_CLI_EDITOR')
        
        # Output settings
        if os.getenv('GTM_CLI_NO_COLOR'):
            overrides['color_output'] = False
        
        if os.getenv('GTM_CLI_QUIET'):
            overrides['quiet'] = True
            
        if os.getenv('GTM_CLI_VERBOSE'):
            overrides['verbose'] = True
        
        # Project path
        if os.getenv('GTM_CLI_PROJECTS_PATH'):
            overrides['projects_path'] = os.getenv('GTM_CLI_PROJECTS_PATH')
        
        return overrides
    
    def validate_config(self) -> list:
        """Validate configuration and return list of issues."""
        config = self.get_config()
        issues = []
        
        # Check for required API key
        if not config.openai_api_key:
            issues.append(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or run: gtm-cli config set openai_api_key YOUR_KEY"
            )
        
        # Check projects path if specified
        if config.projects_path:
            path = Path(config.projects_path)
            if not path.exists():
                issues.append(f"Projects path does not exist: {config.projects_path}")
            elif not path.is_dir():
                issues.append(f"Projects path is not a directory: {config.projects_path}")
        
        return issues
    
    def get_projects_path(self) -> Path:
        """Get the projects directory path."""
        config = self.get_config()
        if config.projects_path:
            return Path(config.projects_path)
        return Path.cwd() / "gtm_projects"


def get_api_key() -> Optional[str]:
    """Get OpenAI API key from configuration."""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    return config.openai_api_key


def require_api_key() -> str:
    """Get OpenAI API key or raise error if not available."""
    api_key = get_api_key()
    if not api_key:
        from cli.utils.logging import CLIError
        raise CLIError(
            "OpenAI API key not found",
            suggestions=[
                "Set environment variable: export OPENAI_API_KEY=your_key",
                "Or run: gtm-cli config set openai_api_key your_key"
            ]
        )
    return api_key


# Example usage and testing
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    print("Current configuration:")
    config = config_manager.get_config()
    for key, value in config.to_dict().items():
        # Don't print API keys in full
        if 'key' in key.lower() and value:
            value = f"{value[:8]}..." if len(value) > 8 else value
        print(f"  {key}: {value}")
    
    print(f"\nProjects path: {config_manager.get_projects_path()}")
    
    print("\nValidation issues:")
    issues = config_manager.validate_config()
    for issue in issues:
        print(f"  - {issue}")
    
    if not issues:
        print("  No issues found")