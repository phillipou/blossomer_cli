# Blossomer GTM CLI - Technical Architecture

## Core Architecture Overview

### Complete 5-Step GTM Generation Pipeline
- **`init <domain>`** - Interactive 5-step GTM project generation
- **`show <asset>`** - Rich formatted asset display with syntax highlighting
- **`generate <step>`** - Individual step regeneration with dependency tracking
- **`export`** - Markdown report generation with meaningful naming
- **`eval`** - Comprehensive prompt quality assurance system
- **Hypothesis capture** - Optional context inputs for target account and persona
- **YOLO mode** - Non-interactive batch generation
- **System editor integration** - Auto-detected editor with fallbacks
- **Project state management** - Automatic dependency tracking and stale detection

### 5-Step Generation Flow
1. **Company Overview** - Domain analysis and business insights extraction
2. **Target Account** - Ideal customer profile with firmographics
3. **Buyer Persona** - Detailed persona with demographics and use cases
4. **Email Campaign** - Personalized email with guided 4-step builder
5. **GTM Strategic Plan** - Complete execution plan with scoring frameworks, tool recommendations, and Blossomer methodology

### Technical Infrastructure
- **TensorBlock Forge Integration** - Unified LLM access across 19+ models
- **Rich Terminal UI** - Beautiful formatting with progress indicators
- **JSON File Storage** - Structured project data with metadata
- **Error Handling** - Actionable error messages with recovery options

## Key Technology Stack

### Core Framework
- **Typer** - CLI framework with type hints and auto-completion
- **Rich** - Terminal formatting with progress indicators and syntax highlighting
- **Questionary** - Interactive prompts with [C/e/r/a] choice patterns
- **Pydantic** - Data validation and schema management
- **TensorBlock Forge** - Unified LLM access across multiple providers

### LLM Integration Benefits
- **Single API Key** - One FORGE_API_KEY for all providers (OpenAI, Anthropic, Gemini, xAI, Deepseek)
- **Cost Optimization** - GPT-4.1-nano at $0.000015/1K tokens (10x cheaper than alternatives)
- **Model Switching** - Easy A/B testing across providers via model parameters
- **Unified Error Handling** - Consistent error patterns across all providers

## Command Reference

```bash
# Core GTM Generation
python3 -m cli.main init acme.com           # Start interactive GTM generation
python3 -m cli.main show all                # Display all assets with formatting
python3 -m cli.main generate overview       # Regenerate specific step
python3 -m cli.main generate email          # Regenerate email with guided flow
python3 -m cli.main export                  # Generate markdown reports

# Evaluation System
python3 -m cli.main eval list               # List available evaluations
python3 -m cli.main eval run product_overview --sample-size 5
python3 -m cli.main eval run target_account --sample-size 5
python3 -m cli.main eval run all            # Run all evaluations
```

## Project Storage Structure

```
gtm_projects/
├── {domain}/
│   ├── json_output/           # All JSON files stored here (CLI source of truth)
│   │   ├── overview.json      # Company analysis
│   │   ├── account.json       # Target account profile  
│   │   ├── persona.json       # Buyer persona
│   │   ├── email.json         # Email campaign
│   │   └── strategic_plan.json # GTM execution plan
│   ├── plans/                 # Human-editable markdown files
│   │   ├── overview.md        # Editable company analysis
│   │   ├── account.md         # Editable target account
│   │   ├── persona.md         # Editable buyer persona
│   │   ├── email.md           # Editable email campaign
│   │   └── strategy.md  # Editable strategic plan
│   ├── .metadata.json         # Generation metadata
│   └── export/
│       └── gtm-report-{date}.md
└── .gtm-cli-state.json        # Global state/preferences
```

## Data Flow & Dependencies

1. **Company Overview** → Target Account
2. **Company Overview + Target Account** → Buyer Persona  
3. **All Previous Steps** → Email Campaign
4. **All Previous Steps** → GTM Strategic Plan

## Evaluation System Architecture

### Core Infrastructure (`evals/core/`)
- **Unified Runner**: Single command interface for all prompt evaluations
- **Reusable Judges**: Shared deterministic and LLM-based evaluation logic
- **Jinja2 Templates**: LLM judge prompts stored as easily editable .j2 files
- **Dataset Management**: Sampling and test case handling
- **Results System**: Parsing, rendering, and reporting

### Evaluation Flow
1. **Sample test cases** from CSV dataset (configurable size)
2. **Generate outputs** using same services as CLI application
3. **Run deterministic checks** (JSON validation, schema compliance, format rules)
4. **Execute LLM judges** (traceability, actionability, redundancy, context steering)
5. **Aggregate results** and generate reports
6. **Parse and render** results in readable format

### Cost-Effective Design
- **Ultra-Cheap Models**: GPT-4.1-nano (~$0.000015 per judge call)
- **Deterministic First**: Fast checks eliminate expensive LLM calls on bad outputs
- **Batch Processing**: Efficient evaluation of multiple test cases
- **Configurable Sampling**: Test with small samples during development

