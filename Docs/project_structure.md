# Project Structure

## Root Directory

```
blossomer-cli/
├── cli/                          # CLI-specific code
│   ├── __init__.py
│   ├── main.py                   # Main Typer app entry point
│   ├── commands/                 # Individual command implementations
│   │   ├── __init__.py
│   │   ├── init.py              # init command with 5-step flow
│   │   ├── show.py              # show command with Rich formatting
│   │   ├── export.py            # export command for markdown
│   │   ├── generate.py          # generate individual steps
│   │   ├── edit.py              # edit files with system editor
│   │   └── list.py              # list all projects
│   ├── utils/                   # CLI utilities
│   │   ├── __init__.py
│   │   ├── formatting.py        # Rich formatting helpers
│   │   ├── file_manager.py      # Project file management
│   │   ├── editor.py            # System editor integration
│   │   ├── prompts.py           # Questionary prompt helpers
│   │   └── progress.py          # Progress indicators
│   ├── config.py                # Configuration management
│   └── exceptions.py            # CLI-specific exceptions
├── app/                         # Adapted existing services
│   ├── __init__.py
│   ├── services/                # Reused LLM and generation services
│   │   ├── __init__.py
│   │   ├── email_generation_service.py      # Reused
│   │   ├── product_overview_service.py      # Reused
│   │   ├── target_account_service.py        # Reused
│   │   ├── target_persona_service.py        # Reused
│   │   ├── gtm_plan_service.py             # New for CLI
│   │   ├── llm_service.py                  # Reused
│   │   ├── context_orchestrator_service.py # Reused
│   │   └── web_content_service.py          # Reused
│   ├── prompts/                 # Prompt templates and management
│   │   ├── __init__.py
│   │   ├── base.py              # Reused
│   │   ├── models.py            # Reused
│   │   ├── registry.py          # Reused
│   │   ├── runner.py            # Reused
│   │   └── templates/           # Jinja2 templates
│   │       ├── product_overview.jinja2     # Reused
│   │       ├── target_account.jinja2       # Reused
│   │       ├── target_persona.jinja2       # Reused
│   │       ├── email_generation_blossomer.jinja2  # Reused
│   │       └── gtm_plan.jinja2             # New template
│   ├── schemas/                 # Pydantic models adapted for CLI
│   │   ├── __init__.py
│   │   ├── cli_models.py        # CLI-specific models
│   │   └── api_models.py        # Adapted from existing schemas
│   └── core/                    # Core utilities
│       ├── __init__.py
│       └── llm_singleton.py     # Adapted for CLI use
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── cli/                     # CLI-specific tests
│   │   ├── __init__.py
│   │   ├── test_commands.py     # Command functionality tests
│   │   ├── test_utils.py        # Utility function tests
│   │   └── test_integration.py  # End-to-end workflow tests
│   └── fixtures/                # Test data and fixtures
│       ├── sample_projects/     # Sample GTM projects for testing
│       └── mock_responses/      # Mock LLM responses
├── docs/                        # Documentation
│   ├── Implementation.md        # This implementation plan
│   ├── project_structure.md     # This file
│   ├── UI_UX_doc.md            # CLI UX documentation
│   └── PRD.md                  # Original product requirements
├── scripts/                     # Utility scripts
│   ├── setup_dev.py            # Development environment setup
│   ├── clean_projects.py       # Clean up test projects
│   └── migrate_data.py         # Data migration utilities
├── gtm_projects/               # User project storage (created at runtime)
│   ├── .gtm-cli-state.json    # Global CLI state
│   └── {domain}/              # Individual project directories
│       ├── overview.json      # Company analysis
│       ├── account.json       # Target account profile
│       ├── persona.json       # Buyer persona
│       ├── email.json         # Email campaign
│       ├── plan.json          # GTM execution plan
│       ├── .metadata.json     # Generation metadata
│       └── export/            # Exported reports
│           └── gtm-report-{date}.md
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Package configuration
├── setup.py                   # Package setup (if needed)
├── README.md                  # Project documentation
├── .gitignore                 # Git ignore rules
└── .env.example               # Environment variables template
```

## Detailed Structure Explanation

### CLI Directory (`cli/`)

**Purpose:** Contains all CLI-specific code that doesn't exist in the current web application.

**Key Files:**
- `main.py`: Entry point using Typer, defines the main app and global options
- `commands/`: Each command gets its own module for maintainability
- `utils/`: Shared utilities for formatting, file management, and user interaction
- `config.py`: Handles configuration, API keys, and user preferences

### Adapted App Directory (`app/`)

