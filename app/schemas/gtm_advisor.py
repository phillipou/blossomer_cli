"""GTM Advisor schema definitions for strategic planning output."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class QualificationCriteria(BaseModel):
    """Gate-keeping attributes for lead qualification."""
    criterion: str = Field(..., description="The qualification criterion name")
    type: str = Field(..., description="Type: 'threshold', 'binary', or 'qualitative'")
    description: str = Field(..., description="What this criterion measures")
    threshold: str = Field(..., description="Specific threshold or requirement")
    detection_method: str = Field(..., description="How to detect this using available tools")


class ScoringSignal(BaseModel):
    """Prioritization attributes for lead scoring."""
    signal: str = Field(..., description="The scoring signal name")
    weight: float = Field(..., description="Point weight for this signal", ge=0, le=100)
    scoring_guide: Dict[str, int] = Field(..., description="Score values for different signal levels")
    rationale: str = Field(..., description="Why this signal is predictive")
    detection_method: str = Field(..., description="How to detect this using available tools")
    detection_tools: List[str] = Field(..., description="Specific tools needed to measure this signal")


class ScoringModel(BaseModel):
    """Base model for lead scoring frameworks."""
    qualification_criteria: List[QualificationCriteria] = Field(..., description="Gate-keeping requirements")
    scoring_signals: List[ScoringSignal] = Field(..., description="Weighted scoring factors")
    total_possible_score: int = Field(..., description="Maximum possible score")
    fit_hypothesis: str = Field(..., description="What makes a lead most likely to convert")
    
    @validator('scoring_signals')
    def validate_weights_sum_to_100(cls, v):
        """Ensure scoring weights sum to exactly 100."""
        total_weight = sum(signal.weight for signal in v)
        if abs(total_weight - 100.0) > 0.01:  # Allow for floating point precision
            raise ValueError(f"Scoring signal weights must sum to 100, got {total_weight}")
        return v


class AccountScoringModel(ScoringModel):
    """Account-level scoring model."""
    company_fit_hypothesis: str = Field(..., description="What makes an account most likely to need this solution")


class ContactScoringModel(ScoringModel):
    """Contact-level scoring model."""  
    persona_fit_hypothesis: str = Field(..., description="What makes a contact most likely to engage and champion")


class ToolRecommendation(BaseModel):
    """Individual tool recommendation."""
    tool_name: str = Field(..., description="Name of the recommended tool")
    category: str = Field(..., description="Tool category")
    description: str = Field(..., description="What the tool does")
    website: str = Field(..., description="Tool website URL")
    phils_notes: Optional[str] = Field(None, description="Phil's specific notes about this tool")
    recommended_by_phil: bool = Field(..., description="Whether Phil explicitly recommends this tool")
    selection_rationale: str = Field(..., description="Why this tool was chosen for this company")
    capabilities_needed: List[str] = Field(..., description="Specific capabilities this tool provides")


class LegoBlock(BaseModel):
    """Individual Lego Block in the email framework."""
    block_number: int = Field(..., description="Block sequence number (0 for subject)")
    block_name: str = Field(..., description="Name of this block")
    purpose: str = Field(..., description="What this block accomplishes")
    example: str = Field(..., description="Example content for this company")
    guidelines: List[str] = Field(..., description="Specific guidelines for this block")


class PrioritizationStrategy(BaseModel):
    """Lead prioritization and effort allocation strategy."""
    top_10_percent: str = Field(..., description="Strategy for highest-scoring leads")
    middle_40_percent: str = Field(..., description="Strategy for mid-tier leads")
    bottom_40_percent: str = Field(..., description="Strategy for lowest-scoring leads") 
    rationale: str = Field(..., description="Why this prioritization approach fits this company")
    scoring_thresholds: Dict[str, int] = Field(..., description="Score ranges for each tier")


class MetricInterpretation(BaseModel):
    """How to interpret a specific metric."""
    signals: str = Field(..., description="What this metric primarily indicates")
    actionable_insights: str = Field(..., description="Specific actions to take based on this metric")
    benchmarks: Optional[Dict[str, str]] = Field(None, description="Performance benchmarks for this metric")
    segmentation_guidance: str = Field(..., description="How to analyze this metric by segment")


class ExecutionSummary(BaseModel):
    """High-level execution guidance and next steps."""
    strategic_focus: str = Field(..., description="Primary strategic recommendation")
    key_hypotheses_to_test: List[str] = Field(..., description="Critical assumptions to validate")
    success_metrics: List[str] = Field(..., description="Key metrics to track")
    timeline_recommendation: str = Field(..., description="Suggested implementation timeline")
    first_90_days: List[str] = Field(..., description="Specific actions for first 90 days")


class EmailVariationAnalysis(BaseModel):
    """Analysis of how email variations differ using Lego Block framework."""
    baseline_description: str = Field(..., description="Description of the baseline email approach")
    variation_description: str = Field(..., description="Description of the email variation approach")
    variable_blocks: List[str] = Field(..., description="Which Lego Blocks vary between baseline and variation")
    constant_blocks: List[str] = Field(..., description="Which Lego Blocks remain consistent")
    hypothesis: str = Field(..., description="What this test will validate about message-market fit")


class ExperimentSetup(BaseModel):
    """Technical setup requirements for A/B testing."""
    sample_size_minimum: int = Field(..., description="Minimum emails per variation")
    test_duration_days: int = Field(..., description="Recommended test duration")
    traffic_split: str = Field(..., description="How to split traffic between variations")
    success_criteria: Dict[str, str] = Field(..., description="Primary and secondary success metrics")
    statistical_requirements: str = Field(..., description="Statistical significance requirements")


class ResultsInterpretation(BaseModel):
    """How to interpret A/B test results."""
    winning_criteria: List[str] = Field(..., description="What defines a winning variation")
    segment_analysis: List[str] = Field(..., description="How to analyze results by segment")
    learning_extraction: List[str] = Field(..., description="What insights to extract from results")
    next_iteration_strategy: Dict[str, str] = Field(..., description="Next steps based on different outcomes")


class EmailExperimentDesign(BaseModel):
    """Complete A/B testing framework for email variations."""
    experiment_available: bool = Field(..., description="Whether email variations are available for testing")
    variation_analysis: Optional[EmailVariationAnalysis] = Field(None, description="Analysis of email variations")
    experiment_setup: Optional[ExperimentSetup] = Field(None, description="Technical testing requirements")
    results_interpretation: Optional[ResultsInterpretation] = Field(None, description="How to interpret results")
    implementation_guidance: Optional[str] = Field(None, description="Step-by-step implementation guidance")


class GTMAdvisorOutput(BaseModel):
    """Complete GTM strategic plan output."""
    
    # Core scoring models
    account_scoring_model: AccountScoringModel = Field(..., description="Account-level lead scoring framework")
    contact_scoring_model: ContactScoringModel = Field(..., description="Contact-level lead scoring framework")
    
    # Tool recommendations
    tool_stack_recommendations: Dict[str, ToolRecommendation] = Field(
        ..., 
        description="Recommended tools by category (9 categories required)"
    )
    
    # Methodology frameworks
    lego_block_framework: List[LegoBlock] = Field(..., description="Customized Lego Block email framework")
    prioritization_strategy: PrioritizationStrategy = Field(..., description="Lead prioritization approach")
    
    # Analytics and optimization
    metrics_interpretation_guide: Dict[str, MetricInterpretation] = Field(
        ..., 
        description="How to interpret key metrics"
    )
    
    # Email experiment design
    email_experiment_design: EmailExperimentDesign = Field(..., description="A/B testing framework for email variations")
    
    # Strategic guidance
    execution_summary: ExecutionSummary = Field(..., description="High-level execution plan")
    
    # Metadata
    generated_for_company: str = Field(..., description="Company this plan was created for")
    methodology_version: str = Field(default="blossomer_v1", description="Methodology version used")
    
    @validator('tool_stack_recommendations')
    def validate_required_categories(cls, v):
        """Ensure all 9 required tool categories are present."""
        required_categories = {
            "CRM", "Outreach (Email)", "Outreach (LinkedIn)", 
            "Contact Verification", "Account Data", "Persona Data",
            "Buying Signals", "Email Infrastructure", "Orchestration"
        }
        
        provided_categories = set()
        for tool in v.values():
            # Handle multi-category tools
            categories = [cat.strip() for cat in tool.category.split(",")]
            provided_categories.update(categories)
        
        missing_categories = required_categories - provided_categories
        if missing_categories:
            raise ValueError(f"Missing required tool categories: {missing_categories}")
        
        return v
    
    @validator('lego_block_framework') 
    def validate_lego_blocks(cls, v):
        """Ensure all required Lego Blocks are present."""
        required_blocks = {"Subject", "Intro", "Pain Point", "Company Intro", "Emphasis", "CTA"}
        provided_blocks = {block.block_name for block in v}
        
        missing_blocks = required_blocks - provided_blocks
        if missing_blocks:
            raise ValueError(f"Missing required Lego Blocks: {missing_blocks}")
            
        return v


# Convenience classes for specific use cases
class GTMScoringFramework(BaseModel):
    """Combined scoring framework for both accounts and contacts."""
    account_model: AccountScoringModel
    contact_model: ContactScoringModel
    
    def get_total_signals(self) -> int:
        """Get total number of scoring signals across both models."""
        return len(self.account_model.scoring_signals) + len(self.contact_model.scoring_signals)
    
    def get_all_detection_tools(self) -> List[str]:
        """Get all unique tools needed for detection across both models."""
        tools = set()
        for signal in self.account_model.scoring_signals:
            tools.update(signal.detection_tools)
        for signal in self.contact_model.scoring_signals:
            tools.update(signal.detection_tools)
        return sorted(list(tools))


class ToolStackAnalysis(BaseModel):
    """Analysis of the recommended tool stack."""
    total_tools: int
    tools_by_category: Dict[str, List[str]]
    phil_recommended_count: int
    estimated_monthly_cost: Optional[str] = None
    integration_complexity: str
    
    @classmethod
    def from_recommendations(cls, recommendations: Dict[str, ToolRecommendation]) -> "ToolStackAnalysis":
        """Create analysis from tool recommendations."""
        tools_by_category = {}
        phil_count = 0
        
        for tool in recommendations.values():
            if tool.recommended_by_phil:
                phil_count += 1
            
            categories = [cat.strip() for cat in tool.category.split(",")]
            for category in categories:
                if category not in tools_by_category:
                    tools_by_category[category] = []
                tools_by_category[category].append(tool.tool_name)
        
        return cls(
            total_tools=len(recommendations),
            tools_by_category=tools_by_category,
            phil_recommended_count=phil_count,
            integration_complexity="Medium" if len(recommendations) > 6 else "Low"
        )