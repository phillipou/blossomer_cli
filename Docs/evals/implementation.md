# Product Overview Evaluation Implementation Guide

## Overview

This document provides step-by-step instructions for implementing the evaluation harness for `product_overview.jinja2` using Promptfoo.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Promptfoo)
- Anthropic API key
- Access to target websites for scraping

## Implementation Strategy

### LLM Judge Design Principles

1. **Unified Provider Interface**: Use TensorBlock Forge for easy model switching across providers
2. **Cost-Effective Models**: Start with Gemini 1.5 Flash (~$0.0001 per call), easily switch to others
3. **Structured Prompts**: Consistent JSON response format with clear pass/fail criteria
4. **Contextual Sampling**: Random sampling of claims for traceability (L-1) to ensure broad coverage
5. **Fail-Fast Logic**: Deterministic checks run first to avoid expensive LLM calls on obviously bad outputs
6. **Error Handling**: Graceful degradation when judge calls fail with fallback responses

### Cost Management Strategy

- **Estimated Cost per Full Run**: ~$0.021 (21 test cases × 4 judges × $0.0001 + deterministic checks)
- **Monthly Budget**: ~$1 for daily evaluation runs  
- **Cost Controls**: Easy model switching via Forge, limit max_tokens, batch calls when possible
- **Model Flexibility**: Can easily test different providers (Gemini, Claude, OpenAI) for optimal cost/quality

### Quality Assurance Approach

- **Judge Calibration**: Test judges on known good/bad examples before deployment
- **Consistency Checks**: Compare judge decisions across similar inputs
- **Human Validation**: Periodic spot-checks of judge decisions vs human assessment

## Current Implementation Status

### ✅ Completed Tasks
1. **Directory Structure**: Created organized workspace in `evals/product_overview/`
2. **Schema Generation**: Auto-generated JSON schema from `ProductOverviewResponse` Pydantic model
3. **Deterministic Checks**: Implemented all 5 checks (D-1 through D-5) with error handling
4. **LLM Judge Implementation**: Complete with TensorBlock Forge integration for unified provider access
5. **Structured Prompt Templates**: Modular, testable prompt system for all 4 judge types
6. **Documentation**: Comprehensive implementation guide with cost analysis

### 🔄 In Progress
- **Test Dataset Creation**: Need to create website content and CSV test cases

### 📋 Next Steps
- Create test dataset with website scraping
- Configure Promptfoo integration
- Build evaluation runner script
- Add reporting dashboard

## Key Benefits of TensorBlock Forge Integration

### **Unified Provider Access**
- **Single API**: OpenAI-compatible interface for all providers (Gemini, Claude, OpenAI, etc.)
- **Easy Model Switching**: Change models via environment variable `EVAL_MODEL`
- **Cost Optimization**: Test different providers to find optimal cost/quality balance

### **Implementation Features**
- **Structured Prompts**: Modular prompt templates with validation
- **Error Handling**: Graceful degradation with retries and fallbacks  
- **Cost Tracking**: Built-in estimation for different model pricing
- **JSON Validation**: Enforced structured output with format validation

### **Model Flexibility Examples**
```python
# Switch between models easily in code
judge = ForgeJudge()
judge.run_all_judges(data, website_content, model="gemini-1.5-flash")    # ~$0.0001/call
judge.run_all_judges(data, website_content, model="claude-3-5-haiku")    # ~$0.001/call  
judge.run_all_judges(data, website_content, model="gpt-4o-mini")         # ~$0.0002/call
```

## Implementation Roadmap

### Phase 1: Core Infrastructure (High Priority)

#### 1. Set up Promptfoo Configuration and Directory Structure
**Goal**: Create organized evaluation workspace
**Tasks**:
- [ ] Install Promptfoo: `npm install -g promptfoo`
- [ ] Create directory structure:
  ```
  evals/
  ├── product_overview/
  │   ├── promptfooconfig.yaml
  │   ├── schema/
  │   │   └── product_overview_schema.json
  │   ├── checks/
  │   │   ├── deterministic_checks.py
  │   │   └── llm_judges.py
  │   ├── data/
  │   │   ├── test_cases.csv
  │   │   └── website_content/
  │   └── results/
  ```
- [ ] Initialize Promptfoo config: `promptfoo init`

