# Evaluation Judge System

## Overview
The evaluation system uses both deterministic and LLM-based judges to assess the quality of generated company analyses. All judges follow a standardized output format for consistency.

## Standardized Output Format

All evaluation checks (both deterministic and LLM) return results in this JSON structure:

```json
{
  "check_name": "string - identifier for the check",
  "description": "string - what this check evaluates", 
  "inputs_evaluated": [
    {"field": "string", "value": "any - the input that was evaluated"}
  ],
  "pass": true/false,
  "rationale": "2-3 sentence explanation of why the check passed or failed",
  "rating": "poor|sufficient|impressive"  // Optional field for LLM quality assessments
}
```

### Additional Fields by Judge Type

**Deterministic Judges** may include:
- `data`: Parsed JSON data (for json_validation check)

**LLM Sub-Criterion Checks** include:
- `rating`: Qualitative assessment (poor|sufficient|impressive)

**Any Judge** may include:
- `error`: Error message if judge execution failed

### LLM Judge Structure

LLM judges now return individual checks for each sub-criterion rather than aggregate results. This makes results more actionable and follows the same pattern as deterministic checks.

**Example**: The `general_quality` judge returns 3 individual checks:
- `evidence_support`
- `context_handling` 
- `content_distinctness`

**Example**: The `founder_resonance` judge returns 4 individual checks:
- `industry_sophistication`
- `strategic_depth`
- `authentic_voice_capture`
- `actionable_specificity`

## Available Judges

### Deterministic Judges (DeterministicJudge)
Fast, zero-cost validation checks that run first:

- **D-1 json_validation**: Validates output is properly formatted JSON
- **D-2 schema_compliance**: Validates output matches expected schema and ≥90% fields populated
- **D-3 format_compliance**: Validates insight fields follow 'Key: Value' format
- **D-4 field_cardinality**: Validates array fields contain expected number of items
- **D-5 url_preservation**: Validates input URL is preserved in output

### LLM Judge Categories (LLMJudge)
Sophisticated evaluation using language models. Each category returns multiple individual checks:

- **general_quality**: Returns 3 checks for evidence support, context handling, and content distinctness (prompt-agnostic)
- **founder_resonance**: Returns 4 checks for sophisticated understanding that would impress founders (product_overview specific)

## LLM Judge Category Details

### General Quality Judge Category
Evaluates three prompt-agnostic criteria in a single LLM call, returning 3 individual checks:

**Individual Checks Returned:**
1. **evidence_support**: Claims properly supported by evidence or marked as assumptions
2. **context_handling**: Appropriate incorporation/ignoring of user context based on type
3. **content_distinctness**: Sections provide unique value without excessive duplication

**Overall Pass Criteria**: All three checks must pass (rating "sufficient" or higher)

### Founder Resonance Judge Category
Evaluates four product-overview specific criteria in a single LLM call, returning 4 individual checks:

**Individual Checks Returned:**
1. **industry_sophistication**: Nuanced understanding of industry dynamics and competitive landscape
2. **strategic_depth**: Non-obvious strategic implications and opportunities
3. **authentic_voice_capture**: Company's unique positioning vs generic business-speak
4. **actionable_specificity**: Insights specific to company that lead to valuable discovery questions

**Overall Pass Criteria**: At least 3 out of 4 checks must pass (rating "sufficient" or higher), with at least 1 rating "impressive"

### Output Format Examples

**Individual Check from General Quality Category:**
```json
{
  "check_name": "evidence_support",
  "description": "Claims properly supported by evidence or marked as assumptions",
  "inputs_evaluated": [{"field": "analysis_claims", "value": "Sampled claims from analysis"}],
  "pass": true/false,
  "rating": "poor|sufficient|impressive",
  "rationale": "2-3 sentence explanation of evidence quality assessment"
}
```

**Individual Check from Founder Resonance Category:**
```json
{
  "check_name": "industry_sophistication",
  "description": "Nuanced understanding of industry dynamics and competitive landscape",
  "inputs_evaluated": [{"field": "full_analysis", "value": "Complete analysis structure"}],
  "pass": true/false,
  "rating": "poor|sufficient|impressive", 
  "rationale": "2-3 sentence explanation of industry sophistication assessment"
}
```

**Multiple Checks Returned from a Judge Category:**
```json
{
  "evidence_support": { /* individual check */ },
  "context_handling": { /* individual check */ },
  "content_distinctness": { /* individual check */ }
}
```

## Usage

### In Configuration
```python
config = EvalConfig(
    # ... other config
    deterministic_checks=["D-1", "D-2", "D-3", "D-4", "D-5"],
    llm_judges=["general_quality", "founder_resonance"]
)
```

### Judge Execution Order
1. **Deterministic judges** run first (fail-fast on first failure)
2. **LLM judge categories** run if deterministic checks pass, each returning multiple individual checks
3. Overall evaluation passes only if all individual checks pass their criteria

## Template System

LLM judge categories use Jinja2 templates located in:
- `templates/system/`: System prompts defining evaluation criteria and output format
- `templates/user/`: User prompts with data to evaluate

Each judge category has matching system and user templates (e.g., `general_quality.j2` in both directories). The system templates define how to return multiple individual checks in the standardized format.

## Cost Optimization

The combined judge categories demonstrate significant cost savings:
- **general_quality**: Combines 3 criteria into 1 LLM call, returning 3 individual checks = ~67% cost reduction
- **founder_resonance**: Combines 4 criteria into 1 LLM call, returning 4 individual checks = ~75% cost reduction

This reduces evaluation from 7 LLM calls to 2 calls while maintaining detailed, actionable results through structured multi-criteria assessment. Each criterion still gets its own individual check result for maximum actionability.