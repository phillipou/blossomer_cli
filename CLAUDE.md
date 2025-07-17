# Blossomer GTM CLI - Development Guidelines

## Project Context
Building a CLI tool that demonstrates Blossomer's GTM intelligence by analyzing company domains and generating complete go-to-market packages. **Goal: Polished prototype ASAP** - be practical, avoid over-engineering.

## Code Quality Standards

### Python Standards
- **Type hints everywhere** - Typer + Pydantic make this natural
- **Docstrings for public functions** - Keep them concise and practical
- **Follow existing patterns** - Match the style in `app/services/` 
- **No premature optimization** - Get it working first, optimize if needed
- Python is aliased to /usr/bin/python3 (system Python) but pip is using /opt/homebrew/bin/pip (Homebrew Python). Let me use the correct pip for the system Python

### File Organization
- Follow `/Docs/project_structure.md` exactly
- One command per file in `cli/commands/`
- Utilities grouped by function in `cli/utils/`
- Reuse existing `app/services/` without modification when possible

### Error Handling Philosophy
- **Fail fast with clear messages** - Technical founders need actionable feedback
- **Graceful degradation** - Always offer next steps (→ Try: ..., → Or: ...)
- **No silent failures** - Every error should guide the user to success

## Practical Patterns

### CLI Command Structure
```python
# cli/commands/{command}.py
import typer
from rich.console import Console
from cli.utils.formatting import display_summary

app = typer.Typer()
console = Console()

@app.command()
def command_name(arg: str, flag: bool = False):
    """Clear one-line description"""
    # Implementation
```

### Service Integration
- Import existing services from `app/services/`
- Adapt for CLI context but don't rewrite core logic
- Add CLI-specific formatting in `cli/utils/`

### Testing Strategy
- **Integration tests over unit tests** - Test the full user workflow
- **Happy path first** - Core functionality must work perfectly
- **Error scenarios second** - Test common failure modes
- Use Typer's built-in testing utilities

## Dependencies
- **Stick to the plan**: Typer + Rich + Questionary + existing deps
- **No new frameworks** - Work with what we have
- **Justify any additions** - Must solve a specific problem we can't handle otherwise

## Common Commands to Run
```bash
# Development setup (when implemented)
pip install -e .

# Testing (when implemented) 
pytest tests/

# Code quality (add these when needed)
black cli/ app/
flake8 cli/ app/
mypy cli/ app/
```

## What NOT to Do (Anti-Patterns)
- ❌ **Custom configuration frameworks** - Use simple JSON files
- ❌ **Complex plugin systems** - Keep it simple and direct
- ❌ **Premature abstractions** - Solve actual problems, not imaginary ones
- ❌ **Over-engineered error handling** - Clear messages > complex retry logic
- ❌ **Custom logging frameworks** - Python's logging module is fine
- ❌ **Database migrations** - We're using JSON files, keep it simple

## Implementation Priority
1. **Get the 5-step flow working** - This is the core value
2. **Polish the terminal UX** - Rich formatting, progress indicators
3. **Error handling** - Clear recovery paths for users
4. **Performance** - Only optimize if it's actually slow

## Technical Debt Guidelines
- **Document shortcuts taken** - Comment why you chose the simple approach
- **Prefer readable over clever** - Technical founders will read this code
- **Consistent naming** - Follow existing patterns in `app/`
- **Single responsibility** - Functions should do one thing well

## CLI-Specific Patterns

### Progress Indicators
```python
# Use Rich for all progress display
from rich.progress import Progress
with Progress() as progress:
    task = progress.add_task("Analyzing...", total=100)
    # Work happens here
    progress.update(task, completed=50)
```

### User Interactions
```python
# Use Questionary for all prompts
import questionary
choice = questionary.select(
    "What would you like to do?",
    choices=["Continue", "Edit", "Regenerate", "Abort"]
).ask()
```

### File Operations
```python
# Use pathlib, save JSON with proper error handling
from pathlib import Path
import json

def save_project_data(domain: str, step: str, data: dict):
    project_dir = Path("gtm_projects") / domain
    project_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = project_dir / f"{step}.json"
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return file_path
```

## Performance Guidelines
- **Async where it matters** - LLM calls, file I/O
- **Cache API responses** - Don't regenerate unnecessarily  
- **Stream large outputs** - Don't load everything into memory
- **Measure first** - Don't optimize without profiling

## Remember
- **Ship working software** - Perfect is the enemy of good
- **Technical founders appreciate directness** - Clear, honest feedback
- **The CLI is a demo** - Show Blossomer's intelligence, not engineering complexity
- **Follow the docs** - `/Docs/Implementation.md` is the source of truth

## When in Doubt
1. Check existing patterns in `app/services/`
2. Prioritize user experience over code elegance
3. Ask "Does this help ship faster?" before adding complexity
4. Follow the 5-step flow specifications exactly

## Security and Ethical Considerations
- Always ask for my permission to run code that will make an API request to an LLM since it'll cost me $$$