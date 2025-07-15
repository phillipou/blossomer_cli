# Implementation Plan for Blossomer GTM CLI Tool

## Feature Analysis

### Identified Features:

**Core Commands:**
- **`init <domain>`** - Start new GTM project with interactive flow through 5 steps
- **`show <asset>`** - Display generated assets with rich formatting  
- **`export`** - Export assets as markdown report
- **`generate <step>`** - Manually run/re-run specific steps
- **`edit <file>`** - Open generated file in system editor
- **`list`** - Show all GTM projects

**5-Step Generation Flow:**
1. **Company Overview** - Analyze domain and extract business insights
2. **Target Account** - Generate ideal customer profile with firmographics
3. **Buyer Persona** - Create detailed persona with demographics and use cases
4. **Email Campaign** - Generate personalized email with subject lines and segments
5. **GTM Plan** - Create 30-day execution roadmap with tools and metrics

**Interactive Features:**
- Progressive disclosure with user choices at each step
- Real-time editing with system editor integration
- Error recovery with retry/skip options
- YOLO mode for one-shot generation
- Context preservation across steps

**Output Management:**
- JSON file storage for each step
- Rich terminal formatting with progress indicators
- Export to markdown reports
- Project state management

### Feature Categorization:

**Must-Have Features:**
- Core CLI framework with Typer
- Interactive 5-step GTM flow
- LLM integration for content generation
- JSON file storage and management
- Rich terminal formatting
- Basic error handling

**Should-Have Features:**
- System editor integration with smart detection
- Project state management
- Export functionality
- YOLO mode for power users
- Dependency regeneration
- Progress indicators with micro-progress states
- Smart domain format handling
- Time-to-value metrics and cost tracking
- Copy-paste friendly command output

**Nice-to-Have Features:**
- Advanced error recovery
- API rate limit handling
- CLI auto-completion
- Custom prompt templates
- Batch processing capabilities

## Recommended Tech Stack

### CLI Framework:
- **Typer** - Modern CLI framework with type hints
- **Documentation:** https://typer.tiangolo.com/
- **Justification:** Built by FastAPI team, excellent type safety, auto-completion, matches existing Pydantic patterns

### Terminal Formatting:
- **Rich** - Beautiful terminal formatting and progress bars
- **Documentation:** https://rich.readthedocs.io/en/latest/
- **Justification:** Perfect for creating the formatted output shown in PRD, markdown rendering, progress indicators

### Interactive Prompts:
- **Questionary** - Beautiful interactive CLI prompts
- **Documentation:** https://github.com/tmbo/questionary
- **Justification:** Superior UX for the [C/e/r/a] choice patterns, validation, auto-completion

### Core Dependencies:
- **Pydantic** - Data validation (already in use)
- **Documentation:** https://docs.pydantic.dev/latest/
- **Justification:** Already integrated, perfect for CLI argument validation

### File Handling:
- **Pathlib** - Modern path handling (built-in)
- **JSON** - File storage (built-in)
- **Tempfile** - Temporary file handling (built-in)

### LLM Integration:
- **Existing Services** - Reuse current LLM service architecture
- **OpenAI Python Client** - Already integrated
- **Documentation:** https://platform.openai.com/docs/

## Implementation Status

**Current Status:** ✅ Stage 2 Complete - Ready for Stage 3  
**Last Updated:** July 15, 2025

### Completed Stages

#### ✅ Stage 1: Foundation & Setup (COMPLETED)
**Duration:** Completed in 1 day
**Dependencies:** None

