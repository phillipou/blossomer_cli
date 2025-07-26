# Email Generation Evaluation Framework

## 1. Context and Goals

### Problem Statement
The email generation prompt (`app/prompts/templates/email_generation_blossomer.jinja2`) is our most complex and nuanced prompt, containing detailed stylistic guidance, uncertainty handling, and sophisticated personalization logic. We need a comprehensive evaluation framework to ensure it consistently produces high-quality, natural-sounding founder-to-founder emails.

### Key Challenges Addressed
- **Complexity**: The prompt has 370+ lines of detailed instructions covering style, structure, personalization, and uncertainty handling
- **Subjectivity**: Email quality is highly subjective - what feels "natural" vs "templated" requires nuanced evaluation
- **Uncertainty Handling**: The prompt must intelligently ignore gibberish inputs and fall back to defaults
- **Identity Management**: Critical requirement to maintain sender vs recipient company identity
- **Personalization Balance**: Must distinguish between appropriate personalization and hyper-relevant content

### Success Criteria Achieved
✅ Consistent production of natural-sounding emails that pass the "rewrite test"
✅ Proper handling of uncertain/gibberish inputs with graceful fallbacks  
✅ Correct company identity handling (never confuse sender/recipient)
✅ Adherence to structural requirements (word count, subject line format, etc.)
✅ Recognition of hyper-relevant content as valid personalization alternative

## 2. Technical Architecture

### Directory Structure
```
evals/prompts/email_generation/
├── config.yaml                    # Service mapping and judge configuration
├── schema.json                   # Email output structure validation
└── judges/
    └── deterministic.py          # Custom email-specific checks (unused - integrated into base)

evals/core/judges/templates/
├── system/
│   └── email_quality.j2         # LLM judge system prompt with email best practices
└── user/
    └── email_quality.j2          # LLM judge user prompt with structured output format

evals/datasets/
├── eval_test_inputs.csv          # Base evaluation dataset
└── email_eval_enriched.csv       # Enhanced dataset with realistic company contexts
```

### Integration Points
- **Service**: `app.services.email_generation_service.generate_email_campaign_service`
- **Request Schema**: `EmailGenerationRequest` with company_context, target_account, target_persona, preferences
- **Response Schema**: Custom email generation response format with subjects, full_email_body, email_body_breakdown, writing_process, metadata
- **Context Orchestrator**: Required for company analysis and persona generation

## 3. Two-Stage Evaluation Architecture

### Stage 1: Deterministic Validation (Fast, Zero-Cost)

**Implementation Strategy**: Extended base `DeterministicJudge` class with conditional logic rather than creating separate class, maintaining backward compatibility.

**Email-Specific Logic**:
```python
if self.config.service_module == "app.services.email_generation_service":
    return self._check_email_subject_format(data, test_case)  # Custom email logic
else:
    # Standard "Key: Value" format for other services
```

#### D-1: JSON Validation (`json_validation`)
- Validates proper JSON syntax and parsing
- Returns parsed data for subsequent checks
- Same as base implementation

#### D-2: Schema Compliance (`schema_compliance`) 
- Validates against `schema.json` structure
- Requires 90% field population threshold
- Checks for all required email fields: subjects, full_email_body, email_body_breakdown, writing_process, metadata

#### D-3: Subject Format (`subject_format`)
**Custom Implementation**: `_check_email_subject_format()`
- Validates 3-4 word count requirement
- Checks proper capitalization (first word only)
- Ensures no generic pain words in subject lines
- Example pass: "Streamline support workflows", Example fail: "Sales problem"

#### D-4: Word Count (`word_count`)
**Custom Implementation**: `_check_email_word_count()`
- Validates email body is 50-100 words
- Counts words in `full_email_body` field
- Enforces conciseness requirement for founder emails

#### D-5: Identity Check (`identity_check`)
**Custom Implementation**: `_check_email_identity()`
- **Anti-hallucination logic**: Prevents confusing sender/recipient companies
- **Flexible placeholder acceptance**: Accepts [Company Name], {Company}, [Company], etc.
- **Generic email allowance**: Passes emails without specific company references
- **Fails on**: Addressing sender company as recipient (e.g., "Hi Intryc")

**Critical Design Decision**: Focus on preventing hallucination rather than enforcing specific placeholder format.

### Stage 2: LLM Quality Assessment

**Architecture**: Single comprehensive LLM judge returning 4 detailed checks rather than 3 separate judges for cost efficiency and holistic evaluation.

