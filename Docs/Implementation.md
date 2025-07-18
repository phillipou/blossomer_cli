# Implementation Plan for Blossomer GTM CLI Tool

## Current Architecture Overview

### Core CLI Features (✅ Implemented)
- **`init <domain>`** - Interactive 5-step GTM project generation
- **`show <asset>`** - Rich formatted asset display with syntax highlighting
- **`generate <step>`** - Individual step regeneration with dependency tracking
- **Hypothesis capture** - Optional context inputs for target account and persona
- **YOLO mode** - Non-interactive batch generation
- **System editor integration** - Auto-detected editor with fallbacks
- **Project state management** - Automatic dependency tracking and stale detection

### 5-Step Generation Flow (✅ Working)
1. **Company Overview** - Domain analysis and business insights extraction
2. **Target Account** - Ideal customer profile with firmographics
3. **Buyer Persona** - Detailed persona with demographics and use cases
4. **Email Campaign** - Personalized email with guided 4-step builder
5. **GTM Plan** - 30-day execution roadmap (schema needs completion)

### Technical Infrastructure (✅ Completed)
- **TensorBlock Forge Integration** - Unified LLM access across 19+ models
- **Rich Terminal UI** - Beautiful formatting with progress indicators
- **JSON File Storage** - Structured project data with metadata
- **Error Handling** - Actionable error messages with recovery options

## Key Technology Stack (✅ In Use)

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


## Current Implementation Status

**Status:** ✅ Core CLI Complete + Evaluation System Complete with Template-Driven Architecture - Focus on Remaining Features  
**Last Updated:** July 17, 2025

### ✅ Completed Core Features
- **Interactive CLI Commands** - Full 5-step GTM generation with rich UX
- **TensorBlock Forge Integration** - Unified LLM access with optimal model selection
- **Hypothesis Capture** - Optional context inputs for better personalization
- **Guided Email Builder** - 4-step interactive email generation
- **Project Management** - State tracking, dependency management, stale detection
- **System Editor Integration** - Auto-detected editor with fallback options
- **YOLO Mode** - Non-interactive batch generation for power users
- **✅ Evaluation System** - Complete prompt quality assurance with template-driven architecture and actual field value display

### 🎯 Current Working Commands
```bash
# Core GTM Generation
python3 -m cli.main init acme.com       # Start interactive GTM generation
python3 -m cli.main show all            # Display all assets with formatting
python3 -m cli.main generate overview   # Regenerate specific step
python3 -m cli.main generate email      # Regenerate email with guided flow

# Evaluation System
python3 -m cli.main eval list           # List available evaluations
python3 -m cli.main eval run product_overview --sample-size 5
python3 -m cli.main eval run target_account --sample-size 5
python3 -m cli.main eval run all        # Run all evaluations
```

### 🚧 Remaining Development Tasks

#### High Priority (Next Features)
- [ ] **Complete GTM Plan Generation** - Finish 5th step with proper schema/template
- [ ] **Implement `export` command** - Markdown report generation with meaningful naming
- [ ] **Implement `edit` command** - File editing with dependency cascade handling
- [ ] **Implement `list` command** - Project overview and management
- [ ] **Add `status` command** - Quick project health check

#### Medium Priority (Polish & UX)
- [ ] **Copy-paste friendly output** - Completion summaries with next steps
- [ ] **Enhanced error handling** - More actionable error messages
- [ ] **API rate limit handling** - Retry logic with exponential backoff
- [ ] **CLI auto-completion** - Shell completion support
- [ ] **Performance optimization** - Caching and response time improvements

#### Low Priority (Deployment)
- [ ] **Installation scripts** - Easy setup and deployment
- [ ] **Comprehensive help** - Enhanced documentation with examples
- [ ] **Testing suite expansion** - More comprehensive test coverage

## 🧪 Evaluation System for Prompt Quality

### Overview
Automated evaluation system to ensure prompt templates maintain consistent quality and handle edge cases appropriately. Built to mirror the app architecture exactly while providing efficient quality assurance.

