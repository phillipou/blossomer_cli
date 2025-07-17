# Product Overview Prompt Evaluation Spec

## Overview

This document defines the evaluation harness for `app/prompts/templates/product_overview.jinja2` using Promptfoo. The goal is to ensure the prompt performs consistently and meets quality standards for discovery call preparation.

## Context

- **Target Template**: `app/prompts/templates/product_overview.jinja2`
- **Purpose**: Generate structured discovery call preparation material from company websites
- **Output Format**: JSON with company analysis, capabilities, use cases, positioning, and objections
- **Key Challenge**: Consistent quality across diverse website content and context conditions

## Evaluation Strategy

### 1. Minimal Dataset (21 Test Cases)

#### Core Dataset (5 SaaS Sites)
Well-written SaaS company sites across different verticals (examples):
- **Stripe** (fintech/payments) - stripe.com
- **Notion** (productivity) - notion.so  
- **Figma** (design tools) - figma.com
- **Datadog** (monitoring) - datadoghq.com
- **Slack** (communications) - slack.com

*Rationale: Covers normal path with quality content and clear value propositions*

#### Edge Cases (2 Weak Landing Pages)
Sites with minimal/poor content to test `[MISSING]` logic:
- **Instalbel** (AI data-labelin startup) - instalabel.ai/
- **Early-stage startup** with basic landing page
- **Legacy B2B site** with limited product details
Examples
- **Instalabel** (AI data-labeling) - instalabel.ai
- **Vulcan** (AI legal) - vulcan-tech.com

*Rationale: Forces proper handling of insufficient data*

#### Context Steering (3 Variants per URL)
Each URL tested with 3 context types:
- **None**: No `user_inputted_context` provided
- **Valid**: Relevant additional context about company/product
- **Noise**: Gibberish or irrelevant context

*Total: 7 URLs × 3 context types = 21 test cases*

### 2. Deterministic Checks (Zero LLM Cost)

Run in order, abort if any fail:

#### D-1: Valid JSON
- **Guards**: Basic parsing ability
- **Rule**: `json.loads()` succeeds
- **Implementation**: Python JSON parsing

#### D-2: Schema Compliance
- **Guards**: Required fields present, correct types
- **Rule**: `jsonschema.validate()` passes + ≥90% top-level fields non-empty
- **Implementation**: JSON Schema validation against product_overview schema

#### D-3: Format Compliance
- **Guards**: Product-specific format requirements
- **Rule**: All `*_insights` fields follow "Key: Value" format
- **Implementation**: Regex check for colon separator in insight strings

#### D-4: Field Cardinality
- **Guards**: Appropriate content volume
- **Rule**: 3-5 items in `capabilities` and `objections` arrays
- **Implementation**: Length validation

### 3. LLM-as-Judge Checks

Each judge returns:
```json
{
  "pass": true|false,
  "details": [
    {
      "check_id": "L-1",
      "reason": "Brief explanation of result",
      "pass_rule": "Criteria that was evaluated"
    }
  ]
}
```

#### L-1: Traceability
- **Clause**: Evidence-based claims
- **Rule**: 5 randomly sampled factual statements from `business_profile_insights`, `use_case_analysis_insights`, `positioning_insights` either cite website content or carry `[ASSUMPTION]` tag. Majority (≥3) must comply.
- **Scope**: Judge sees website content + sampled statements

#### L-2: Actionability
- **Clauses**: 
  - **Specificity**: Insights are specific to this company, not generic
  - **Discovery Value**: Each insight suggests clear follow-up questions
  - **Evidence-Based**: Claims supported by website content
- **Rule**: All three clauses must hold
- **Scope**: Judge sees full JSON output

#### L-3: Content Redundancy
- **Clause**: Avoid duplication across sections
- **Rule**: No significant overlap between `description` and `business_profile_insights` content (Jaccard similarity < 0.30)
- **Scope**: Judge sees both sections only

#### L-4: Context Steering
- **Clause**: Appropriate context usage
- **Rule**: Based on `context_type`:
  - **valid** → At least one insight incorporates user-provided context
  - **noise** → Insights ignore gibberish, focus on website content  
  - **none** → Auto-pass (baseline behavior)
- **Scope**: Judge sees `user_inputted_context`, `context_type`, and output JSON

All L-checks must return `"pass": true` for overall success.

## Quality Criteria

### "Good" Output Definition
- **Traceable**: Claims backed by website evidence or marked assumptions
- **Actionable**: Insights lead to specific discovery questions
- **Structured**: Follows exact JSON schema and formatting rules
- **Comprehensive**: Covers business model, capabilities, positioning, objections
- **Context-Aware**: Appropriately incorporates or ignores user context

### Failure Cases
- **Invalid JSON**: Parsing errors, malformed structure
- **Missing Fields**: Required schema elements absent
- **Format Violations**: Insights don't follow "Key: Value" pattern
- **Unsupported Claims**: Statements not traceable to source material
- **Generic Content**: Insights that could apply to any company
- **Context Contamination**: Noise context influencing analysis

## Implementation Notes

### Promptfoo Configuration
```yaml
prompts:
  - file://app/prompts/templates/product_overview.jinja2

providers:
  - anthropic:claude-3-5-sonnet-20241022

tests:
  - vars:
      input_website_url: "https://stripe.com"
      context_type: "none"
    assert:
      - type: python
        value: file://evals/deterministic_checks.py
      - type: llm-rubric
        value: file://evals/llm_judges.py

datasets:
  - file://evals/test_cases.csv
```

### Test Data Structure
```csv
input_website_url,context_type,user_inputted_context,website_content
https://stripe.com,none,"",<scraped_content>
https://stripe.com,valid,"Payment processing for online marketplaces",<scraped_content>
https://stripe.com,noise,"Purple elephants dancing in the moonlight",<scraped_content>
```

### Judge Implementation
- Use fast, cost-effective model (gpt-4.1-nano Haiku)
- Batch judge calls when possible
- Clear pass/fail criteria with explanations
- Standardized response format

## Success Metrics

- **Deterministic Pass Rate**: >95% on valid inputs
- **LLM Judge Pass Rate**: >90% on quality criteria
- **Context Steering**: 100% appropriate handling of noise vs valid context
- **Cost Efficiency**: <$5 per full evaluation run

## Maintenance

- **Dataset Updates**: Add new test cases as edge cases are discovered
- **Judge Calibration**: Periodically review judge consistency
- **Schema Evolution**: Update checks when prompt template changes
- **Performance Monitoring**: Track evaluation runtime and cost trends

This evaluation framework provides a foundation for maintaining prompt quality while remaining practical and cost-effective.