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
- Optional hypothesis capture for target account and persona context
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

**Current Status:** ✅ Stage 3 Complete + Guided Email Feature Complete - Ready for Stage 4  
**Last Updated:** July 16, 2025

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

#### ✅ Stage 3: Interactive CLI Commands (COMPLETED)
**Duration:** Completed in 1 day
**Dependencies:** ✅ Stage 2 completion

#### Sub-steps:
- [x] Implement `init` command with full interactive flow
- [x] Add micro-progress indicators (→ Fetching website... ✓, → Processing with AI... ✓)
- [x] Implement user choice handling [C/e/r/a] with keyboard shortcuts (Enter, Ctrl+C)
- [x] Add system editor integration with auto-detection
- [x] Implement `show` command with Rich formatting and syntax highlighting
- [x] Implement `generate` command for individual step regeneration
- [x] Add dependency regeneration when editing earlier steps
- [x] Implement project state management and existing project handling
- [x] Add YOLO mode (--yolo flag) for non-interactive generation
- [ ] Add time-to-value and cost tracking display (deferred to Stage 4)

**Git Commits:**
- `c4958b3` added interactive email guide
- `d720c3b` fixed email_generation.jinja2 prompt bug
- `97b28ef` Implement guided email setup with 4-step interactive flow
- `52c6d3a` Improve existing project handling in init command

**What's Working in Stage 3:**
- ✅ Full interactive `init` command with 5-step flow
- ✅ Micro-progress indicators with Rich formatting and timing
- ✅ User choice handling [Continue/Edit/Regenerate/Abort] with Questionary
- ✅ System editor integration with auto-detection and fallbacks
- ✅ Rich-formatted `show` command with syntax highlighting and asset summaries
- ✅ Individual step regeneration via `generate` command with dependency checking
- ✅ Automatic dependency regeneration when editing earlier steps
- ✅ Project state management and existing project detection
- ✅ YOLO mode for non-interactive batch generation
- ✅ Comprehensive error handling with actionable recovery options
- ✅ Stale data detection and warnings

**🆕 Guided Email Feature (COMPLETED):**
- ✅ **4-Step Interactive Email Builder**: Use Case → Pain Point → Capability → Desired Outcome selection
- ✅ **Dynamic Content Extraction**: Pulls from target_persona.json use_cases and buying_signals arrays
- ✅ **Custom Instructions Support**: "Other" option with custom LLM instructions for steps 2 & 3
- ✅ **Template Integration**: Updated email_generation_blossomer.jinja2 to handle guided mode variables
- ✅ **Clean UI Formatting**: Simplified display text (content after colon for step 2, text before colon for step 3)
- ✅ **Hardcoded CTA Options**: Consistent call-to-action choices across sessions
- ✅ **Dynamic Array Handling**: Supports variable array sizes with proper numbering
- ✅ **Graceful Fallbacks**: Uses defaults when persona data is incomplete

**Testing:** All Stage 3 components tested and working. Run commands:
```bash
python3 -m cli.main --help              # CLI help and command overview
python3 -m cli.main init --help         # Interactive flow help
python3 -m cli.main show --help         # Asset display help  
python3 -m cli.main generate --help     # Individual generation help

# Example usage:
python3 -m cli.main init acme.com       # Start interactive GTM generation (includes guided email)
python3 -m cli.main show all            # Display all assets with formatting
python3 -m cli.main generate overview   # Regenerate specific step
python3 -m cli.main generate email      # Regenerate email with guided flow option
```

### ⏳ Stage 4: Advanced Features & Polish (READY TO START)
**Duration:** 1-2 weeks
**Dependencies:** ✅ Stage 3 completion + ✅ Guided Email Feature completion  

#### Sub-steps:
- [ ] **Implement hypothesis capture** - Optional context inputs for target account and persona
  - [ ] Add hypothesis capture prompts to init command before Step 1
  - [ ] Update target account and persona generation to use hypothesis context
  - [ ] Support --context flag for non-interactive hypothesis provision
  - [ ] Add hypothesis data to project metadata for regeneration
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

## 📄 JSON-to-Markdown Utility Project

### Overview
Create a utility system that converts GTM analysis JSON files to well-formatted Markdown for preview display and export functionality.

### Use Cases
1. **Preview Mode**: Generate truncated, clean markdown for showing content snippets in CLI commands
2. **Export Mode**: Generate complete, formatted markdown reports for external use

### Architecture Design

#### File Location
- **Primary File**: `cli/utils/markdown_formatter.py`
- **Integration Points**: `cli/commands/show.py` (preview), `cli/commands/export.py` (full export)

#### Class Structure
```python
# Base formatter with common functionality
class MarkdownFormatter:
    def format(self, data: dict, preview: bool = False, max_chars: int = 500) -> str
    
# Specialized formatters for each JSON schema
class OverviewFormatter(MarkdownFormatter)    # overview.json
class AccountFormatter(MarkdownFormatter)     # account.json  
class PersonaFormatter(MarkdownFormatter)     # persona.json
class EmailFormatter(MarkdownFormatter)       # email.json

# Factory function for easy instantiation
def get_formatter(step_type: str) -> MarkdownFormatter
```