### Architecture Design

#### Core Infrastructure (`evals/core/`)
- **Unified Runner**: Single command interface for all prompt evaluations
- **Reusable Judges**: Shared deterministic and LLM-based evaluation logic
- **Jinja2 Templates**: LLM judge prompts stored as easily editable .j2 files
- **Dataset Management**: Sampling and test case handling
- **Results System**: Parsing, rendering, and reporting

#### Prompt-Specific Evaluations (`evals/prompts/{prompt_name}/`)
- **Configuration**: YAML-based prompt-specific settings
- **Custom Judges**: Prompt-specific evaluation logic
- **Test Data**: CSV files with edge cases and context variations
- **Schema Validation**: Expected output format validation

### Evaluation Flow
1. **Sample test cases** from CSV dataset (configurable size)
2. **Generate outputs** using same services as CLI application
3. **Run deterministic checks** (JSON validation, schema compliance, format rules)
4. **Execute LLM judges** (traceability, actionability, redundancy, context steering)
5. **Aggregate results** and generate reports
6. **Parse and render** results in readable format

### Key Features

#### Mirror App Architecture
- **Same Services**: Uses identical generation services as CLI
- **Same Data Flow**: Input → Service → Output exactly matches app behavior
- **Same Error Handling**: Consistent error patterns and recovery
- **Same Configuration**: Uses TensorBlock Forge integration

#### Cost-Effective Design
- **Ultra-Cheap Models**: GPT-4.1-nano (~$0.000015 per judge call)
- **Deterministic First**: Fast checks eliminate expensive LLM calls on bad outputs
- **Batch Processing**: Efficient evaluation of multiple test cases
- **Configurable Sampling**: Test with small samples during development

#### Jinja2 Template System
```python
# Judge prompts are stored as .j2 files for easy editing
evals/core/judges/templates/
├── system/              # System prompt templates (instructions)
│   ├── traceability.j2      # Evidence-based claim verification
│   ├── actionability.j2     # Specificity and discovery value
│   ├── redundancy.j2        # Content overlap detection
│   └── context_steering.j2  # Context handling appropriateness
└── user/                # User prompt templates (data only)
    ├── traceability.j2      # Website content and claims
    ├── actionability.j2     # Analysis data to evaluate
    ├── redundancy.j2        # Description and insights sections
    └── context_steering.j2  # Context and analysis data
```

#### Evaluation Types

**Deterministic Checks (Zero Cost):**
- **D-1 Valid JSON**: Basic parsing validation
- **D-2 Schema Compliance**: Field presence and type validation
- **D-3 Format Compliance**: "Key: Value" pattern validation
- **D-4 Field Cardinality**: Array length validation (3-5 items)
- **D-5 URL Preservation**: Input/output URL matching

**LLM Judge Categories (Ultra-Low Cost):**
- **content_integrity**: Returns 3 individual checks - evidence_support, context_handling, content_distinctness
- **business_insight**: Returns 4 individual checks - industry_sophistication, strategic_depth, authentic_voice_capture, actionable_specificity
- **account_targeting_quality**: Returns 3 individual checks - proxy_strength, detection_feasibility, profile_crispness

#### Individual Check Output Structure

Each evaluation check (both deterministic and LLM) follows a standardized format:

```json
{
  "check_name": "evidence_support",
  "description": "Claims properly supported by evidence or marked as assumptions",
  "inputs_evaluated": [
    {"field": "analysis_claims", "value": "Sampled claims from analysis"}
  ],
  "pass": true,
  "rating": "impressive",
  "rationale": "Most claims are directly supported by the provided website content with clear references to capabilities and market positioning."
}
```

**Structure Requirements:**
- **check_name**: Unique identifier for the evaluation check
- **description**: Brief explanation of what the check evaluates (1-2 sentences)
- **inputs_evaluated**: Array of {field: field_name, value: field_value} pairs showing what data was examined
- **pass**: Boolean indicating if the check passed or failed
- **rating**: Optional qualitative assessment (poor|sufficient|impressive) for LLM checks
- **rationale**: Clear 2-3 sentence explanation of why it passed or failed