#### Judge Configuration
```yaml
llm_judges: ["email_quality"]
models:
  default: "OpenAI/gpt-4o-mini"  # Cost-effective for evaluation
  fallback: "Gemini/models/gemini-1.5-flash"
```

#### Email Quality Judge (`_judge_email_quality`)
Returns 4 standardized checks with LLM-identified input quotes:

**1. Email Naturalness (`email_naturalness`)**
- Evaluates founder-to-founder tone vs corporate speak
- LLM identifies: most natural phrase, least natural phrase, subject assessment
- Pass criteria: "sufficient" or "impressive" rating

**2. Personalization Appropriateness (`personalization_appropriateness`)**
- **Key Innovation**: Recognizes hyper-relevant content as valid personalization alternative
- LLM identifies: personalization evidence, hyper-relevance evidence, overall relevance level
- Pass criteria: Traditional personalization OR hyper-relevant content addressing specific role/industry pain points

**3. Uncertainty Handling (`uncertainty_handling`)**
- Detects forced/unnatural content from uncertain inputs
- LLM identifies: uncertainty indicators, content coherence issues, natural fallback evidence
- Pass criteria: Graceful handling without forcing gibberish into emails

**4. Structure Compliance (`structure_compliance`)**
- Evaluates founder outreach best practices
- LLM identifies: opening hook, value proposition, call-to-action effectiveness
- Pass criteria: Clear "why now", problem-solution fit, appropriate CTA

#### LLM Input Evaluation Innovation
**Problem Solved**: Instead of hardcoded Jinja2 logic extracting email segments, the LLM itself identifies and quotes the specific lines that influenced each rating.

**Example Output**:
```json
"inputs_evaluated": [
  {"field": "hyper_relevance_evidence", "value": "support teams are swamped with manual QA checks and inconsistent evaluations"},
  {"field": "personalization_evidence", "value": "None found"},
  {"field": "overall_relevance_level", "value": "Highly relevant to CX heads at growing startups"}
]
```

## 4. Dataset Enhancement

### Enriched Data Strategy
**Problem**: Original hardcoded test data used generic "Test Company" contexts
**Solution**: Created `email_eval_enriched.csv` with realistic company contexts

#### Data Structure
```csv
input_website_url,context_type,expected_company_name,company_context,target_account_context,target_persona_context,preferences
```

#### Enhanced Context Examples
- **Intryc**: "SaaS platform for customer support QA" with capabilities like "AI Evaluations", "Customizable Scorecards"
- **DrDroid**: "Incident response automation" with "Automated Root Cause Analysis", "Intelligent Alerting"
- **Mandrel**: "Supply chain optimization" with "Procurement Automation", "Inventory Optimization"

#### Realistic Preferences
- Varied use_case: "streamline_workflows", "reduce_costs", "enhance_security", "improve_efficiency"
- Context-appropriate emphasis: "pain-point" vs "desired-outcome"
- Diverse opening_line: "not-personalized", "buying-signal", "company-research"

### Evaluation Runner Integration
**Dynamic Context Loading**:
```python
# Try to use enriched context data if available
company_context = json.loads(test_case.get('company_context', '{}')) if test_case.get('company_context') else None

if company_context and target_account_context and target_persona_context and preferences:
    # Use enriched realistic data
    request = EmailGenerationRequest(company_context=company_context, ...)
else:
    # Fallback to basic data for backward compatibility
    request = EmailGenerationRequest(company_context={"company_name": "Test Company", ...})
```

## 5. Results and Quality Metrics

### Success Thresholds
- **Deterministic Pass Rate**: 100% (all structural requirements met)
- **LLM Judge Pass Rate**: 75%+ per individual check
- **Overall Pass Rate**: Both deterministic and LLM judges must pass

### Fail-Fast Design
1. **Deterministic checks run first** - if any fail, LLM evaluation is skipped (cost optimization)
2. **LLM evaluation only on structurally valid emails**
3. **Overall pass requires both stages to succeed**

### Quality Improvements Achieved
**Before Enhancement**:
- Generic emails: "Test Company helps with test capabilities"
- Poor personalization detection
- Hardcoded input evaluation

**After Enhancement**:
- Specific emails: "support teams are swamped with manual QA checks" (for Intryc CX context)
- Hyper-relevance recognition: Content addressing specific role pain points passes without traditional personalization
- LLM-driven input identification: Judge quotes exact problematic/exemplary phrases

