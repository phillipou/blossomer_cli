#!/usr/bin/env python3
"""
Pydantic models for LLM judge responses.
Follows the same patterns as existing app/schemas models.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class JudgeDetail(BaseModel):
    """Base detail for judge evaluation results."""
    
    check_id: str = Field(..., description="Judge check identifier (L-1, L-2, etc.)")
    reason: str = Field(..., description="Explanation of the evaluation result")


class TraceabilityDetail(JudgeDetail):
    """Detail for L-1 traceability check."""
    
    claim_number: int = Field(..., description="Index of the claim being evaluated")
    claim: str = Field(..., description="The actual claim text being evaluated")
    supported: bool = Field(..., description="Whether the claim is properly supported by evidence")


class ActionabilityDetail(JudgeDetail):
    """Detail for L-2 actionability check."""
    
    criterion: Literal["specificity", "discovery_value", "evidence_based"] = Field(
        ..., description="The specific criterion being evaluated"
    )
    pass_: bool = Field(..., alias="pass", description="Whether this criterion passes")


class RedundancyDetail(JudgeDetail):
    """Detail for L-3 redundancy check."""
    
    similarity_score: float = Field(..., description="Jaccard similarity score between sections")


class ContextSteeringDetail(JudgeDetail):
    """Detail for L-4 context steering check."""
    
    context_type: Literal["none", "valid", "noise"] = Field(
        ..., description="Type of context provided"
    )
    appropriate_handling: Optional[bool] = Field(
        None, description="Whether context was handled appropriately"
    )


class JudgeResponse(BaseModel):
    """Base response model for all LLM judges."""
    
    pass_: bool = Field(..., alias="pass", description="Whether the evaluation passes")
    details: List[JudgeDetail] = Field(..., description="Detailed evaluation results")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")


class TraceabilityResponse(JudgeResponse):
    """Response model for L-1 traceability judge."""
    
    details: List[TraceabilityDetail] = Field(..., description="Traceability evaluation details")


class ActionabilityResponse(JudgeResponse):
    """Response model for L-2 actionability judge."""
    
    details: List[ActionabilityDetail] = Field(..., description="Actionability evaluation details")


class RedundancyResponse(JudgeResponse):
    """Response model for L-3 redundancy judge."""
    
    details: List[RedundancyDetail] = Field(..., description="Redundancy evaluation details")


class ContextSteeringResponse(JudgeResponse):
    """Response model for L-4 context steering judge."""
    
    details: List[ContextSteeringDetail] = Field(..., description="Context steering evaluation details")


class JudgeEvaluationResult(BaseModel):
    """Aggregate result from all LLM judges."""
    
    overall_pass: bool = Field(..., description="Whether all judges passed")
    judges: Dict[str, JudgeResponse] = Field(..., description="Results from each judge")
    total_cost_estimate: float = Field(..., description="Total estimated cost for all judge calls")
    judge_calls_made: int = Field(..., description="Number of judge calls made")
    model_used: str = Field(..., description="LLM model used for evaluation")


# Export all models for easy import
__all__ = [
    "JudgeDetail",
    "TraceabilityDetail", 
    "ActionabilityDetail",
    "RedundancyDetail",
    "ContextSteeringDetail",
    "JudgeResponse",
    "TraceabilityResponse",
    "ActionabilityResponse", 
    "RedundancyResponse",
    "ContextSteeringResponse",
    "JudgeEvaluationResult"
]