**LLM Judge Categories Return Multiple Individual Checks:**
- **content_integrity** → 3 checks: evidence_support, context_handling, content_distinctness
- **business_insight** → 4 checks: industry_sophistication, strategic_depth, authentic_voice_capture, actionable_specificity
- **account_targeting_quality** → 3 checks: proxy_strength, detection_feasibility, profile_crispness

**Example Deterministic Check:**
```json
{
  "check_name": "json_validation",
  "description": "Validates that the output is properly formatted JSON",
  "inputs_evaluated": [
    {"field": "raw_output", "value": "{ \"company_name\": \"Example Corp\", ... }"}
  ],
  "pass": true,
  "rationale": "The output is valid JSON with proper syntax. All required fields are present and correctly formatted."
}
```

**Example LLM Judge Check:**
```json
{
  "check_name": "industry_sophistication",
  "description": "Nuanced understanding of industry dynamics and competitive landscape",
  "inputs_evaluated": [
    {"field": "full_analysis", "value": "Complete analysis structure"}
  ],
  "pass": true,
  "rating": "impressive",
  "rationale": "The analysis demonstrates deep understanding of the customer support QA industry, including specific pain points like manual sampling limitations and AI integration challenges."
}
```

**Display Features:**
- **Rating Display**: Each LLM check shows color-coded rating (IMPRESSIVE/SUFFICIENT/POOR)
- **Rating Distribution Table**: Summary showing count and percentage of each rating level
- **Inputs Evaluated**: Shows actual field values being assessed (not summaries)
- **Cost Efficiency**: 3 LLM calls return 10 individual actionable checks
- **Granular Feedback**: Each criterion can be individually analyzed and improved

### Usage Examples

#### Basic Evaluation
```bash
# CLI integration (preferred method)
python3 -m cli.main eval run product_overview --sample-size 3
python3 -m cli.main eval run target_account --sample-size 3
python3 -m cli.main eval run all --sample-size 5

# Direct runner access (for development)
python3 -m evals.core.runner product_overview --sample-size 3
python3 -m evals.core.runner target_account --sample-size 3
python3 -m evals.core.runner all --sample-size 5
```

#### Adding New Prompt Evaluation
```bash
# Use the CLI to create a new evaluation
python3 -m cli.main eval create new_prompt \
  --service-module "app.services.new_service" \
  --service-function "new_service_function" \
  --create-sample-data

# Or manually:
# 1. Create directory: evals/prompts/new_prompt/
# 2. Add configuration: config.yaml
# 3. Define test cases: data.csv
# 4. Create output schema: schema.json
# 5. Run: python3 -m cli.main eval run new_prompt
```

### Quality Criteria

#### "Good" Output Definition
- **Traceable**: Claims backed by website evidence or marked assumptions
- **Actionable**: Insights lead to specific discovery questions
- **Structured**: Follows exact JSON schema and formatting rules
- **Comprehensive**: Covers all required business analysis areas
- **Context-Aware**: Appropriately incorporates or ignores user context

#### Success Metrics
- **Deterministic Pass Rate**: >95% on valid inputs
- **LLM Judge Pass Rate**: >90% on quality criteria
- **Context Steering**: 100% appropriate handling of noise vs valid context
- **Cost Efficiency**: <$0.10 per full evaluation run
- **Execution Time**: <5 minutes for full evaluation

### Implementation Benefits

#### For Development
- **Rapid Iteration**: Test prompt changes quickly with sample datasets
- **Edge Case Detection**: Systematic testing of failure modes
- **Regression Prevention**: Catch quality degradation early
- **Usage Tracking**: Monitor evaluation usage across model changes

#### For Production
- **Quality Assurance**: Consistent output quality across different inputs
- **Model Comparison**: A/B test different LLM providers easily
- **Performance Monitoring**: Track quality metrics over time
- **Documentation**: Clear evaluation criteria and expected behaviors