**Purpose:** Reuses existing business logic while removing web-specific components.

**Services Directory (`app/services/`):**
- **Reused Files:** Keep all LLM generation services as they contain the core business logic
- **New File:** `gtm_plan_service.py` for the new GTM plan generation step
- **Removed:** Web scraper cache, authentication services, database services

**Prompts Directory (`app/prompts/`):**
- **Reused:** All existing prompt templates and management code
- **Enhanced:** Add `cli_summary` fields to existing templates for CLI display
- **New:** `gtm_plan.jinja2` template for the 5th step

**Schemas Directory (`app/schemas/`):**
- **Adapted:** Existing Pydantic models for CLI context
- **New:** CLI-specific models for command arguments and responses

### Test Directory (`tests/`)

**Purpose:** Comprehensive testing for CLI functionality.

**Structure:**
- `cli/`: Tests specific to CLI commands and utilities
- `fixtures/`: Sample data for testing generation workflows
- Integration tests for complete user workflows

### Project Storage (`gtm_projects/`)

**Purpose:** Runtime directory for user projects and state.

**Features:**
- Created automatically when CLI first runs
- Each domain gets its own subdirectory
- Metadata tracking for generation history
- Export subdirectory for markdown reports

### Configuration Files

**pyproject.toml:** Modern Python packaging with entry points for CLI commands
**requirements.txt:** Production dependencies (Typer, Rich, Questionary, existing deps)
**requirements-dev.txt:** Development tools (pytest, black, flake8, etc.)

## File Organization Patterns

### Command Structure
Each CLI command follows a consistent pattern:
```python
# cli/commands/init.py
import typer
from rich.console import Console
from questionary import prompt

app = typer.Typer()
console = Console()

@app.command()
def init(domain: str, yolo: bool = False, context: str = None):
    """Initialize new GTM project"""
    # Command implementation
```

### Module Imports
```python
# Standard library imports first
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Third-party imports
import typer
from rich.console import Console
from questionary import select, confirm

# Local imports
from app.services.product_overview_service import generate_company_overview
from cli.utils.formatting import display_summary
from cli.utils.file_manager import save_project_data
```

### Error Handling Pattern
```python
try:
    result = await generate_content(data)
except LLMServiceError as e:
    console.print(f"❌ Generation failed: {e}", style="red")
    if questionary.confirm("Retry?").ask():
        # Retry logic
    else:
        # Skip or abort
```

## Configuration Management

### Environment Variables
```bash
# .env.example
OPENAI_API_KEY=your_api_key_here
GTM_CLI_HOME=~/.gtm-cli
GTM_CLI_LOG_LEVEL=INFO
GTM_CLI_DEFAULT_EDITOR=code
```

### CLI State File
```json
// gtm_projects/.gtm-cli-state.json
{
  "version": "1.0.0",
  "default_editor": "code",
  "last_used_project": "acme.com",
  "user_preferences": {
    "auto_regenerate_deps": true,
    "show_timing": true,
    "color_output": true
  },
  "api_usage": {
    "total_requests": 150,
    "last_reset": "2024-01-01T00:00:00Z"
  }
}
```

## Package Structure

### Entry Points (pyproject.toml)
```toml
[project.scripts]
gtm-cli = "cli.main:app"

[project.entry-points."gtm_cli.commands"]
init = "cli.commands.init:app"
show = "cli.commands.show:app"
export = "cli.commands.export:app"
generate = "cli.commands.generate:app"
edit = "cli.commands.edit:app"
list = "cli.commands.list:app"
```

### Import Structure
```python
# cli/__init__.py
from cli.main import app

__version__ = "1.0.0"
__all__ = ["app"]
```

## Development Workflow

### Setting Up Development Environment
1. Remove unnecessary web components from `app/`
2. Create new `cli/` directory structure
3. Install CLI dependencies (Typer, Rich, Questionary)
4. Adapt existing services for CLI context
5. Implement command modules one by one
6. Add comprehensive testing

### File Naming Conventions
- CLI commands: lowercase with underscores (`init.py`, `show.py`)
- Utilities: descriptive names (`file_manager.py`, `formatting.py`)
- Services: keep existing naming (`email_generation_service.py`)
- Tests: prefix with `test_` (`test_commands.py`)

### Module Organization
- One command per file in `cli/commands/`
- Utilities grouped by functionality in `cli/utils/`
- Maintain existing service structure in `app/services/`
- CLI-specific models in separate files from API models

This structure provides clear separation between CLI and existing web components while maximizing code reuse and maintaining clean organization patterns.