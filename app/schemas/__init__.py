"""
schemas.py - Centralized schemas for Blossomer GTM API

This module defines JSON schemas for LLM structured outputs and database models,
enabling reuse and validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, ConfigDict
from enum import Enum
from datetime import datetime


class ProductOverviewRequest(BaseModel):
    website_url: str = Field(
        ...,
        description="Company website or landing page URL",
    )
    user_inputted_context: Optional[str] = Field(
        None,
        description="Optional user-provided context for campaign generation",
    )
    company_context: Optional[str] = Field(
        None,
        description="Optional company context inferred from previous endpoints",
    )


class BusinessProfile(BaseModel):
    category: str = Field(..., description="5-6 words on product category")
    business_model: str = Field(
        ..., description="1-2 sentences on revenue streams and pricing"
    )
    existing_customers: str = Field(
        ..., description="1-3 sentences on customer evidence"
    )


class UseCaseAnalysis(BaseModel):
    process_impact: str = Field(
        ..., description="Primary process/workflow this product impacts"
    )
    problems_addressed: str = Field(
        ..., description="Problems and inefficiencies solved"
    )
    how_they_do_it_today: str = Field(
        ..., description="Current state/alternative approaches"
    )


class Positioning(BaseModel):
    key_market_belief: str = Field(
        ..., description="Unique POV on why current solutions fail"
    )
    unique_approach: str = Field(..., description="Differentiated value proposition")
    language_used: str = Field(..., description="Terminology and mental models used")


class ICPHypothesis(BaseModel):
    target_account_hypothesis: str = Field(..., description="Ideal customer profile")
    target_persona_hypothesis: str = Field(
        ..., description="Ideal stakeholder/decision-maker"
    )


class ProductOverviewResponse(BaseModel):
    company_name: str = Field(..., description="Official company name")
    company_url: str = Field(..., description="Canonical website URL")
    description: str = Field(
        ..., description="2-3 sentences on core identity and what they do"
    )
    business_profile_insights: Optional[List[str]] = Field(
        None,
        description=(
            "Business profile insights as a list of strings in 'Key: Value' format. (Flattened)"
        ),
    )
    capabilities: List[str] = Field(
        ..., description="Key features and capabilities"
    )
    use_case_analysis_insights: Optional[List[str]] = Field(
        None,
        description=(
            "Use case analysis insights as a list of strings in 'Key: Value' format. (Flattened)"
        ),
    )
    positioning_insights: Optional[List[str]] = Field(
        None,
        description=(
            "Positioning insights as a list of strings in 'Key: Value' format. (Flattened)"
        ),
    )
    objections: List[str] = Field(
        ..., description="Common objections and concerns"
    )
    target_customer_insights: Optional[List[str]] = Field(
        None,
        description=(
            "Target customer insights as a list of strings in 'Key: Value' format. (Flattened)"
        ),
    )
    metadata: Dict[str, Any] = Field(
        ..., description="Analysis metadata and quality scores"
    )


class TargetAccountRequest(BaseModel):
    website_url: str = Field(..., description="Company website or landing page URL")
    account_profile_name: Optional[str] = Field(
        None,
        description=(
            "Name of the target account profile "
            "(e.g., 'Mid-market SaaS companies', 'Enterprise healthcare organizations')"
        ),
    )
    hypothesis: Optional[str] = Field(
        None,
        description="User's hypothesis about why this account profile is ideal for the solution",
    )
    additional_context: Optional[str] = Field(
        None,
        description="Additional user-provided context for target account generation",
    )
    company_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Company context from previous endpoints (e.g., company/generate output)",
    )


class CompanySize(BaseModel):
    employees: Optional[str] = Field(
        None, description="Employee count range (e.g., '50-500')"
    )
    department_size: Optional[str] = Field(
        None, description="Relevant department size if applicable"
    )
    revenue: Optional[str] = Field(None, description="Revenue range if relevant")


class Firmographics(BaseModel):
    industry: List[str] = Field(
        ..., description="Exact industry names from Clay taxonomy"
    )
    employees: Optional[str] = Field(None, description="Exact range (e.g., '50-500')")
    department_size: Optional[str] = Field(
        None, description="Relevant dept size if applicable"
    )
    revenue: Optional[str] = Field(None, description="Revenue range if relevant")
    geography: Optional[List[str]] = Field(
        None, description="Geographic markets if relevant"
    )
    business_model: Optional[List[str]] = Field(
        None, description="Clay-searchable business model keywords"
    )
    funding_stage: Optional[List[str]] = Field(
        None, description="Exact funding stage names"
    )
    company_type: Optional[List[str]] = Field(
        None, description="Public/Private/PE-backed etc."
    )
    keywords: List[str] = Field(
        ...,
        description=(
            "3-5 sophisticated company description keywords that indicate implicit need - "
            "avoid obvious solution terms"
        ),
    )


# Enum for BuyingSignal priority
class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class BuyingSignal(BaseModel):
    title: str = Field(..., description="Concise signal name (3-5 words)")
    description: str = Field(
        ...,
        description="1-2 sentences explaining why this signal indicates buying readiness",
    )
    type: str = Field(
        ..., description="Company Data|Website|Tech Stack|News|Social Media|Other"
    )
    priority: PriorityEnum = Field(..., description="Low|Medium|High")
    detection_method: str = Field(
        ...,
        description=("Specific Clay enrichment or data source"),
    )


class ConfidenceAssessment(BaseModel):
    overall_confidence: str = Field(..., description="high|medium|low")
    data_quality: str = Field(..., description="high|medium|low")
    inference_level: str = Field(..., description="minimal|moderate|significant")
    recommended_improvements: List[str] = Field(
        ..., description="What additional data would help"
    )


class ICPMetadata(BaseModel):
    primary_context_source: str = Field(
        ..., description="user_input|company_context|website_content"
    )
    sources_used: List[str] = Field(..., description="List of context sources utilized")
    confidence_assessment: ConfidenceAssessment = Field(
        ..., description="Confidence metrics"
    )
    processing_notes: Optional[str] = Field(
        None, description="Any important notes about analysis approach"
    )


class TargetAccountResponse(BaseModel):
    """
    Response model for the /customers/target_accounts endpoint
    (ICP analysis with Clay-ready filters).
    """

    target_account_name: str = Field(
        ..., description="Short descriptive name for this customer segment"
    )
    target_account_description: str = Field(
        ..., description="1-2 sentences: who they are and why they need this solution"
    )
    target_account_rationale: List[str] = Field(
        ...,
        description="3-5 bullets explaining the overall logic behind these targeting filters",
    )
    firmographics: Firmographics = Field(..., description="Clay-ready prospect filters")
    buying_signals: List[BuyingSignal] = Field(
        ..., description="Detectable buying signals with specific data sources"
    )
    buying_signals_rationale: List[str] = Field(
        ...,
        description=(
            "3-5 bullets explaining the overall logic behind these buying signal choices"
        ),
    )
    metadata: ICPMetadata = Field(
        ...,
        description=("Analysis metadata and quality scores"),
    )


class TargetPersonaRequest(BaseModel):
    website_url: str = Field(..., description="Company website or landing page URL")
    persona_profile_name: Optional[str] = Field(
        None,
        description=(
            "Name of the target persona profile "
            "(e.g., 'VP of Engineering', 'Head of Customer Success', 'IT Director')"
        ),
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
        None,
        description="Structured context about the analyzed company/product",
    )
    target_account_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Target account profile context - the ideal customer company type this persona works for",
    )


class UseCase(BaseModel):
    """Individual use case model for target persona."""

    use_case: str = Field(
        ...,
        description="3-5 word description of the use case or workflow this product impacts",
    )
    pain_points: str = Field(
        ...,
        description="1 sentence description of the pain or inefficiency associated with this pain point",
    )
    capability: str = Field(
        ...,
        description="1 sentence description of the capability the product has that can fix this pain point",
    )
    desired_outcome: str = Field(
        ...,
        description="The desired outcome the persona hopes to achieve using this product",
    )


class Demographics(BaseModel):
    """Demographics model for target persona."""

    job_titles: List[str] = Field(
        ..., description="2-4 likely job titles this person would hold"
    )
    departments: List[str] = Field(
        ..., description="The department(s) they likely belong to"
    )
    seniority: List[str] = Field(
        ...,
        description="Seniority levels: Entry|C-Suite|Senior Manager|Manager|VP|Founder/CEO",
    )
    buying_roles: List[str] = Field(
        ...,
        description="Buying roles: Technical Buyers|Economic Buyers|Decision Maker|Champion|End-User|Blocker|Executive Sponsor|Legal and Compliance|Budget Holder",
    )
    job_description_keywords: List[str] = Field(
        ...,
        description="3-5 key words expected in job description describing day-to-day activities",
    )


class TargetPersonaResponse(BaseModel):
    """
    Response model for the /customers/target_personas endpoint (matches new prompt output).
    """

    target_persona_name: str = Field(
        ..., description="Short descriptive name for this persona segment"
    )
    target_persona_description: str = Field(
        ..., description="1-2 sentences: who they are and why they need this solution"
    )
    target_persona_rationale: List[str] = Field(
        ...,
        description="3-5 bullets explaining the overall logic behind targeting this persona",
    )
    demographics: Demographics = Field(
        ..., description="Demographics and targeting attributes"
    )
    use_cases: List[UseCase] = Field(
        ..., description="3-4 use cases following logical progression"
    )
    buying_signals: List[BuyingSignal] = Field(
        ..., description="Observable buying signals with detection methods"
    )
    buying_signals_rationale: List[str] = Field(
        ..., description="3-5 bullets explaining buying signal logic"
    )
    objections: List[str] = Field(
        ...,
        description="3 bullets summarizing common concerns about adopting this solution",
    )
    goals: List[str] = Field(
        ...,
        description="3-5 bullets explaining business objectives this product can help with",
    )
    purchase_journey: List[str] = Field(
        ...,
        description="3-6 bullet points highlighting path from awareness to purchase",
    )
    metadata: Dict[str, Any] = Field(
        ..., description="Analysis metadata and quality scores"
    )


# Email Generation Schemas
class EmailPreferences(BaseModel):
    """User preferences from the Email Campaign Wizard."""

    use_case: str = Field(..., description="Selected use case ID from persona data")
    emphasis: str = Field(
        ..., description="Emphasis approach: capabilities|pain-point|desired-outcome"
    )
    opening_line: str = Field(
        ...,
        description="Opening line strategy: buying-signal|company-research|not-personalized",
    )
    cta_setting: str = Field(
        ...,
        description="Call-to-action type: feedback|meeting|priority-check|free-resource|visit-link",
    )
    template: str = Field(..., description="Template type: blossomer")
    social_proof: Optional[str] = Field(
        None,
        description="Optional user-provided social proof, testimonials, or case studies to include",
    )


class EmailGenerationRequest(BaseModel):
    """Request model for email generation API."""

    company_context: Optional[Dict[str, Any]] = Field(
        None, description="Company overview from localStorage dashboard_overview"
    )
    target_account: Optional[Dict[str, Any]] = Field(
        None, description="Selected target account from wizard step 1"
    )
    target_persona: Optional[Dict[str, Any]] = Field(
        None, description="Selected target persona from wizard step 1"
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None, description="User preferences from wizard steps 2-3"
    )


class EmailSegment(BaseModel):
    """Individual email segment with type classification."""

    text: str = Field(..., description="The text content of this email segment")
    type: str = Field(
        ...,
        description="Segment type: greeting|opening|pain-point|solution|evidence|cta|signature",
    )


class EmailSubjects(BaseModel):
    """Generated email subjects with primary and alternatives."""

    primary: str = Field(..., description="Most effective subject line")
    alternatives: List[str] = Field(
        ..., description="2 alternative subject lines", min_length=2, max_length=2
    )


# EmailBreakdown is a flexible dictionary structure to match frontend expectations
# Frontend uses: breakdown[segment.type]?.label, breakdown[segment.type]?.description, etc.
EmailBreakdown = Dict[str, Dict[str, str]]


def get_default_email_breakdown() -> EmailBreakdown:
    """
    Returns the default email breakdown structure that matches frontend expectations.
    Each segment type maps to an object with label, description, and color.
    """
    return {
        # Legacy segment types (for backward compatibility)
        "greeting": {
            "label": "Greeting",
            "description": "Standard personalized greeting",
            "color": "bg-purple-100 border-purple-200",
        },
        "opening": {
            "label": "Opening Line",
            "description": "Personalized connection or research-based opener",
            "color": "bg-blue-100 border-blue-200",
        },
        "pain-point": {
            "label": "Pain Point",
            "description": "Challenge or problem being addressed",
            "color": "bg-red-100 border-red-200",
        },
        "solution": {
            "label": "Solution",
            "description": "How your product solves the pain point",
            "color": "bg-green-100 border-green-200",
        },
        "evidence": {
            "label": "Evidence",
            "description": "Proof points or social proof",
            "color": "bg-indigo-100 border-indigo-200",
        },
        "cta": {
            "label": "Call to Action",
            "description": "Next step request",
            "color": "bg-yellow-100 border-yellow-200",
        },
        "signature": {
            "label": "Signature",
            "description": "Professional closing",
            "color": "bg-gray-100 border-gray-200",
        },
        # New Blossomer segment types
        "subject": {
            "label": "Subject Line",
            "description": "Internal memo style, relates to first line",
            "color": "bg-slate-100 border-slate-200",
        },
        "intro": {
            "label": "Opening Line",
            "description": "Personalized reason for outreach",
            "color": "bg-blue-100 border-blue-200",
        },
        "company-intro": {
            "label": "Company Introduction",
            "description": "One-liner with social proof",
            "color": "bg-cyan-100 border-cyan-200",
        },
        "emphasis": {
            "label": "Value Emphasis",
            "description": "Highlighting key capability/outcome",
            "color": "bg-emerald-100 border-emerald-200",
        },
    }


class EmailGenerationMetadata(BaseModel):
    """Metadata about the email generation process."""

    generation_id: str = Field(..., description="Unique identifier for this generation")
    confidence: str = Field(
        ..., description="Confidence level for email quality: high|medium|low"
    )
    personalization_level: str = Field(
        ..., description="Level of personalization achieved: high|medium|low"
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Time taken to generate email in milliseconds"
    )


class EmailGenerationResponse(BaseModel):
    """Response model for email generation API."""

    subjects: EmailSubjects = Field(..., description="Generated subject lines")
    email_body: List[EmailSegment] = Field(
        ..., description="Email content broken into structured segments"
    )
    breakdown: EmailBreakdown = Field(
        ...,
        description="Flexible segment breakdown for UI rendering - maps segment types to {label, description, color}",
    )
    metadata: EmailGenerationMetadata = Field(
        ..., description="Generation metadata and quality metrics"
    )


# Database Model Schemas
# ======================

class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field("user", max_length=20)

class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=20)
    last_login: Optional[datetime] = None

class UserResponse(UserBase):
    """Schema for user responses."""
    id: UUID4
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., max_length=255)
    url: str = Field(..., max_length=500)
    data: Optional[Dict[str, Any]] = None

class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "TechFlow Solutions",
                "url": "https://techflowsolutions.com",
                "data": {
                    "description": "AI-powered workflow automation platform for software teams",
                    "business_profile": {
                        "category": "B2B SaaS workflow automation",
                        "business_model": "Monthly/annual subscriptions with tiered pricing",
                        "existing_customers": "50+ software companies using the platform"
                    },
                    "capabilities": [
                        "Automated code review workflows",
                        "CI/CD pipeline optimization",
                        "Team collaboration tools",
                        "Performance analytics dashboard"
                    ],
                    "positioning": {
                        "key_market_belief": "Manual dev processes are the biggest bottleneck in software delivery",
                        "unique_approach": "AI-driven automation that learns from team patterns"
                    }
                }
            }
        }

class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    name: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "TechFlow Solutions (Updated)",
                "data": {
                    "description": "Updated: AI-powered workflow automation platform for software teams",
                    "last_updated": "2024-Q4"
                }
            }
        }

class CompanyResponse(CompanyBase):
    """Schema for company responses."""
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    """Base account schema."""
    name: str = Field(..., max_length=255)
    data: Dict[str, Any] = Field(..., description="Account data including firmographics, buying signals, rationale, metadata")

class AccountCreate(AccountBase):
    """Schema for creating a new account."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mid-market SaaS Companies",
                "data": {
                    "firmographics": {
                        "industry": ["Software", "SaaS", "Technology"],
                        "employees": "50-500",
                        "revenue": "$5M-$50M",
                        "geography": ["North America", "Europe"],
                        "funding_stage": ["Series A", "Series B", "Series C"],
                        "keywords": ["rapid growth", "scaling team", "CI/CD", "automation", "developer productivity"]
                    },
                    "buying_signals": [
                        {
                            "title": "Recent engineering hiring",
                            "description": "Companies actively hiring developers indicating growth",
                            "type": "Company Data",
                            "priority": "High",
                            "detection_method": "LinkedIn job postings, company announcements"
                        },
                        {
                            "title": "DevOps tool adoption",
                            "description": "Recent adoption of modern development tools",
                            "type": "Tech Stack",
                            "priority": "Medium",
                            "detection_method": "GitHub repos, job descriptions, tech stack data"
                        }
                    ],
                    "rationale": [
                        "Mid-market companies have complex workflows but limited resources",
                        "Growing teams need better automation to maintain velocity",
                        "Budget available for tools that improve developer productivity"
                    ]
                }
            }
        }