#### 2. Create JSON Schema Validation
**Goal**: Validate product_overview template output structure
**Tasks**:
- [ ] Generate JSON schema from existing Pydantic models in `app/schemas/__init__.py`
- [ ] Use `ProductOverviewResponse` model to ensure schema sync
- [ ] Add evaluation-specific validation rules (Key: Value format, etc.)
- [ ] Test schema against sample outputs

#### 3. Implement Deterministic Checks (D-1 through D-5)
**Goal**: Fast, zero-cost validation of basic output quality
**Tasks**:
- [ ] **D-1 Valid JSON**: Basic parsing validation
- [ ] **D-2 Schema Compliance**: Field presence and type validation
- [ ] **D-3 Format Compliance**: "Key: Value" pattern validation for insights
- [ ] **D-4 Field Cardinality**: Array length validation (3-5 items)
- [ ] **D-5 URL Preservation**: Input/output URL matching
- [ ] Create test runner that aborts on first failure

#### 4. Build LLM Judge Implementations (L-1 through L-4)
**Goal**: Qualitative assessment using LLM-as-judge
**Strategy**: Use Claude 3.5 Haiku for cost-effective judging with structured prompts
**Tasks**:
- [ ] **L-1 Traceability**: Sample 5 factual claims, verify website evidence or [ASSUMPTION] tags
- [ ] **L-2 Actionability**: Evaluate specificity, discovery value, and evidence-based claims
- [ ] **L-3 Content Redundancy**: Check Jaccard similarity between description and insights
- [ ] **L-4 Context Steering**: Validate appropriate handling of valid/noise/none context
- [ ] Implement standardized judge response format with pass/fail + details
- [ ] Add judge result aggregation and cost tracking
- [ ] Create judge prompt templates for consistency

### Phase 2: Data and Configuration (Medium Priority)

#### 5. Create Test Dataset
**Goal**: Comprehensive test cases covering edge cases
**Tasks**:
- [ ] Select 5 high-quality SaaS sites:
  - Stripe (payments)
  - Notion (productivity) 
  - Figma (design)
  - Datadog (monitoring)
  - Slack (communications)
- [ ] Select 2 weak landing pages for edge testing
- [ ] Create 3 context variants per URL (none, valid, noise)
- [ ] Format as CSV with required columns

#### 6. Scrape Website Content
**Goal**: Prepare realistic test data
**Tasks**:
- [ ] Build website scraper (or use existing tools)
- [ ] Extract homepage content for each test URL
- [ ] Clean and format content for template input
- [ ] Store content in organized file structure
- [ ] Validate content quality and completeness

#### 7. Write Promptfoo Configuration
**Goal**: Orchestrate evaluation execution
**Tasks**:
- [ ] Configure prompt template path
- [ ] Set up Anthropic provider
- [ ] Define test assertions (deterministic + LLM judges)
- [ ] Configure dataset loading
- [ ] Set up result output format

#### 8. Create Evaluation Runner Script
**Goal**: Streamlined evaluation execution
**Tasks**:
- [ ] Create Python script for end-to-end evaluation
- [ ] Add command-line interface for configuration
- [ ] Implement result parsing and summary
- [ ] Add cost tracking and performance metrics
- [ ] Create automated reporting

### Phase 3: Polish and Maintenance (Low Priority)

#### 9. Add Reporting and Metrics Dashboard
**Goal**: Visual evaluation results and trends
**Tasks**:
- [ ] Create HTML report generation
- [ ] Add pass/fail rate visualizations
- [ ] Track evaluation costs and performance
- [ ] Implement trend analysis over time
- [ ] Add alerting for quality degradation

## Detailed Implementation Steps

### Step 1: Directory Setup

```bash
# Create directory structure
mkdir -p evals/product_overview/{schema,checks,data/website_content,results}
cd evals/product_overview

# Install dependencies
npm install -g promptfoo
pip install jsonschema beautifulsoup4 requests
```

### Step 2: JSON Schema Generation

Create `schema/generate_schema.py` to generate schema from Pydantic models:

```python
#!/usr/bin/env python3
"""
Generate JSON Schema from Pydantic models for evaluation purposes.
This ensures our evaluation schemas stay in sync with the actual models.
"""

import json
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "app"))

from schemas import ProductOverviewResponse

def generate_json_schema():
    """Generate JSON Schema from ProductOverviewResponse Pydantic model."""
    
    # Generate schema from Pydantic model
    schema = ProductOverviewResponse.model_json_schema()
    
    # Add evaluation-specific constraints
    schema["title"] = "Product Overview Evaluation Schema"
    schema["description"] = "Schema for validating product_overview.jinja2 template output"
    
    # Add custom validation rules for evaluation
    properties = schema.get("properties", {})
    
    # Ensure Key: Value format validation for insight fields
    insight_fields = [
        "business_profile_insights", "capabilities", 
        "use_case_analysis_insights", "positioning_insights",
        "objections", "target_customer_insights"
    ]
    
    for field in insight_fields:
        if field in properties and "items" in properties[field]:
            # Add regex pattern for Key: Value format
            properties[field]["items"]["pattern"] = "^[^:]+:.+"
            properties[field]["items"]["description"] = "Must follow 'Key: Value' format"
    
    return schema

if __name__ == "__main__":
    schema = generate_json_schema()
    output_path = Path(__file__).parent / "product_overview_schema.json"
    
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ Generated schema saved to {output_path}")
```

Then run: `python schema/generate_schema.py`

### Step 3: Deterministic Checks Implementation

Create `checks/deterministic_checks.py`:

```python
import json
import jsonschema
from typing import Dict, List, Any

def validate_json(output: str) -> Dict[str, Any]:
    """D-1: Valid JSON check"""
    try:
        data = json.loads(output)
        return {"pass": True, "data": data}
    except json.JSONDecodeError as e:
        return {"pass": False, "error": str(e)}

def validate_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """D-2: Schema compliance check"""
    with open("schema/product_overview_schema.json") as f:
        schema = json.load(f)
    
    try:
        jsonschema.validate(data, schema)
        # Check 90% fields non-empty
        non_empty_count = sum(1 for v in data.values() if v)
        if non_empty_count / len(data) >= 0.9:
            return {"pass": True}
        else:
            return {"pass": False, "error": "Less than 90% fields populated"}
    except jsonschema.ValidationError as e:
        return {"pass": False, "error": str(e)}

def validate_format_compliance(data: Dict[str, Any]) -> Dict[str, Any]:
    """D-3: Format compliance check"""
    insight_fields = [
        "business_profile_insights", 
        "use_case_analysis_insights",
        "positioning_insights",
        "target_customer_insights"
    ]
    
    for field in insight_fields:
        if field in data:
            for insight in data[field]:
                if ":" not in insight:
                    return {
                        "pass": False, 
                        "error": f"Field {field} missing colon separator"
                    }
    
    return {"pass": True}

# Additional checks D-4 and D-5...
```

### Step 4: LLM Judge Implementation with TensorBlock Forge

Create `checks/llm_judges.py` using Forge for unified provider access:

```python
import anthropic
import json
import random
from typing import Dict, List, Any, Optional

class LLMJudge:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"  # Cost-effective model for judging
    
    def _call_judge(self, prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Make a standardized judge call with error handling."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            # Validate response format
            if not isinstance(result, dict) or "pass" not in result:
                raise ValueError("Judge response missing required 'pass' field")
            
            return result
            
        except Exception as e:
            return {
                "pass": False,
                "error": f"Judge evaluation failed: {str(e)}",
                "details": []
            }
    
    def judge_traceability(self, data: Dict[str, Any], website_content: str) -> Dict[str, Any]:
        """L-1: Traceability check - verify claims are evidence-based."""
        
        # Sample factual claims from insight fields
        insight_fields = [
            "business_profile_insights",
            "use_case_analysis_insights", 
            "positioning_insights"
        ]
        
        all_claims = []
        for field in insight_fields:
            if field in data and data[field]:
                all_claims.extend([(field, claim) for claim in data[field]])
        
        # Sample 5 claims randomly
        sampled_claims = random.sample(all_claims, min(5, len(all_claims)))
        
        prompt = f"""
You are evaluating if factual claims in a company analysis are properly supported by evidence.

WEBSITE CONTENT:
{website_content}

CLAIMS TO EVALUATE:
{chr(10).join([f"{i+1}. [{field}] {claim}" for i, (field, claim) in enumerate(sampled_claims)])}

TASK: For each claim, determine if it either:
1. Cites specific website text/content, OR
2. Carries an [ASSUMPTION] tag, OR  
3. Is clearly supported by website evidence

PASS CRITERIA: At least 3 out of 5 claims must be properly supported.

Return JSON format:
{{
  "pass": true/false,
  "details": [
    {{
      "check_id": "L-1",
      "claim_number": 1,
      "claim": "the actual claim text",
      "supported": true/false,
      "reason": "brief explanation of why it's supported or not"
    }}
  ]
}}
"""
        
        return self._call_judge(prompt, max_tokens=800)
    
    def judge_actionability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """L-2: Actionability check - evaluate specificity and discovery value."""
        
        prompt = f"""
You are evaluating if a company analysis provides actionable insights for sales discovery calls.

ANALYSIS TO EVALUATE:
{json.dumps({
    "description": data.get("description", ""),
    "business_profile_insights": data.get("business_profile_insights", []),
    "positioning_insights": data.get("positioning_insights", []),
    "target_customer_insights": data.get("target_customer_insights", [])
}, indent=2)}

EVALUATION CRITERIA:
1. SPECIFICITY: Are insights specific to this company (not generic statements)?
2. DISCOVERY VALUE: Do insights suggest clear follow-up questions for sales calls?
3. EVIDENCE-BASED: Are claims grounded in observable information?

PASS CRITERIA: All three criteria must be met.

Return JSON format:
{{
  "pass": true/false,
  "details": [
    {{
      "check_id": "L-2",
      "criterion": "specificity|discovery_value|evidence_based",
      "pass": true/false,
      "reason": "brief explanation"
    }}
  ]
}}
"""
        
        return self._call_judge(prompt, max_tokens=600)
    
    def judge_redundancy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """L-3: Content redundancy check - ensure sections don't duplicate content."""
        
        description = data.get("description", "")
        insights = data.get("business_profile_insights", [])
        
        prompt = f"""
You are evaluating content redundancy between sections of a company analysis.

DESCRIPTION:
{description}

BUSINESS INSIGHTS:
{chr(10).join([f"- {insight}" for insight in insights])}

TASK: Check if the business insights significantly duplicate content from the description.

PASS CRITERIA: Jaccard similarity should be < 0.30 (less than 30% overlap).

Calculate word-level overlap and determine if there's excessive duplication.

Return JSON format:
{{
  "pass": true/false,
  "details": [
    {{
      "check_id": "L-3",
      "similarity_score": 0.XX,
      "reason": "brief explanation of overlap assessment"
    }}
  ]
}}
"""
        
        return self._call_judge(prompt, max_tokens=400)
    
    def judge_context_steering(self, data: Dict[str, Any], user_context: str, context_type: str) -> Dict[str, Any]:
        """L-4: Context steering check - validate appropriate context usage."""
        
        if context_type == "none":
            # Auto-pass for no context
            return {
                "pass": True,
                "details": [{"check_id": "L-4", "reason": "No context provided - auto-pass"}]
            }
        
        prompt = f"""
You are evaluating if a company analysis appropriately handles user-provided context.

USER CONTEXT: {user_context}
CONTEXT TYPE: {context_type}

GENERATED ANALYSIS:
{json.dumps(data, indent=2)}

EVALUATION RULES:
- If context_type is "valid": Analysis should incorporate relevant details from user context
- If context_type is "noise": Analysis should ignore gibberish and focus on core content

PASS CRITERIA:
- Valid context: At least one insight clearly incorporates user-provided information
- Noise context: Analysis ignores irrelevant context and stays focused

Return JSON format:
{{
  "pass": true/false,
  "details": [
    {{
      "check_id": "L-4",
      "context_type": "{context_type}",
      "appropriate_handling": true/false,
      "reason": "brief explanation"
    }}
  ]
}}
"""
        
        return self._call_judge(prompt, max_tokens=500)
    
    def run_all_judges(self, data: Dict[str, Any], website_content: str, 
                       user_context: str = "", context_type: str = "none") -> Dict[str, Any]:
        """Run all LLM judges and aggregate results."""
        
        results = {
            "overall_pass": False,
            "judges": {},
            "total_cost_estimate": 0.0
        }
        
        # Run each judge
        judges = [
            ("L-1_traceability", lambda: self.judge_traceability(data, website_content)),
            ("L-2_actionability", lambda: self.judge_actionability(data)),
            ("L-3_redundancy", lambda: self.judge_redundancy(data)),
            ("L-4_context_steering", lambda: self.judge_context_steering(data, user_context, context_type))
        ]
        
        all_passed = True
        for judge_name, judge_func in judges:
            result = judge_func()
            results["judges"][judge_name] = result
            
            if not result.get("pass", False):
                all_passed = False
            
            # Estimate cost (rough: ~$0.001 per judge call)
            results["total_cost_estimate"] += 0.001
        
        results["overall_pass"] = all_passed
        return results

# Usage example for Promptfoo integration
def evaluate_with_llm_judges(output: str, input_vars: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Promptfoo integration."""
    
    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        return {"pass": False, "error": f"Invalid JSON: {e}"}
    
    judge = LLMJudge(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    return judge.run_all_judges(
        data=data,
        website_content=input_vars.get("website_content", ""),
        user_context=input_vars.get("user_inputted_context", ""),
        context_type=input_vars.get("context_type", "none")
    )
```