### Implementation Tasks

#### Core Formatter Development
- [ ] **Create base MarkdownFormatter class** with common functionality
  - [ ] Character truncation logic for preview mode
  - [ ] Common markdown formatting utilities (headers, lists, tables)
  - [ ] Metadata section generation
  - [ ] Error handling for malformed data

- [ ] **Implement OverviewFormatter** for company analysis JSON
  - [ ] Company name and description (priority content)
  - [ ] Business insights and capabilities as lists
  - [ ] Use case analysis and positioning insights
  - [ ] Target customer insights and objections
  - [ ] Preview: Company name + description + top 3 insights

- [ ] **Implement AccountFormatter** for target account JSON
  - [ ] Account name and description header
  - [ ] Firmographics as formatted table
  - [ ] Buying signals as prioritized list with descriptions
  - [ ] Rationale as bullet points
  - [ ] Preview: Name + description + top 3 buying signals

- [ ] **Implement PersonaFormatter** for buyer persona JSON
  - [ ] Persona name and description header
  - [ ] Demographics table (job titles, departments, seniority)
  - [ ] Use cases with pain points and outcomes
  - [ ] Buying signals and objections as sections
  - [ ] Goals and purchase journey
  - [ ] Preview: Name + description + primary use case

- [ ] **Implement EmailFormatter** for email campaign JSON
  - [ ] Subject line variations as header
  - [ ] Email body with segment type annotations
  - [ ] Breakdown explanation for each segment type
  - [ ] Generation metadata and personalization info
  - [ ] Preview: Primary subject + first 2 email segments

#### Utility Functions
- [ ] **Create formatter factory function** for easy instantiation
  - [ ] Map step types to formatter classes
  - [ ] Handle unknown step types gracefully
  - [ ] Support future formatter additions

- [ ] **Implement preview mode logic**
  - [ ] Smart content prioritization (most valuable content first)
  - [ ] Character counting with word boundaries
  - [ ] Graceful truncation with ellipsis
  - [ ] Preserve markdown structure in truncated content

- [ ] **Implement full export mode**
  - [ ] Complete formatting with all sections
  - [ ] Rich markdown features (tables, code blocks, lists)
  - [ ] Consistent header hierarchy
  - [ ] Metadata appendix with generation details

#### Integration Points
- [ ] **Update show command** to use preview formatting
  - [ ] Import formatter utility
  - [ ] Replace current JSON display with markdown preview
  - [ ] Maintain Rich terminal formatting
  - [ ] Add character limit option

- [ ] **Create export command** for full markdown generation
  - [ ] New CLI command: `export <step|all> [--output file.md]`
  - [ ] Single step export vs. complete report
  - [ ] Meaningful filename generation (gtm-report-domain-date.md)
  - [ ] File overwrite confirmation prompts

#### Testing & Validation
- [ ] **Add unit tests** for all formatter classes
  - [ ] Test with real JSON data from gtm_projects
  - [ ] Test preview mode character limits
  - [ ] Test malformed data handling
  - [ ] Test markdown syntax validity

- [ ] **Integration testing**
  - [ ] Test show command preview integration
  - [ ] Test export command functionality
  - [ ] Test with various project states (complete, partial, stale)

### Technical Specifications

#### Markdown Structure Standards
```markdown
# {Company Name} - GTM Analysis

## Company Overview
- **Description**: {description}
- **URL**: {company_url}

### Key Insights
- {insight 1}
- {insight 2}

## Target Account Profile
**{target_account_name}**

{target_account_description}

### Firmographics
| Attribute | Value |
|-----------|-------|
| Industry | {industries} |
| Employees | {employee_range} |

### Buying Signals
1. **{signal_title}** ({priority})
   {signal_description}
   *Detection: {detection_method}*
```

#### Content Prioritization for Preview
1. **Overview**: Company name → description → top 3 business insights
2. **Account**: Target name → description → top 3 buying signals  
3. **Persona**: Persona name → description → primary use case
4. **Email**: Primary subject → intro → pain point segments

#### Character Limits
- **Short Preview**: 200 characters (for command summaries)
- **Medium Preview**: 500 characters (for step previews)
- **Long Preview**: 1000 characters (for detailed views)

### Dependencies
- **Existing**: Uses current JSON schemas and project structure
- **New**: No additional external dependencies required
- **Integration**: Enhances existing `show` command, enables new `export` command

### Success Criteria
1. ✅ All JSON types can be converted to readable markdown
2. ✅ Preview mode shows most important content within character limits
3. ✅ Export mode generates complete, well-formatted reports
4. ✅ Integration works seamlessly with existing CLI commands
5. ✅ Handles malformed data gracefully with clear error messages
6. ✅ Maintains performance for large JSON files

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