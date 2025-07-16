#!/usr/bin/env python3
"""
Structured prompt templates for LLM judges.
These prompts are designed for Gemini models with clear JSON output requirements.
"""

from typing import Dict, List, Any, Tuple


class JudgePrompts:
    """Centralized prompt templates for all LLM judges."""
    
    @staticmethod
    def traceability_prompt(website_content: str, sampled_claims: List[Tuple[str, str]]) -> str:
        """L-1: Traceability check prompt."""
        
        claims_text = "\n".join([
            f"{i+1}. [{field}] {claim}" 
            for i, (field, claim) in enumerate(sampled_claims)
        ])
        
        return f"""You are evaluating if factual claims in a company analysis are properly supported by evidence.

WEBSITE CONTENT:
{website_content}

CLAIMS TO EVALUATE:
{claims_text}

TASK: For each claim, determine if it either:
1. Cites specific website text/content, OR
2. Carries an [ASSUMPTION] tag, OR  
3. Is clearly supported by website evidence

PASS CRITERIA: At least 3 out of 5 claims must be properly supported.

IMPORTANT: Respond with ONLY valid JSON in this exact format:
{{
  "pass": true,
  "details": [
    {{
      "check_id": "L-1",
      "claim_number": 1,
      "claim": "the actual claim text",
      "supported": true,
      "reason": "brief explanation of why it's supported or not"
    }}
  ]
}}"""

    @staticmethod
    def actionability_prompt(analysis_data: Dict[str, Any]) -> str:
        """L-2: Actionability check prompt."""
        
        import json
        
        analysis_json = json.dumps({
            "description": analysis_data.get("description", ""),
            "business_profile_insights": analysis_data.get("business_profile_insights", []),
            "positioning_insights": analysis_data.get("positioning_insights", []),
            "target_customer_insights": analysis_data.get("target_customer_insights", [])
        }, indent=2)
        
        return f"""You are evaluating if a company analysis provides actionable insights for sales discovery calls.

ANALYSIS TO EVALUATE:
{analysis_json}

EVALUATION CRITERIA:
1. SPECIFICITY: Are insights specific to this company (not generic statements)?
2. DISCOVERY VALUE: Do insights suggest clear follow-up questions for sales calls?
3. EVIDENCE-BASED: Are claims grounded in observable information?

PASS CRITERIA: All three criteria must be met.

IMPORTANT: Respond with ONLY valid JSON in this exact format:
{{
  "pass": true,
  "details": [
    {{
      "check_id": "L-2",
      "criterion": "specificity",
      "pass": true,
      "reason": "brief explanation"
    }},
    {{
      "check_id": "L-2",
      "criterion": "discovery_value",
      "pass": true,
      "reason": "brief explanation"
    }},
    {{
      "check_id": "L-2",
      "criterion": "evidence_based",
      "pass": true,
      "reason": "brief explanation"
    }}
  ]
}}"""

    @staticmethod
    def redundancy_prompt(description: str, insights: List[str]) -> str:
        """L-3: Content redundancy check prompt."""
        
        insights_text = "\n".join([f"- {insight}" for insight in insights])
        
        return f"""You are evaluating content redundancy between sections of a company analysis.

DESCRIPTION:
{description}

BUSINESS INSIGHTS:
{insights_text}

TASK: Check if the business insights significantly duplicate content from the description.

PASS CRITERIA: Jaccard similarity should be < 0.30 (less than 30% overlap).

Instructions:
1. Calculate word-level overlap between description and insights
2. Determine if there's excessive duplication
3. Consider both exact matches and semantic similarity

IMPORTANT: Respond with ONLY valid JSON in this exact format:
{{
  "pass": true,
  "details": [
    {{
      "check_id": "L-3",
      "similarity_score": 0.15,
      "reason": "brief explanation of overlap assessment"
    }}
  ]
}}"""

    @staticmethod
    def context_steering_prompt(analysis_data: Dict[str, Any], user_context: str, context_type: str) -> str:
        """L-4: Context steering check prompt."""
        
        import json
        
        analysis_json = json.dumps(analysis_data, indent=2)
        
        if context_type == "valid":
            evaluation_rule = "Analysis should incorporate relevant details from user context"
            pass_criteria = "At least one insight clearly incorporates user-provided information"
        elif context_type == "noise":
            evaluation_rule = "Analysis should ignore gibberish and focus on core content"
            pass_criteria = "Analysis ignores irrelevant context and stays focused"
        else:
            # This shouldn't happen as "none" is handled separately
            evaluation_rule = "No specific context handling required"
            pass_criteria = "Auto-pass"
        
        return f"""You are evaluating if a company analysis appropriately handles user-provided context.

USER CONTEXT: {user_context}
CONTEXT TYPE: {context_type}

GENERATED ANALYSIS:
{analysis_json}

EVALUATION RULE: {evaluation_rule}

PASS CRITERIA: {pass_criteria}

IMPORTANT: Respond with ONLY valid JSON in this exact format:
{{
  "pass": true,
  "details": [
    {{
      "check_id": "L-4",
      "context_type": "{context_type}",
      "appropriate_handling": true,
      "reason": "brief explanation of how context was handled"
    }}
  ]
}}"""

    @staticmethod
    def get_system_prompt() -> str:
        """System prompt for all judge calls."""
        return """You are an expert evaluator for AI-generated company analysis content. 

Your task is to assess the quality of business analysis outputs according to specific criteria.

Key requirements:
1. Be objective and evidence-based in your evaluations
2. Provide clear, actionable feedback in your reasoning
3. Always respond with valid JSON only - no additional text or markdown
4. Use the exact JSON format specified in each prompt
5. Be concise but specific in your explanations

Focus on practical utility for sales and marketing teams who will use this analysis for discovery calls and customer outreach."""


class PromptValidator:
    """Validates prompt templates and responses."""
    
    @staticmethod
    def validate_response_format(response: str, expected_check_id: str) -> bool:
        """Validate that judge response follows expected format."""
        try:
            import json
            data = json.loads(response)
            
            # Check required fields
            if not isinstance(data, dict):
                return False
            
            if "pass" not in data or "details" not in data:
                return False
            
            if not isinstance(data["pass"], bool):
                return False
            
            if not isinstance(data["details"], list):
                return False
            
            # Check details format
            for detail in data["details"]:
                if not isinstance(detail, dict):
                    return False
                
                if "check_id" not in detail:
                    return False
                
                if detail["check_id"] != expected_check_id:
                    return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    @staticmethod
    def extract_pass_result(response: str) -> bool:
        """Extract pass/fail result from judge response."""
        try:
            import json
            data = json.loads(response)
            return data.get("pass", False)
        except:
            return False


if __name__ == "__main__":
    # Test prompt generation
    prompts = JudgePrompts()
    
    # Test traceability prompt
    sample_claims = [
        ("business_profile_insights", "Category: Payment Processing Platform"),
        ("positioning_insights", "Key Market Belief: Traditional payment systems are slow")
    ]
    
    traceability_prompt = prompts.traceability_prompt(
        website_content="Stripe is a payment processing platform...",
        sampled_claims=sample_claims
    )
    
    print("🧪 Sample Traceability Prompt:")
    print(traceability_prompt[:200] + "...")
    
    # Test response validation
    sample_response = '''{"pass": true, "details": [{"check_id": "L-1", "supported": true, "reason": "test"}]}'''
    
    is_valid = PromptValidator.validate_response_format(sample_response, "L-1")
    print(f"\n✅ Response format validation: {is_valid}")