"""
CLI-specific schemas adapted from app/schemas for command-line use.

These schemas remove web-specific fields and add CLI-specific functionality
while maintaining compatibility with the existing generation services.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# CLI Summary Schema (new for terminal display)
class CLISummary(BaseModel):
    """Summary for CLI display."""
    title: str = Field(..., description="Short descriptive title")
    key_points: List[str] = Field(..., description="3-5 key bullet points")
    metrics: Dict[str, str] = Field(default_factory=dict, description="Key metrics/values")


# Request schemas adapted for CLI
class CLIProductOverviewRequest(BaseModel):
    """CLI request for company overview generation."""
    domain: str = Field(..., description="Company domain (e.g., acme.com)")
    website_url: str = Field(..., description="Full website URL") 
    user_context: Optional[str] = Field(None, description="User-provided context")
    
    @classmethod
    def from_domain(cls, domain: str, context: Optional[str] = None) -> 'CLIProductOverviewRequest':
        """Create request from domain and optional context."""
        from cli.utils.domain import normalize_domain
        clean_domain, full_url = normalize_domain(domain)
        return cls(
            domain=clean_domain,
            website_url=full_url,
            user_context=context
        )


class CLITargetAccountRequest(BaseModel):
    """CLI request for target account generation."""
    domain: str = Field(..., description="Company domain")
    website_url: str = Field(..., description="Company website URL")
    account_profile_name: Optional[str] = Field(None, description="Target account profile name")
    hypothesis: Optional[str] = Field(None, description="User hypothesis about ideal accounts")
    additional_context: Optional[str] = Field(None, description="Additional context")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company overview data")


class CLITargetPersonaRequest(BaseModel):
    """CLI request for buyer persona generation."""
    domain: str = Field(..., description="Company domain")
    website_url: str = Field(..., description="Company website URL")
    persona_profile_name: Optional[str] = Field(None, description="Target persona name")
    hypothesis: Optional[str] = Field(None, description="User hypothesis about ideal personas")
    additional_context: Optional[str] = Field(None, description="Additional context")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company overview data")
    target_account_context: Optional[Dict[str, Any]] = Field(None, description="Target account data")


class CLIEmailGenerationRequest(BaseModel):
    """CLI request for email campaign generation."""
    domain: str = Field(..., description="Company domain")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company overview data")
    target_account: Optional[Dict[str, Any]] = Field(None, description="Target account data")
    target_persona: Optional[Dict[str, Any]] = Field(None, description="Target persona data")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Email preferences")


class CLIGTMPlanRequest(BaseModel):
    """CLI request for GTM plan generation."""
    domain: str = Field(..., description="Company domain")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company overview data")
    target_account: Optional[Dict[str, Any]] = Field(None, description="Target account data")
    target_persona: Optional[Dict[str, Any]] = Field(None, description="Target persona data")
    email_campaign: Optional[Dict[str, Any]] = Field(None, description="Email campaign data")


# Response schemas with CLI summaries
class CLIResponse(BaseModel):
    """Base CLI response with summary for terminal display."""
    cli_summary: CLISummary = Field(..., description="Summary for CLI display")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    file_size_bytes: Optional[int] = Field(None, description="Saved file size")
    
    def get_file_size_display(self) -> str:
        """Get human-readable file size."""
        if not self.file_size_bytes:
            return "unknown"
        
        if self.file_size_bytes < 1024:
            return f"{self.file_size_bytes}B"
        elif self.file_size_bytes < 1024 * 1024:
            return f"{self.file_size_bytes / 1024:.1f}KB"
        else:
            return f"{self.file_size_bytes / (1024 * 1024):.1f}MB"


# Project state and metadata
class ProjectState(BaseModel):
    """State of a GTM project."""
    domain: str = Field(..., description="Company domain")
    created_at: datetime = Field(..., description="Creation timestamp")
    modified_at: datetime = Field(..., description="Last modification timestamp")
    steps_completed: List[str] = Field(default_factory=list, description="Completed steps")
    total_steps: int = Field(default=5, description="Total steps in the flow")
    
    @property
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return len(self.steps_completed) >= self.total_steps
    
    @property
    def completion_status(self) -> str:
        """Get completion status string."""
        if self.is_complete:
            return f"✅ Complete ({len(self.steps_completed)}/{self.total_steps})"
        else:
            return f"⚠️  Partial ({len(self.steps_completed)}/{self.total_steps})"
    
    @property
    def missing_steps(self) -> List[str]:
        """Get list of missing steps."""
        all_steps = ["overview", "account", "persona", "email", "strategy"]
        return [step for step in all_steps if step not in self.steps_completed]


class ProjectSummary(BaseModel):
    """Summary of multiple projects for list command."""
    projects: List[ProjectState] = Field(default_factory=list, description="List of projects")
    total_count: int = Field(..., description="Total number of projects")
    complete_count: int = Field(..., description="Number of complete projects")
    
    @classmethod
    def from_projects(cls, projects: List[ProjectState]) -> 'ProjectSummary':
        """Create summary from list of projects."""
        complete_count = sum(1 for p in projects if p.is_complete)
        return cls(
            projects=projects,
            total_count=len(projects),
            complete_count=complete_count
        )


# Command-specific schemas
class InitCommandOptions(BaseModel):
    """Options for the init command."""
    domain: str = Field(..., description="Company domain to analyze")
    context: Optional[str] = Field(None, description="Additional context")
    yolo: bool = Field(default=False, description="Skip interactions")
    overwrite: bool = Field(default=False, description="Overwrite existing project")


class ShowCommandOptions(BaseModel):
    """Options for the show command."""
    domain: Optional[str] = Field(None, description="Project domain")
    asset: str = Field(default="all", description="Asset to show")
    json_output: bool = Field(default=False, description="Output as JSON")
    no_color: bool = Field(default=False, description="Disable colors")


class EditCommandOptions(BaseModel):
    """Options for the edit command."""
    domain: str = Field(..., description="Project domain")
    step: str = Field(..., description="Step to edit")
    editor: Optional[str] = Field(None, description="Editor to use")
    auto_regenerate: bool = Field(default=True, description="Auto-regenerate dependent steps")


# Step configuration
STEP_NAMES = {
    "overview": "Company Overview",
    "account": "Target Account",
    "persona": "Buyer Persona", 
    "email": "Email Campaign",
    "strategy": "GTM Plan"
}

STEP_ICONS = {
    "overview": "🔍",
    "account": "🎯", 
    "persona": "👤",
    "email": "✉️",
    "strategy": "📋"
}

STEP_DEPENDENCIES = {
    "overview": [],
    "account": ["overview"],
    "persona": ["overview", "account"],
    "email": ["overview", "account", "persona"],
    "strategy": ["overview", "account", "persona", "email"]
}


def get_step_display_name(step: str) -> str:
    """Get display name for a step."""
    icon = STEP_ICONS.get(step, "•")
    name = STEP_NAMES.get(step, step.title())
    return f"{icon} {name}"


def get_dependent_steps(step: str) -> List[str]:
    """Get steps that depend on the given step."""
    dependent = []
    for other_step, deps in STEP_DEPENDENCIES.items():
        if step in deps:
            dependent.append(other_step)
    return dependent


# Utility functions for schema conversion
def convert_to_legacy_request(cli_request: CLIProductOverviewRequest) -> Dict[str, Any]:
    """Convert CLI request to legacy API request format."""
    return {
        "website_url": cli_request.website_url,
        "user_inputted_context": cli_request.user_context,
        "company_context": None
    }


# Error schemas
class CLIValidationError(BaseModel):
    """Validation error for CLI."""
    field: str = Field(..., description="Field with error")
    message: str = Field(..., description="Error message")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class CLIErrorResponse(BaseModel):
    """Error response for CLI."""
    error: str = Field(..., description="Error message")
    suggestions: List[str] = Field(default_factory=list, description="Suggested actions")
    exit_code: int = Field(default=1, description="Exit code")