### Future Extensions

#### Additional Prompts
- **✅ Target Account Evaluation**: Profile definition crispness, detection quality, actionable prospect filters
- **✅ Target Persona Evaluation**: Demographics precision, use case alignment, buying signal relevance
- **Email Generation Evaluation**: Subject line effectiveness, personalization quality
- **GTM Plan Evaluation**: Actionability, timeline feasibility, metric relevance

#### Advanced Features
- **Comparative Analysis**: Compare outputs across different model versions
- **Trend Analysis**: Track quality metrics over time
- **Automated Alerts**: Notify on quality degradation
- **Human Validation**: Integrate human feedback into evaluation pipeline

### Technical Implementation

#### Dependencies
- **TensorBlock Forge**: Unified LLM access (already integrated)
- **Existing Services**: Reuse all current generation services
- **Jinja2**: Template rendering (already used in app)
- **pandas**: Dataset handling
- **Rich**: Terminal output formatting

#### Configuration Management
```yaml
# evals/prompts/product_overview/config.yaml
name: "Product Overview Evaluation"
service: "app.services.product_overview_service"
schema: "schema.json"
judges:
  deterministic: ["D-1", "D-2", "D-3", "D-4", "D-5"]
  llm: ["content_integrity", "business_insight"]
models:
  default: "OpenAI/gpt-4.1-nano"
  fallback: "Gemini/models/gemini-1.5-flash"
```

This evaluation system ensures prompt quality while remaining practical, efficient, and closely aligned with the actual application architecture.

## 🎯 Target Account Profile Evaluation Design

### Overview
Target account evaluation assesses the quality of ideal customer profile (ICP) generation using two core dimensions: **Profile Definition Crispness** and **Detection Quality**. This evaluation ensures target account profiles are specific enough to be actionable while remaining technically feasible to implement.

### Quality Framework

#### **Dimension 1: Profile Definition Crispness** 
*"How precisely have you defined your ideal customer?"*

**Core Metric**: **Exclusion Rate** - How many companies in the broad category are you excluding?
- **Excellent**: "Series B SaaS companies with 50-200 employees using Kubernetes in production" (high exclusion rate)
- **Poor**: "Growing tech companies that need better tools" (excludes almost no one)

**Evaluation Criteria**:
- **Specificity**: Are firmographics specific enough to filter effectively? (e.g., "100-500 employees" vs "mid-size companies")
- **Logical Alignment**: Does the profile logically connect to the problem being solved?
- **Clay Readiness**: Can all firmographic filters be copy-pasted into prospecting tools?
- **Keyword Sophistication**: Do keywords indicate implicit need vs. explicit solution seeking?

#### **Dimension 2: Detection Quality**
*"Can you actually find these companies and identify when they need you?"*

**Sub-Components**:

1. **Proxy Strength**: Are your attributes/signals good predictors of need?
   - Do firmographics correlate with having the problem?
   - Do buying signals indicate "need now" vs. "might need someday"?
   - Is the priority distribution realistic (~10% high, ~65% medium, ~25% low)?

2. **Technical Feasibility**: Can you detect these with available tools?
   - Traditional tools: Clay, Apollo, ZoomInfo for firmographics
   - AI-enhanced capabilities: MCP servers, web scraping, deep research for advanced signals
   - Detection methods clearly specified for each signal

**The Quality Flow**:
```
Problem Definition → Profile Crispness → Attribute Quality → Detection Feasibility → Rationale Clarity
     ↓                    ↓                  ↓                    ↓                    ↓
"What problem    "What specific     "What do they      "Can we find       "Can someone
do we solve?"    companies have     look like &        these signals      follow our 
                 this problem?"     when do they       with existing      logic?"
                                   need it?"          tools?"
```

### Evaluation Structure

