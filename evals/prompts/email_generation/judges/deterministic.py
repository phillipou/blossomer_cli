"""
Email-specific deterministic checks.
Extends base deterministic judge with email-specific validation logic.
"""

from typing import Dict, Any
from evals.core.judges.deterministic import DeterministicJudge


class EmailDeterministicJudge(DeterministicJudge):
    """Email-specific deterministic validation checks."""
    
    def _check_format_compliance(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-3: Subject line format validation for emails."""
        subjects = data.get("subjects", {})
        primary_subject = subjects.get("primary", "")
        
        inputs_evaluated = [
            {"field": "primary_subject", "value": primary_subject}
        ]
        
        if not primary_subject:
            return {
                "check_name": "subject_format",
                "description": "Validates subject line has 3-4 words with proper capitalization",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Missing primary subject line"
            }
        
        # Check word count
        words = primary_subject.split()
        word_count = len(words)
        
        if word_count < 3 or word_count > 4:
            return {
                "check_name": "subject_format", 
                "description": "Validates subject line has 3-4 words with proper capitalization",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Subject line has {word_count} words, expected 3-4 words"
            }
        
        # Check first word capitalization
        if words[0] and not words[0][0].isupper():
            return {
                "check_name": "subject_format",
                "description": "Validates subject line has 3-4 words with proper capitalization", 
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Subject line must start with a capital letter"
            }
        
        # Check that only first word is capitalized (unless proper nouns)
        for word in words[1:]:
            if word and word[0].isupper() and word.lower() in ["i", "the", "a", "an", "and", "or", "but", "for", "of", "in", "on", "at", "to"]:
                return {
                    "check_name": "subject_format",
                    "description": "Validates subject line has 3-4 words with proper capitalization",
                    "inputs_evaluated": inputs_evaluated,
                    "pass": False,
                    "rationale": f"Only the first word should be capitalized (found '{word}')"
                }
        
        return {
            "check_name": "subject_format",
            "description": "Validates subject line has 3-4 words with proper capitalization",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "Subject line has correct format: 3-4 words with proper capitalization"
        }
    
    def _check_field_cardinality(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-4: Email body word count validation."""
        email_body = data.get("full_email_body", "")
        
        # Count words in email body
        word_count = len(email_body.split())
        
        inputs_evaluated = [
            {"field": "full_email_body", "value": f"{word_count} words"}
        ]
        
        if word_count < 50:
            return {
                "check_name": "word_count",
                "description": "Validates email body is between 50-100 words",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Email body has {word_count} words, minimum is 50"
            }
        
        if word_count > 100:
            return {
                "check_name": "word_count",
                "description": "Validates email body is between 50-100 words",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": f"Email body has {word_count} words, maximum is 100"
            }
        
        return {
            "check_name": "word_count",
            "description": "Validates email body is between 50-100 words",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": f"Email body has {word_count} words, within the 50-100 word range"
        }
    
    def _check_url_preservation(self, data: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """D-5: Company identity validation - ensures sender != recipient."""
        # Get sender company from test case context
        company_context = test_case.get("company_context", {})
        sender_company = company_context.get("company_name", "")
        
        # Check email body for [Company Name] placeholder
        email_body = data.get("full_email_body", "")
        
        inputs_evaluated = [
            {"field": "sender_company", "value": sender_company},
            {"field": "email_body_contains", "value": "[Company Name] present" if "[Company Name]" in email_body else "[Company Name] missing"}
        ]
        
        # Must contain [Company Name] placeholder
        if "[Company Name]" not in email_body:
            return {
                "check_name": "identity_check",
                "description": "Validates proper sender/recipient identity handling",
                "inputs_evaluated": inputs_evaluated,
                "pass": False,
                "rationale": "Email must use [Company Name] placeholder for recipient"
            }
        
        # Should not confuse sender with recipient
        if sender_company and sender_company in email_body.replace("[Company Name]", ""):
            # Check if it's being used incorrectly as the recipient
            if f"to {sender_company}" in email_body.lower() or f"at {sender_company}" in email_body.lower():
                return {
                    "check_name": "identity_check",
                    "description": "Validates proper sender/recipient identity handling",
                    "inputs_evaluated": inputs_evaluated,
                    "pass": False,
                    "rationale": f"Email incorrectly uses sender company '{sender_company}' as recipient"
                }
        
        return {
            "check_name": "identity_check",
            "description": "Validates proper sender/recipient identity handling",
            "inputs_evaluated": inputs_evaluated,
            "pass": True,
            "rationale": "Email correctly uses [Company Name] placeholder and maintains proper sender/recipient identity"
        }