#### Sub-steps:
- [x] Set up CLI project structure using Typer
- [x] Install and configure Rich for terminal formatting
- [x] Install and configure Questionary for interactive prompts
- [x] Create base CLI app with global options (--help, --version, --quiet, --verbose, --no-color, --yolo)
- [x] Implement smart domain format normalization (acme.com, www.acme.com, https://acme.com)
- [x] Add smart editor detection ($EDITOR, VS Code, vim, nano fallbacks)
- [x] Implement project directory management (gtm_projects/ structure)
- [x] Set up logging and error handling framework with actionable error messages
- [x] Create configuration management for API keys and settings
- [x] Remove unnecessary web app components from existing codebase
- [x] Adapt existing Pydantic schemas for CLI use

**Git Commits:**
- `07bf3f8` Initial project documentation and planning
- `f7c54a4` Set up CLI framework with Typer, Rich, and Questionary
- `a7ac035` Clean up web app components by moving to archive
- `763ba1a` Preserve core generation services and prompts for CLI reuse
- `f54eb20` Complete Stage 1: Foundation & Setup

**What's Working in Stage 1:**
- ✅ CLI framework with beautiful Rich formatting
- ✅ Interactive prompts with Questionary  
- ✅ Smart domain normalization (`acme.com` → `https://acme.com`)
- ✅ Editor auto-detection with fallbacks
- ✅ Project file management with metadata tracking
- ✅ Professional logging with actionable error messages
- ✅ Configuration system with environment variable support
- ✅ Clean project structure with web components archived

**Testing:** All foundation components tested and working. Run testing commands:
```bash
python3 -m cli.main --help          # CLI help
python3 -m cli.main demo             # Rich formatting test
python3 -m cli.utils.domain          # Domain normalization test
python3 -m cli.utils.editor          # Editor detection test
python3 -m cli.utils.file_manager    # File management test
```

## Implementation Stages

### Stage 1: Foundation & Setup ✅ COMPLETED

#### ✅ Stage 2: Core Generation Engine (COMPLETED)
**Duration:** Completed in 1 day
**Dependencies:** ✅ Stage 1 completion

#### Sub-steps:
- [x] Adapt existing LLM services for CLI context (remove web dependencies)
- [x] Implement company overview generation (reuse existing product_overview_service.py)
- [x] Implement target account generation (reuse existing target_account_service.py)  
- [x] Implement buyer persona generation (reuse existing target_persona_service.py)
- [x] Implement email campaign generation (reuse existing email_generation_service.py)
- [ ] Create new GTM plan generation service (deferred - needs schema/template)
- [ ] Add CLI summary field generation to all prompt templates (deferred - for Stage 3)
- [x] Implement JSON file storage and retrieval for each step
- [x] Create data dependency tracking between steps

**Git Commits:**
- `a00847d` Add CLI-adapted LLM services
- `d802480` Add CLI-adapted generation services for Steps 1-4
- `3f5578c` Add comprehensive project storage system
- `f34e791` Add GTM generation orchestration service
- `bfff997` Add comprehensive testing suite for Stage 2

**What's Working in Stage 2:**
- ✅ CLI-adapted LLM services (removed FastAPI/HTTPException dependencies)
- ✅ Complete 4-step generation pipeline (overview → account → persona → email)
- ✅ JSON file storage system with gtm_projects/{domain}/*.json structure
- ✅ Data dependency tracking and stale detection
- ✅ Project lifecycle management (create/delete/list/status)
- ✅ GTM orchestration service for complete flow management
- ✅ Force regeneration with automatic dependent step marking
- ✅ Comprehensive testing suite with unit and integration tests

**Testing:** All core generation components tested and working. Run testing commands:
```bash
cd tests && python3 run_all_tests.py     # Comprehensive component tests (NEW)
python3 interactive_test.py              # Interactive usage scenarios  
python3 -c "from cli.services.gtm_generation_service import gtm_service; print('✓ GTM service ready')"

# Individual test modules:
cd tests && python3 test_domain_utils.py     # Domain normalization tests
cd tests && python3 test_project_storage.py  # Project storage tests
cd tests && python3 test_dependencies.py     # Dependency tracking tests
cd tests && python3 test_services.py         # Service integration tests
```

### 🔄 Stage 3: Interactive CLI Commands (NEXT)
**Duration:** 2-3 weeks
**Dependencies:** ✅ Stage 2 completion

#### Sub-steps:
- [ ] Implement `init` command with full interactive flow
- [ ] Add micro-progress indicators (→ Fetching website... ✓, → Processing with AI... ✓)
- [ ] Implement user choice handling [C/e/r/a] with keyboard shortcuts (Enter, Ctrl+C)
- [ ] Add system editor integration with auto-detection
- [ ] Implement `show` command with Rich formatting and syntax highlighting
- [ ] Implement `generate` command for individual step regeneration
- [ ] Add dependency regeneration when editing earlier steps
- [ ] Implement project state management and existing project handling
- [ ] Add YOLO mode (--yolo flag) for non-interactive generation
- [ ] Add time-to-value and cost tracking display

### ⏳ Stage 4: Advanced Features & Polish (PENDING)
**Duration:** 1-2 weeks
**Dependencies:** Stage 3 completion  

#### Sub-steps:
- [ ] Implement `export` command with meaningful file naming (gtm-report-acme-com-jan15.md)
- [ ] Implement `edit` command with dependency cascade handling
- [ ] Implement `list` command with project overview
- [ ] Add `status` command for quick project overview
- [ ] Add copy-paste friendly command output at completion
- [ ] Add comprehensive error handling with actionable next steps
- [ ] Implement API rate limit handling with retry logic
- [ ] Add CLI auto-completion support and consistent exit codes
- [ ] Create comprehensive help documentation with examples
- [ ] Add performance optimization and caching
- [ ] Implement thorough testing suite
- [ ] Create installation and deployment scripts

## Detailed Implementation Strategy

### Codebase Cleanup and Adaptation

**Files to Remove:**
- Remove all FastAPI/web server components (`app/api/`)
- Remove web-specific database models and routes
- Remove authentication and rate limiting for web users
- Remove development cache and web scraping components

**Files to Adapt:**
- Reuse `app/services/` (LLM services, content processing)
- Reuse `app/prompts/` (templates and prompt management)
- Reuse `app/schemas/` (Pydantic models, adapt for CLI context)
- Adapt `app/core/llm_singleton.py` for CLI environment

**New Files to Create:**
- `cli/` directory for all CLI-specific code
- `cli/main.py` - Main Typer app entry point
- `cli/commands/` - Individual command implementations
- `cli/utils/` - CLI utilities (formatting, file management)
- `cli/config.py` - Configuration management
- `setup.py` or `pyproject.toml` - Package installation

### File Storage Architecture

```
gtm_projects/
├── {domain}/
│   ├── overview.json      # Company analysis
│   ├── account.json       # Target account profile  
│   ├── persona.json       # Buyer persona
│   ├── email.json         # Email campaign
│   ├── plan.json          # GTM execution plan
│   ├── .metadata.json     # Generation metadata
│   └── export/
│       └── gtm-report-{date}.md
└── .gtm-cli-state.json    # Global state/preferences
```

### Error Handling Strategy

**Generation Failures:**
- Implement retry logic with exponential backoff
- Provide skip options for non-critical steps
- Allow manual editing to fix context issues
- Save partial progress to prevent data loss

**API Issues:**
- Rate limit detection and automatic retry
- API key validation and rotation support
- Graceful degradation with cached responses
- Clear error messaging with recovery options

### Data Flow Design

**Step Dependencies:**
1. Company Overview → Target Account
2. Company Overview + Target Account → Buyer Persona  
3. All Previous → Email Campaign
4. All Previous → GTM Plan

**Regeneration Logic:**
- When a step is regenerated, mark all dependent steps as stale
- Offer to regenerate dependent steps or continue with existing data
- Maintain data integrity across the dependency chain

## Resource Links

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/en/latest/)
- [Questionary Documentation](https://github.com/tmbo/questionary)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [OpenAI Python Client](https://platform.openai.com/docs/)
- [Click Documentation](https://click.palletsprojects.com/) (Typer's foundation)
- [Python Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [CLI Best Practices Guide](https://clig.dev/)

## Quality Assurance

### Testing Strategy
- Unit tests for each generation service
- Integration tests for complete workflows
- CLI functional tests using Typer's testing utilities
- Error scenario testing (API failures, invalid inputs)
- Performance testing for large projects

### Code Quality
- Type hints throughout (leveraging Typer's type system)
- Comprehensive docstrings and inline documentation
- Linting with flake8/black for consistent formatting
- Pre-commit hooks for code quality enforcement

### User Experience
- Comprehensive help text with practical examples
- Clear error messages with actionable next steps (→ Try: ..., → Or: ...)
- Intuitive command structure following CLI conventions
- Responsive feedback with micro-progress indicators
- Copy-paste friendly output for common next steps
- Smart defaults (domain normalization, editor detection)
- Time-to-value and cost feedback for technical founders
- Graceful handling of interruptions (Ctrl+C)
- Consistent exit codes (0=success, 1=user error, 2=system error)