#### **Deterministic Checks (Target Account Specific)**
- **D-1 Valid JSON**: Basic parsing validation
- **D-2 Schema Compliance**: Field presence and type validation  
- **D-3 Priority Distribution**: Buying signals follow ~10%/65%/25% high/medium/low distribution
- **D-4 Field Cardinality**: Rationale arrays contain 3-5 items, keywords contain 3-5 items
- **D-5 Detection Specification**: Every buying signal specifies detection method and type
- **D-6 Clay Compatibility**: Firmographic values use exact, searchable terminology

#### **LLM Judge Categories**
- **content_integrity**: Evidence support, context handling, content distinctness
- **account_targeting_quality**: Profile crispness, detection feasibility, business logic depth

### Success Metrics
- **Profile Specificity**: >80% of outputs demonstrate high exclusion rate
- **Detection Feasibility**: >90% of buying signals specify realistic detection methods
- **Priority Distribution**: >95% compliance with 10/65/25 priority allocation
- **Clay Readiness**: >95% of firmographics use exact, searchable values
- **Business Logic**: >85% demonstrate sophisticated understanding of customer dynamics

### End Goal
Generate a **usable roadmap** that tells sales teams: "Look for companies that look like X, behave like Y, at moments when Z happens, using tools A/B/C"

### Implementation Files
```
evals/prompts/target_account/
├── config.yaml              # Service mapping and judge configuration
├── schema.json              # TargetAccountResponse validation schema
└── ../datasets/eval_test_inputs.csv  # Shared test dataset
```

### Judge Template Structure
```
evals/core/judges/templates/
├── system/
│   ├── content_integrity.j2        # Existing general content validation
│   └── account_targeting_quality.j2# New: Profile crispness + detection quality
└── user/
    ├── content_integrity.j2        # Data input for content validation
    └── account_targeting_quality.j2# Data input for targeting assessment
```

### ✅ Implementation Complete (July 17, 2025)
1. **✅ Refactored existing evaluation code** - Clean up current spaghetti code
2. **✅ Created unified evaluation runner** - Single command interface
3. **✅ Jinja2 judge templates** - Easy prompt editing with system/user separation
4. **✅ Added support for multiple prompts** - Extensible architecture
5. **✅ Integrated with main CLI workflow** - Continuous quality assurance
6. **✅ Template refactoring** - Separated system instructions from user data for cleaner organization

## 🎯 Target Persona Profile Evaluation Design

### Overview
Target persona evaluation assesses the quality of individual buyer persona generation using the same proven framework as target accounts: **Persona Definition Crispness**, **Individual Proxy Strength**, and **Individual Detection Feasibility**. This evaluation ensures persona profiles are specific enough for individual targeting while capturing realistic personal behaviors and engagement patterns.

### Quality Framework

Target persona evaluation adapts the proven account evaluation framework (**Proxy Strength**, **Definition Crispness**, **Detection Feasibility**) for individual buyer targeting.

#### **Dimension 1: Persona Definition Crispness** 
*"How precisely have you defined your ideal individual buyer?"*

**Core Metric**: **Individual Exclusion Rate** - How many people in the broad role category are you excluding?
- **Excellent**: "VP of Engineering at 100-500 employee SaaS companies with Kubernetes experience and recent DevOps tool adoption" (high exclusion rate, LinkedIn searchable)
- **Poor**: "Tech leaders who care about efficiency" (excludes almost no one, too vague for targeting)

**Evaluation Criteria**:
- **Job Title Specificity**: Titles specific enough for LinkedIn/CRM searches (e.g., "VP of Engineering" vs "tech executive")
- **Department Precision**: Departments align with solution's value proposition and persona's actual responsibilities
- **Seniority Logic**: Seniority matches realistic buying authority and budget influence for this type of purchase
- **Keyword Sophistication**: Job description keywords reflect day-to-day activities, not product relationships
- **LinkedIn Readiness**: All demographic criteria can be copy-pasted into LinkedIn searches

#### **Dimension 2: Individual Proxy Strength**
*"Are your persona attributes/signals good predictors of individual need and engagement?"*

**Sub-Components**:

1. **Workflow-Problem Fit**: Do use cases connect to this persona's actual daily/critical workflows?
   - **Workflow Specificity**: Daily/weekly processes (e.g., "manually entering CRM data") or critical tasks (e.g., "ensuring no financial details missed ahead of IPO")
   - **Feature Mapping**: Desired outcomes connect directly to product capabilities, not lazy business outcomes
   - **Pain-Solution Logic**: Clear use_case → pain_point → capability → desired_outcome progression

2. **Signal-Strategy Fit**: Do buying signals answer the three critical strategy questions?
   - **Strategy Question 1**: "What signals indicate someone is actively trying to solve this problem right now?"
   - **Strategy Question 2**: "What signals indicate someone will respond well to cold outreach?" (intimately familiar with problem)
   - **Strategy Question 3**: "What signals indicate someone can rally others internally?"
   - **Personal Investment**: Signals show individual engagement with problem domain, not just job responsibilities

3. **Priority Distribution Realism**: Is the signal priority realistic (~15% high, ~60% medium, ~25% low)?

#### **Dimension 3: Individual Detection Feasibility**
*"Can you actually find and engage these individuals?"*

**Sub-Components**:

1. **Individual Targeting Tools**: Can you detect these personas with available tools?
   - **LinkedIn/CRM Compatibility**: Job titles, departments, seniority searchable in LinkedIn Sales Navigator, CRM systems
   - **Enrichment Tools**: Buying signals detectable via Clay, Apollo, ZoomInfo, or professional databases
   - **AI-Enhanced Capabilities**: Advanced signals identifiable through MCP servers, content analysis, social listening

2. **Outreach Feasibility**: Can you actually engage these individuals effectively?
   - **Contact Methods**: Signals indicate preferred communication channels and engagement patterns
   - **Receptivity Indicators**: Signals suggest likelihood of responding to cold outreach
   - **Detection Methods**: Every buying signal specifies exact detection method and data source

**The Persona Quality Flow**:
```
Problem Definition → Persona Crispness → Workflow-Signal Quality → Detection Feasibility → Engagement Strategy
     ↓                    ↓                     ↓                      ↓                     ↓
"What problem    "What specific        "What workflows &      "Can we find         "Can we engage
do we solve?"    people have this      signals indicate       these individuals    these people
                 problem?"             need & receptivity?"   with existing        effectively?"
                                                             tools?"
```

### Evaluation Structure

#### **Deterministic Checks (Persona Specific)**
- **D-1 Valid JSON**: Basic parsing validation
- **D-2 Schema Compliance**: Field presence and type validation (BuyerPersonaResponse schema)
- **D-3 Priority Distribution**: Buying signals follow ~15%/60%/25% high/medium/low distribution
- **D-4 Field Cardinality**: Rationale arrays contain 3-5 items, use cases contain 3-4 items
- **D-5 Detection Specification**: Every buying signal specifies detection method and data source

Note: LinkedIn compatibility and use case logic are assessed qualitatively in the `persona_targeting_quality` LLM judge.

#### **LLM Judge Categories**
- **content_integrity**: Evidence support, context handling, content distinctness (shared)
- **persona_targeting_quality**: Demographics precision, use case relevance, individual signal quality (persona-specific)

### Persona-Specific Quality Criteria

#### **Persona Definition Crispness Assessment**
- **Individual Exclusion Rate**: Criteria exclude significant portion of people in broad role category
- **LinkedIn Searchability**: Job titles, departments, seniority directly searchable in LinkedIn Sales Navigator
- **Demographic Precision**: Specific enough for CRM filtering and enrichment tool targeting
- **Keyword Sophistication**: Job description keywords reflect actual daily activities, not product relationships
- **Buying Authority Logic**: Seniority and role align with realistic purchasing influence for this solution type

