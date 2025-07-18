# Evaluation System

The evaluation system provides automated quality assurance for prompt templates using deterministic checks and LLM judges.

## Quick Start

```bash
# List available prompts
python3 -m cli.main eval list

# Validate a prompt configuration
python3 -m cli.main eval validate product_overview

# Run evaluation on a specific prompt
python3 -m cli.main eval run product_overview --sample-size 5

# Run all evaluations
python3 -m cli.main eval run all --sample-size 3
```

## Architecture

The evaluation system consists of:

- **Core Framework** (`evals/core/`): Unified runner, configuration management, dataset handling
- **Prompt Configurations** (`evals/prompts/{name}/`): Per-prompt configs, datasets, and schemas
- **Judges** (`evals/core/judges/`): Deterministic and LLM-based evaluation logic
  - **LLM Judge Templates** (`evals/core/judges/templates/`): Jinja2 templates with system/user separation
    - `system/`: System prompt templates containing instructions, criteria, and response formats
    - `user/`: User prompt templates containing only data/variables to evaluate
- **CLI Integration** (`cli/commands/eval.py`): User-friendly command interface

## Creating New Evaluations

1. **Create prompt configuration**:
   ```bash
   python3 -m cli.main eval create my_prompt \
     --service-module "app.services.my_service" \
     --service-function "my_service_function" \
     --create-sample-data
   ```

2. **Add test cases** to `evals/prompts/my_prompt/data.csv`:
   ```csv
   input_website_url,context_type,user_inputted_context
   https://example.com,none,
   https://test.com,valid,Looking for enterprise solutions
   https://demo.com,noise,Random gibberish text
   ```

3. **Create JSON schema** in `evals/prompts/my_prompt/schema.json`

4. **Validate and run**:
   ```bash
   python3 -m cli.main eval validate my_prompt
   python3 -m cli.main eval run my_prompt
   ```

## Evaluation Types

### Deterministic Checks (Zero Cost)
- **D-1**: Valid JSON parsing
- **D-2**: Schema compliance (90% field population)
- **D-3**: Format compliance ("Key: Value" patterns)
- **D-4**: Field cardinality (3-5 items per array)
- **D-5**: URL preservation (input matches output)

### LLM Judge Categories (Ultra-Low Cost)
Each category makes a single LLM call but returns multiple individual checks:

- **content_integrity**: Returns 3 checks - evidence_support, context_handling, content_distinctness (prompt-agnostic)
- **business_insight**: Returns 4 checks - industry_sophistication, strategic_depth, authentic_voice_capture, actionable_specificity (product_overview specific)
- **account_targeting_quality**: Returns 3 checks - proxy_strength, detection_feasibility, profile_crispness (target_account specific)

**Individual Check Structure**:
Each check (deterministic and LLM) follows a standardized format:
```json
{
  "check_name": "evidence_support",
  "description": "Claims properly supported by evidence or marked as assumptions",
  "inputs_evaluated": [{"field": "positioning_insights", "value": "Key Market Belief: Manual QA methods don't scale; Unique Approach: AI-powered sampling"}],
  "pass": true,
  "rating": "impressive",  // Optional for LLM checks only
  "rationale": "2-3 sentence explanation of assessment"
}
```

**Display Features**:
- **Rating Display**: LLM checks show color-coded ratings (IMPRESSIVE/SUFFICIENT/POOR)
- **Rating Distribution Table**: Summary showing count and percentage of each rating level
- **Inputs Evaluated**: Shows actual field values being assessed (not summaries)
- **Granular Feedback**: Each criterion provides individual actionable feedback

**Template Organization**:
- System prompts contain all evaluation criteria, instructions, and response formats
- User prompts contain the data to be evaluated AND JSON format specification with actual field values
- Clean separation enables easier editing and prevents variable naming drift

## Configuration

Each prompt has a `config.yaml` file:

```yaml
name: "My Prompt Evaluation"
service:
  module: "app.services.my_service"
  function: "my_service_function"
schema: "schema.json"
judges:
  deterministic: ["D-1", "D-2", "D-3", "D-4", "D-5"]
  llm: ["content_integrity", "business_insight"]
# For target_account prompts, use account_targeting_quality instead of business_insight
models:
  default: "OpenAI/gpt-4.1-nano"
  fallback: "Gemini/models/gemini-1.5-flash"
```

## Success Criteria

- **Deterministic Pass Rate**: >95% on valid inputs
- **LLM Judge Pass Rate**: >90% on quality criteria
- **Overall Pass Rate**: >90% to pass evaluation
- **Cost Efficiency**: <$0.10 per full evaluation run

## Advanced Usage

```bash
# Run with verbose output
python3 -m cli.main eval run product_overview --verbose

# Save results to file
python3 -m cli.main eval run product_overview --output results.json

# Run with specific sample size
python3 -m cli.main eval run product_overview --sample-size 10
```

## Direct Runner Usage

For development and debugging:

```bash
# Direct runner access
python3 -m evals.core.runner product_overview --sample-size 3 --verbose

# All prompts
python3 -m evals.core.runner all --sample-size 5 --output combined_results.json
```

## Benefits

- **Quality Assurance**: Consistent output quality across different inputs
- **Cost Effective**: 3 LLM calls return 10 individual actionable checks (~70% cost reduction)
- **Actual Field Values**: Shows real data being evaluated, not summaries
- **Granular Feedback**: Each criterion provides specific, actionable feedback with ratings
- **Fast Feedback**: Deterministic checks catch issues before expensive LLM calls
- **Extensible**: Easy to add new prompts and evaluation criteria
- **Regression Prevention**: Catch quality degradation early with detailed ratings
- **Model Comparison**: A/B test different LLM providers
- **Template-Driven Architecture**: System/user prompt separation prevents variable naming drift
- **Actionable Results**: Individual check format makes debugging and improvement straightforward