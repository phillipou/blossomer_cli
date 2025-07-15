"""
models.py - Pydantic models for prompt template variables.

This module defines all Pydantic models used as context variables for Jinja2 prompt templates.
Each section groups models by the type of prompt or context they support.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

# ==============================================================================
# Shared Enums and Types
# ==============================================================================


class ContextQuality(str, Enum):
    """Overall context quality assessment."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class DataPresence(str, Enum):
    """Presence level for specific data types."""

    COMPREHENSIVE = "comprehensive"
    ADEQUATE = "adequate"
    MINIMAL = "minimal"
    MISSING = "missing"


# ==============================================================================
# Product Overview Prompt Variables
# ==============================================================================


class ProductOverviewPromptVars(BaseModel):
    """Variables for the product_overview.jinja2 prompt template."""

    user_inputted_context: Optional[str] = None
    website_content: Optional[str] = None
    company_context: Optional[str] = None
    context_quality: Optional[str] = None
    assessment_summary: Optional[str] = None
    company_name: Optional[str] = None
    input_website_url: str  # Canonical website URL, always required


# ==============================================================================
# Email Generation Prompt Variables
# ==============================================================================


class EmailGenerationPromptVars(BaseModel):
    """Variables for the email_generation.jinja2 prompt template."""

    company_context: Optional[Dict[str, Any]] = None
    target_account: Optional[Dict[str, Any]] = None
    target_persona: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


# ==============================================================================
# Context Assessment Prompt Variables
# ==============================================================================


class ContentSection(BaseModel):
    """Assessment of a specific content section (e.g., product features, pricing)."""

    section_type: str = Field(
        ...,
        description="Type of content (e.g., 'product_features', 'pricing', 'customers')",
    )
    presence: DataPresence = Field(..., description="Level of information present")
    quality_score: float = Field(..., ge=0, le=1, description="Quality score 0-1")
    key_insights: List[str] = Field(
        default_factory=list, description="Key information extracted"
    )
    gaps: List[str] = Field(default_factory=list, description="Missing information")


class EndpointReadiness(BaseModel):
    """Readiness assessment for a specific endpoint."""

    endpoint: str = Field(
        ..., description="Endpoint name (e.g., 'product_overview', 'target_company')"
    )
    is_ready: bool = Field(..., description="Whether sufficient context exists")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    missing_requirements: List[str] = Field(
        default_factory=list, description="What's needed for this endpoint"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="How to improve readiness"
    )


class ContextAssessmentVars(BaseModel):
    """Variables for context assessment prompt template."""

    website_content: str
    target_endpoint: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


class ContextAssessmentResult(BaseModel):
    """Comprehensive context quality assessment result from the LLM."""

    overall_quality: ContextQuality = Field(
        ..., description="Overall quality assessment of the website content"
    )
    overall_confidence: float = Field(
        ..., ge=0, le=1, description="Overall confidence score (0-1) in the assessment"
    )
    content_sections: List[ContentSection] = Field(
        ..., description="Detailed assessment of each content section found"
    )
    company_clarity: Dict[str, Any] = Field(
        ...,
        description="Assessment of how clearly the company's purpose is communicated",
    )
    endpoint_readiness: List[EndpointReadiness] = Field(
        ..., description="Readiness assessment for each GTM endpoint"
    )
    data_quality_metrics: Dict[str, float] = Field(
        ..., description="Specific quality metrics"
    )
    recommendations: Dict[str, List[str]] = Field(
        ..., description="Recommendations for improving context quality"
    )
    summary: str = Field(
        ..., description="2-3 sentence summary of the context assessment"
    )
    source: str = Field(
        ..., description="Source of the context (e.g., 'website', 'user_input')"
    )
    from_cache: bool = Field(
        ..., description="Whether the context was retrieved from cache"
    )


# ==============================================================================
# Target Account Prompt Variables
# ==============================================================================


class TargetAccountPromptVars(BaseModel):
    """Variables for the target_account.jinja2 prompt template."""

    website_content: Optional[str] = Field(
        None, description="The preprocessed content from the company's website."
    )
    account_profile_name: Optional[str] = Field(
        None,
        description="Name of the target account profile (e.g., 'Mid-market SaaS companies')",
    )
    hypothesis: Optional[str] = Field(
        None,
        description="User's hypothesis about why this account profile is ideal",
    )
    additional_context: Optional[str] = Field(
        None,
        description="Additional user-provided context for target account generation",
    )
    company_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Company context from previous endpoints (JSON object)",
    )
    context_quality: Optional[str] = Field(
        None, description="Optional context quality assessment for the prompt."
    )
    assessment_summary: Optional[str] = Field(
        None, description="Optional summary of the context assessment."
    )


# ==============================================================================
# Target Persona Prompt Variables
# ==============================================================================


class TargetPersonaPromptVars(BaseModel):
    """Variables for the target_persona.jinja2 prompt template."""

    persona_profile_name: Optional[str] = Field(
        None, description="Name of the target persona profile"
    )
    hypothesis: Optional[str] = Field(
        None,
        description="User's hypothesis about why this persona is ideal for the solution",
    )
    additional_context: Optional[str] = Field(
        None,
        description="Additional context or specifications about the target persona",
    )
    company_context: Optional[Dict[str, Any]] = Field(
        None, description="Structured context about the analyzed company/product"
    )
    website_content: Optional[str] = Field(
        None, description="The preprocessed content from the company's website"
    )
    target_account_context: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Target account profile context - dictionary of the ideal customer "
            "company type this persona works for"
        ),
    )


# ======================================================================
# Company Overview Output Model (matches context_assessment.jinja2 template)
# ======================================================================


class CompanyOverviewResult(BaseModel):
    """Structured product/company overview result from the LLM (context_assessment prompt)."""

    company_name: str
    company_url: str
    company_overview: str
    capabilities: List[str]
    business_model: List[str]
    differentiated_value: List[str]
    customer_benefits: List[str]
    alternatives: List[str]
    testimonials: List[str]
    product_description: str
    key_features: List[str]
    company_profiles: List[str]
    persona_profiles: List[str]
    use_cases: List[str]
    pain_points: List[str]
    pricing: str
    metadata: Dict[str, Any]


# ======================================================================
# Target Persona Response Model
# ======================================================================


class TargetPersonaResponse(BaseModel):
    """Model for the target_persona_response.jinja2 prompt template."""

    id: int
    persona_name: str
    persona_description: str
    buying_signals: List[str]
    criteria: List[str]
    use_cases: List[str]
    created_at: str
    updated_at: str


def create_target_persona_response(persona):
    """
    Create a TargetPersonaResponse from a persona object.

    Args:
        persona: The persona object to convert to a TargetPersonaResponse.

    Returns:
        TargetPersonaResponse: The converted TargetPersonaResponse object.
    """
    if not persona:
        return None
    return TargetPersonaResponse(
        id=persona.id,
        persona_name=persona.persona_name,
        persona_description=persona.persona_description,
        buying_signals=persona.buying_signals,
        criteria=persona.criteria,
        use_cases=persona.use_cases,
        created_at=persona.created_at,
        updated_at=persona.updated_at,
    )