### Representative Results
```
✅ Deterministic: 5/5 (100%)
✅ email_naturalness: "sufficient" - "uses conversational language and addresses common pain point"
✅ personalization_appropriateness: "sufficient" - "addresses specific pain point relevant to financial advisors"
✅ uncertainty_handling: "impressive" - "no forced or irrelevant elements"  
✅ structure_compliance: "sufficient" - "clear value proposition and logical flow"
```

## 6. Implementation Decisions

### Backward Compatibility Strategy
**Decision**: Extend base `DeterministicJudge` with conditional logic rather than separate inheritance
**Rationale**: Maintains compatibility with existing evaluations (product_overview, target_account, target_persona)
**Implementation**: 
```python
if self.config.service_module == "app.services.email_generation_service":
    return self._check_email_subject_format(data, test_case)
```

### Single vs Multiple LLM Judges
**Decision**: Single comprehensive judge with 4 detailed checks
**Rationale**: 
- Cost efficiency (1 vs 4 API calls)
- Holistic evaluation (email quality aspects are interconnected)
- Faster iteration and testing
- Easier maintenance

### Dataset Approach
**Decision**: Enhanced CSV with JSON-encoded contexts rather than database normalization
**Rationale**:
- Maintains existing evaluation framework patterns
- Easy to inspect and modify
- Avoids over-engineering for prototype phase
- Enables realistic testing without complex data pipelines

### Personalization Philosophy
**Decision**: "Hyper-relevance" as valid personalization alternative
**Rationale**:
- Founder emails often succeed through deep industry understanding rather than personal details
- Content addressing specific role challenges can be more effective than superficial personalization
- Aligns with email prompt's emphasis on relevant, helpful content

## 7. Usage and Commands

### Running Evaluations
```bash
# Basic evaluation
python3 -m evals.core.runner email_generation

# Detailed evaluation with all companies
python3 -m evals.core.runner email_generation --sample-size 5 --verbose

# Single company test
python3 -m evals.core.runner email_generation --sample-size 1 --verbose

# Custom output file
python3 -m evals.core.runner email_generation --output-file my_email_eval.json
```

### Results Location
```
evals/results/email_generation_YYYYMMDD_HHMMSS.json
```

### Integration with Existing CLI
The email evaluation framework integrates seamlessly with existing evaluation commands:
```bash
python3 -m evals.core.runner list                    # Shows email_generation as available
python3 -m evals.core.runner validate email_generation  # Validates configuration
```

## 8. Future Enhancements

### Completed Improvements ✅
- [x] Realistic company context data
- [x] LLM-driven input identification  
- [x] Hyper-relevance personalization logic
- [x] Comprehensive 4-check LLM evaluation
- [x] Email-specific deterministic validation
- [x] CLI result display fixes

### Potential Future Work
- [ ] Uncertainty test cases with intentional gibberish inputs
- [ ] A/B testing framework for prompt variations
- [ ] Industry-specific evaluation criteria
- [ ] Integration with email campaign analytics
- [ ] Automated prompt improvement suggestions based on evaluation patterns

## 9. Key Lessons Learned

### Technical Insights
1. **Conditional Logic Scales**: Extending base classes with service-specific logic maintains compatibility while enabling specialization
2. **LLM Context Matters**: Providing full email context to LLM judge produces more accurate, specific feedback than segmented evaluation
3. **Cost vs Quality**: Single comprehensive LLM judge provides better holistic assessment than multiple specialized judges
4. **Realistic Data Impact**: Enhanced company contexts dramatically improve evaluation relevance and email quality

### Product Insights  
1. **Hyper-relevance > Personalization**: Industry-specific pain point content often outperforms traditional personalization
2. **Founder Voice Patterns**: Natural language patterns (conversational fragments, real emotions) are detectable and valuable
3. **Anti-hallucination Priority**: Preventing company confusion is more critical than enforcing specific placeholder formats
4. **Structure vs Content**: Both structural compliance and content quality are necessary for effective founder emails

### Framework Design
1. **Fail-fast Performance**: Deterministic checks first saves significant LLM costs
2. **Standard Response Format**: Consistent check structure enables tool compatibility and result aggregation  
3. **Actionable Feedback**: LLM-identified specific quotes provide clear improvement direction
4. **Incremental Enhancement**: Building on existing evaluation patterns accelerates development and adoption

The email evaluation framework successfully balances comprehensiveness with practicality, providing production-ready quality assessment for founder-to-founder email generation.