### Step 5: Test Dataset Creation

Create `data/test_cases.csv`:

```csv
input_website_url,context_type,user_inputted_context,expected_company_name
https://stripe.com,none,"",Stripe
https://stripe.com,valid,"Payment processing for online marketplaces",Stripe
https://stripe.com,noise,"Purple elephants dancing in the moonlight",Stripe
https://notion.so,none,"",Notion
...
```

### Step 6: Promptfoo Configuration

Create `promptfooconfig.yaml`:

```yaml
description: "Product Overview Template Evaluation"

prompts:
  - file://../../app/prompts/templates/product_overview.jinja2

providers:
  - id: anthropic:claude-3-5-sonnet-20241022
    config:
      apiKey: env:ANTHROPIC_API_KEY

tests:
  - vars:
      input_website_url: https://stripe.com
      context_type: none
      user_inputted_context: ""
    assert:
      - type: python
        value: file://checks/deterministic_checks.py:run_all_checks
      - type: llm-rubric
        value: file://checks/llm_judges.py:run_all_judges

datasets:
  - file://data/test_cases.csv

outputPath: ./results/evaluation_results.json
```

### Step 7: Evaluation Runner

Create `run_evaluation.py`:

```python
#!/usr/bin/env python3

import subprocess
import json
import argparse
from pathlib import Path

def run_evaluation(config_path: str = "promptfooconfig.yaml"):
    """Run complete evaluation suite"""
    print("🚀 Starting Product Overview Evaluation...")
    
    # Run Promptfoo evaluation
    result = subprocess.run([
        "promptfoo", "eval", "-c", config_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Evaluation failed: {result.stderr}")
        return False
    
    # Parse and summarize results
    with open("results/evaluation_results.json") as f:
        results = json.load(f)
    
    print_summary(results)
    return True

def print_summary(results: dict):
    """Print evaluation summary"""
    total_tests = len(results.get("results", []))
    passed_tests = sum(1 for r in results["results"] if r.get("success", False))
    
    print(f"\n📊 Evaluation Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {passed_tests/total_tests*100:.1f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="promptfooconfig.yaml")
    args = parser.parse_args()
    
    run_evaluation(args.config)
```

## Success Criteria

- [ ] All deterministic checks pass >95% of the time
- [ ] LLM judges achieve >90% pass rate on quality criteria
- [ ] Full evaluation completes in <10 minutes
- [ ] Total evaluation cost <$5 per run
- [ ] Clear, actionable failure reports

## Next Steps

1. **Execute Phase 1** tasks to establish core infrastructure
2. **Validate** with a small subset of test cases
3. **Scale up** to full dataset once validated
4. **Iterate** based on initial results and edge cases discovered
5. **Extend** to other prompt templates using this foundation

## Maintenance

- **Weekly**: Review any new failure patterns
- **Monthly**: Update test dataset with new edge cases
- **Quarterly**: Recalibrate LLM judges and success thresholds
- **As needed**: Update schema when template evolves