#### **Individual Proxy Strength Assessment**  
- **Workflow-Problem Connection**: Use cases map to persona's actual daily/critical workflows (not business outcomes)
- **Feature-Outcome Mapping**: Desired outcomes connect directly to specific product capabilities (avoid "increase revenue")
- **Signal-Strategy Alignment**: Buying signals answer the three core strategy questions about urgency, receptivity, and influence
- **Process Depth**: Pain points dig 3-4 levels from high-level goals to specific workflow inefficiencies
- **Personal Investment Indicators**: Signals show individual engagement with problem domain beyond job requirements

#### **Individual Detection Feasibility Assessment**
- **Tool Compatibility**: Demographics and signals detectable through LinkedIn, Clay, Apollo, ZoomInfo, professional databases
- **Detection Method Specificity**: Every buying signal specifies exact detection method and data source
- **Outreach Viability**: Signals indicate realistic methods for initiating contact and engagement
- **Enrichment Readiness**: Persona criteria compatible with existing prospecting and enrichment workflows
- **Scalability**: Detection methods work for both individual targeting and list building at scale

### Success Metrics
- **Persona Definition Crispness**: >85% demonstrate high individual exclusion rate with LinkedIn-searchable criteria
- **Workflow-Problem Fit**: >90% of use cases map to specific daily/critical workflows (not business outcomes)
- **Anti-Lazy Outcomes**: >95% of desired outcomes specify feature-mapped improvements (avoid "increase revenue")
- **Signal-Strategy Fit**: >80% of buying signals answer at least 2 of the 3 core strategy questions
- **Priority Distribution**: >95% compliance with 15/60/25 priority allocation for buying signals
- **Individual Detection Feasibility**: >90% of signals specify realistic detection methods for person-level targeting
- **LinkedIn Readiness**: >95% of demographic criteria are copy-paste ready for LinkedIn Sales Navigator

### End Goal
Generate **actionable persona profiles** that enable sales teams to: "Target individuals with job titles X, in departments Y, showing personal signals Z, using detection methods A/B/C"

### Implementation Files
```
evals/prompts/target_persona/
├── config.yaml              # Service mapping and judge configuration
├── schema.json              # BuyerPersonaResponse validation schema
└── ../datasets/eval_test_inputs.csv  # Shared test dataset with persona test cases
```

### Judge Template Structure
```
evals/core/judges/templates/
├── system/
│   ├── content_integrity.j2           # Existing general content validation
│   └── persona_targeting_quality.j2   # New: Demographics precision + individual signal quality
└── user/
    ├── content_integrity.j2           # Data input for content validation  
    └── persona_targeting_quality.j2   # Data input for persona assessment
```

### Usage Examples
```bash
# Run persona evaluation
python3 -m cli.main eval run target_persona --sample-size 5

# Include persona in full evaluation suite
python3 -m cli.main eval run all --sample-size 3

# Validate persona configuration
python3 -m cli.main eval validate target_persona
```

### Quality Assurance Focus Areas

#### **Demographics vs. Firmographics**
- **Personas**: Job titles, departments, seniority, individual responsibilities
- **Accounts**: Company size, industry, revenue, organizational structure
- **Key Difference**: Individual targeting criteria vs. company-level characteristics

#### **Individual vs. Company Buying Signals**
- **Persona Signals**: LinkedIn activity, profile changes, personal content engagement, career development
- **Account Signals**: Company announcements, funding rounds, technology adoption, organizational changes
- **Key Difference**: Personal intent indicators vs. organizational buying triggers

#### **Personal vs. Organizational Outcomes**
- **Persona Outcomes**: Individual KPIs, role success metrics, career advancement goals
- **Account Outcomes**: Company performance, organizational efficiency, business transformation
- **Key Difference**: What matters to this person vs. what matters to the company

### 🎯 Current Evaluation Commands
```bash
# List available evaluations
python3 -m cli.main eval list

# Validate a prompt configuration
python3 -m cli.main eval validate product_overview

# Run single evaluation
python3 -m cli.main eval run product_overview --sample-size 5
python3 -m cli.main eval run target_account --sample-size 5
python3 -m cli.main eval run target_persona --sample-size 5

# Run all evaluations
python3 -m cli.main eval run all --sample-size 3

# Create new evaluation
python3 -m cli.main eval create my_prompt \
  --service-module "app.services.my_service" \
  --service-function "my_service_function" \
  --create-sample-data
```