class AccountUpdate(BaseModel):
    """Schema for updating account information."""
    name: Optional[str] = Field(None, max_length=255)
    data: Optional[Dict[str, Any]] = None

class AccountResponse(AccountBase):
    """Schema for account responses."""
    id: UUID4
    company_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PersonaBase(BaseModel):
    """Base persona schema."""
    name: str = Field(..., max_length=255)
    data: Dict[str, Any] = Field(..., description="Persona data including demographics, use cases, buying signals, objections, goals")

class PersonaCreate(PersonaBase):
    """Schema for creating a new persona."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "VP of Engineering",
                "data": {
                    "demographics": {
                        "job_titles": ["VP Engineering", "Head of Engineering", "Engineering Director"],
                        "departments": ["Engineering", "Technology"],
                        "seniority": ["VP", "Director", "Senior Manager"],
                        "buying_roles": ["Decision Maker", "Technical Buyer", "Economic Buyer"],
                        "job_description_keywords": ["team leadership", "technical strategy", "developer productivity", "scaling", "automation"]
                    },
                    "use_cases": [
                        {
                            "use_case": "Code review automation",
                            "pain_points": "Manual code reviews slow down development cycles and create bottlenecks",
                            "capability": "AI-powered code review that catches issues early and provides instant feedback",
                            "desired_outcome": "Faster development cycles with maintained code quality"
                        },
                        {
                            "use_case": "CI/CD optimization",
                            "pain_points": "Build pipelines are slow and unreliable, causing deployment delays",
                            "capability": "Intelligent pipeline optimization that reduces build times by 40%",
                            "desired_outcome": "Reliable, fast deployments that don't block development"
                        }
                    ],
                    "goals": [
                        "Improve team productivity and delivery speed",
                        "Reduce technical debt and improve code quality",
                        "Scale engineering processes as team grows",
                        "Minimize time spent on manual, repetitive tasks"
                    ],
                    "objections": [
                        "Concerned about integration complexity with existing tools",
                        "Budget approval process may be lengthy",
                        "Team resistance to changing established workflows"
                    ]
                }
            }
        }

class PersonaUpdate(BaseModel):
    """Schema for updating persona information."""
    name: Optional[str] = Field(None, max_length=255)
    data: Optional[Dict[str, Any]] = None

class PersonaResponse(PersonaBase):
    """Schema for persona responses."""
    id: UUID4
    account_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CampaignBase(BaseModel):
    """Base campaign schema."""
    name: str = Field(..., max_length=255)
    type: str = Field(..., max_length=50, description="Campaign type: email, linkedin, cold_call, ad")
    data: Dict[str, Any] = Field(..., description="Campaign data including subject_line, content, segments, alternatives, configuration")

class CampaignCreate(CampaignBase):
    """Schema for creating a new campaign."""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q4 VP Engineering Outreach",
                "type": "email",
                "data": {
                    "subject_line": "Quick question about your development workflow",
                    "content": "Hi {{name}}, I noticed {{company}} has been growing rapidly...",
                    "segments": [
                        {
                            "type": "greeting",
                            "text": "Hi {{name}}"
                        },
                        {
                            "type": "opening",
                            "text": "I noticed {{company}} has been growing rapidly and hiring more developers"
                        },
                        {
                            "type": "pain-point",
                            "text": "As teams scale, manual code reviews and slow CI/CD pipelines often become major bottlenecks"
                        },
                        {
                            "type": "solution",
                            "text": "TechFlow's AI-powered automation platform helps engineering teams like yours maintain velocity while improving code quality"
                        },
                        {
                            "type": "evidence",
                            "text": "We've helped 50+ similar companies reduce their build times by 40% and speed up code reviews by 60%"
                        },
                        {
                            "type": "cta",
                            "text": "Would you be open to a 15-minute demo to see how this could work for your team?"
                        }
                    ],
                    "alternatives": {
                        "subject_lines": [
                            "Scaling your engineering team at {{company}}?",
                            "How {{company}} can ship code 40% faster"
                        ]
                    },
                    "configuration": {
                        "personalization": "high",
                        "tone": "professional",
                        "length": "short"
                    }
                }
            }
        }

class CampaignUpdate(BaseModel):
    """Schema for updating campaign information."""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    data: Optional[Dict[str, Any]] = None

class CampaignResponse(CampaignBase):
    """Schema for campaign responses."""
    id: UUID4
    account_id: UUID4
    persona_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Extended response schemas with relationships
class CompanyWithRelations(CompanyResponse):
    """Company schema with related accounts."""
    accounts: List[AccountResponse] = []

class AccountWithRelations(AccountResponse):
    """Account schema with related personas and campaigns."""
    personas: List[PersonaResponse] = []
    campaigns: List[CampaignResponse] = []

class PersonaWithRelations(PersonaResponse):
    """Persona schema with related campaigns."""
    campaigns: List[CampaignResponse] = []