### Evaluation Structure
```
evals/
├── core/                      # Unified evaluation framework
│   ├── config.py             # YAML configuration management
│   ├── dataset.py            # CSV test case loading
│   ├── results.py            # Rich terminal output with actual field values
│   ├── runner.py             # Single command interface
│   └── judges/               # Evaluation logic
│       ├── deterministic.py      # Zero-cost validation checks
│       ├── llm_judge.py          # LLM-based evaluation with template-driven architecture
│       └── templates/            # Jinja2 templates for LLM judge categories
│           ├── system/           # System prompt templates (instructions & formats)
│           │   ├── content_integrity.j2
│           │   ├── business_insight.j2
│           │   └── account_targeting_quality.j2
│           └── user/             # User prompt templates (data + JSON format)
│               ├── content_integrity.j2
│               ├── business_insight.j2
│               └── account_targeting_quality.j2
├── prompts/                  # Per-prompt configurations
│   ├── product_overview/     # Product overview evaluation
│   ├── target_account/       # Target account profile evaluation
│   └── target_persona/       # Target persona profile evaluation
└── datasets/                 # Centralized test data
    └── eval_test_inputs.csv      # Shared test cases across evaluations
```

## Markdown Formatting System

### Architecture (`cli/utils/markdown_formatter.py`)
```python
# Base formatter with common functionality
class MarkdownFormatter:
    def format(self, data: dict, preview: bool = False, max_chars: int = 500) -> str
    def format_with_markers(self, data: dict, step_type: str) -> str  # Bidirectional sync support
    
# Specialized formatters for each JSON schema
class OverviewFormatter(MarkdownFormatter)    # overview.json
class AccountFormatter(MarkdownFormatter)     # account.json  
class PersonaFormatter(MarkdownFormatter)     # persona.json
class EmailFormatter(MarkdownFormatter)       # email.json

# Factory function for easy instantiation
def get_formatter(step_type: str) -> MarkdownFormatter
```

### Character Limits
- **Short Preview**: 200 characters (for command summaries)
- **Medium Preview**: 500 characters (for step previews)
- **Long Preview**: 1000 characters (for detailed views)

## Bidirectional JSON ↔ Markdown Sync (Experimental)

### Core Concept
```
JSON (Source of Truth) ←→ Plans (Editable) → Export (Final)
     ↑                        ↓                ↓
     └── CLI generates ────── User edits ──── Reports
```

### Key Features
- **🔄 Bidirectional Sync** - Edit markdown, automatically updates JSON
- **🛡️ Resilient Design** - Graceful handling of user edits and errors  
- **⚡ Never Blocks Workflow** - CLI continues working even with sync issues
- **🎯 Field Markers** - `{#field_name}` syntax enables reliable parsing
- **✏️ User Freedom** - Edit headers, add custom sections, change structure

### Future CLI Commands
```bash
blossomer plans generate [step|all]    # json → plans  
blossomer plans update [step|all]      # plans → json
blossomer plans sync [step|all]        # auto-detect changes
blossomer plans edit <step>            # edit with auto-sync
blossomer plans status                 # show sync status
```

**Implementation Philosophy**: *"Fail Soft, Continue Forward"* - Sync enhances the workflow but never breaks it. Orphaned fields are handled gracefully with clear recovery options.

## Development Guidelines

### Code Quality Standards
- **Type hints everywhere** - Typer + Pydantic make this natural
- **Docstrings for public functions** - Keep them concise and practical
- **Follow existing patterns** - Match the style in `app/services/`
- **No premature optimization** - Get it working first, optimize if needed

### Testing Philosophy
- **Integration tests over unit tests** - Test the full user workflow
- **Happy path first** - Core functionality must work perfectly
- **Error scenarios second** - Test common failure modes
- Use Typer's built-in testing utilities

### Error Handling Philosophy
- **Fail fast with clear messages** - Technical founders need actionable feedback
- **Graceful degradation** - Always offer next steps (→ Try: ..., → Or: ...)
- **No silent failures** - Every error guides the user to success
- **Save partial progress** - Prevent data loss on failures

### User Experience Principles
- **Ship working software** - Perfect is the enemy of good
- **Technical founders appreciate directness** - Clear, honest feedback
- **Be helpful, not salesy** - Focus on being relevant, not clever
- **Aim to make a good impression** - Goal is to start conversations

## Key Services Architecture

```
app/services/
├── product_overview_service.py     # Company analysis and insights
├── target_account_service.py       # Ideal customer profiling
├── target_persona_service.py       # Buyer persona generation
├── email_generation_service.py     # Email campaign creation
├── gtm_advisor_service.py          # Strategic plan synthesis
└── context_orchestrator_service.py # Cross-step data flow

cli/services/
├── gtm_generation_service.py       # Main generation orchestration
├── project_storage.py              # File I/O and state management
├── llm_singleton.py                # TensorBlock Forge integration
└── context_orchestrator_service.py # Context management
```

## Prompt Template System

```
app/prompts/templates/
├── product_overview.jinja2         # Company analysis prompt
├── target_account.jinja2           # Account profiling prompt
├── target_persona.jinja2           # Persona generation prompt
├── email_generation_blossomer.jinja2 # Email creation prompt
├── gtm_advisor.jinja2              # Strategic planning prompt
└── gtm_advisor_output.md           # Strategic plan template structure
```

**Template Philosophy**: Use Jinja2 for all LLM prompts with clear separation between system instructions and user data for maintainability and testing.