### 📊 Evaluation System Architecture (✅ Complete & Cleaned)
- **Core Framework** (`evals/core/`): Config, dataset, results, judges
- **CLI Integration** (`cli/commands/eval.py`): User-friendly command interface
- **Prompt Configs** (`evals/prompts/`): Per-prompt configurations and datasets
- **Rich Output**: Progress bars, detailed results, usage tracking
- **Extensible Design**: Easy to add new prompt evaluations

### 🧹 Cleanup Completed (July 17, 2025)
**Legacy Code Removed:**
- `evals/product_overview/` - Old promptfoo-based evaluation system (~15 files)
- `evals/common/` - Old environment setup utilities
- `Docs/evals/implementation.md` - Obsolete promptfoo documentation
- `Docs/evals/product_overview_eval_spec.md` - Old evaluation specification

**Archived for Reference:**
- Old evaluation results → `archive/old_evals/results/`
- Legacy documentation → `archive/old_evals/`
- Utility functions → `archive/old_evals/common/`

**Final Clean Structure:**
```
evals/
├── core/                    # ✅ Unified evaluation framework
│   ├── config.py           # YAML configuration management
│   ├── dataset.py          # CSV test case loading
│   ├── results.py          # Rich terminal output with actual field values
│   ├── runner.py           # Single command interface
│   └── judges/             # Evaluation logic
│       ├── deterministic.py    # Zero-cost validation checks
│       ├── llm_judge.py        # LLM-based evaluation with template-driven architecture
│       └── templates/          # Jinja2 templates for LLM judge categories
│           ├── system/         # System prompt templates (instructions & formats)
│           │   ├── content_integrity.j2
│           │   ├── business_insight.j2
│           │   └── account_targeting_quality.j2
│           └── user/           # User prompt templates (data + JSON format)
│               ├── content_integrity.j2
│               ├── business_insight.j2
│               └── account_targeting_quality.j2
├── prompts/                # ✅ Per-prompt configurations
│   ├── product_overview/   # Product overview evaluation
│   ├── target_account/     # Target account profile evaluation
│   └── target_persona/     # Target persona profile evaluation
└── datasets/               # ✅ Centralized test data
    └── eval_test_inputs.csv    # Shared test cases across evaluations
```

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

## Key Implementation Patterns

### Project Storage Structure (✅ Implemented)
```
gtm_projects/
├── {domain}/
│   ├── json_output/       # All JSON files stored here
│   │   ├── overview.json      # Company analysis
│   │   ├── account.json       # Target account profile  
│   │   ├── persona.json       # Buyer persona
│   │   ├── email.json         # Email campaign
│   │   └── plan.json          # GTM execution plan
│   ├── .metadata.json     # Generation metadata
│   └── export/
│       └── gtm-report-{date}.md
└── .gtm-cli-state.json    # Global state/preferences
```

### Data Flow & Dependencies (✅ Working)
1. **Company Overview** → Target Account
2. **Company Overview + Target Account** → Buyer Persona  
3. **All Previous Steps** → Email Campaign
4. **All Previous Steps** → GTM Plan

### Error Handling Philosophy (✅ Implemented)
- **Fail fast with clear messages** - Technical founders need actionable feedback
- **Graceful degradation** - Always offer next steps (→ Try: ..., → Or: ...)
- **No silent failures** - Every error guides the user to success
- **Save partial progress** - Prevent data loss on failures

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

### User Experience Principles
- **Fail fast with clear messages** - Technical founders need actionable feedback
- **Graceful degradation** - Always offer next steps (→ Try: ..., → Or: ...)
- **No silent failures** - Every error should guide the user to success
- **Ship working software** - Perfect is the enemy of good
- **Technical founders appreciate directness** - Clear, honest feedback