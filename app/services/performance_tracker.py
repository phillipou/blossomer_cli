"""
Performance Tracking Module
Tracks email performance, agent effectiveness, and context quality
Feeds insights back to context store for continuous improvement
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from app.services.context_store import get_context_store, ContextUpdate, ContextUpdateSource
from app.services.context_event_bus import event_bus, ContextEvent

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics we track"""
    EMAIL_OPEN_RATE = "email_open_rate"
    EMAIL_REPLY_RATE = "email_reply_rate"
    EMAIL_MEETING_RATE = "email_meeting_rate"
    AGENT_CONFIDENCE = "agent_confidence"
    CONTEXT_QUALITY = "context_quality"
    GENERATION_TIME = "generation_time"
    USER_SATISFACTION = "user_satisfaction"


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    client_id: str
    agent_type: str
    metric_type: MetricType
    metric_value: float
    context_version: int
    recorded_at: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmailPerformanceData:
    """Email campaign performance data"""
    client_id: str
    campaign_id: str
    email_variant: str
    subject_line: str
    sent_count: int
    opened_count: int
    replied_count: int
    meeting_booked_count: int
    context_version: int
    sent_at: datetime


class PerformanceTracker:
    """
    Tracks performance metrics and feeds insights back to context store
    Enables continuous improvement through data-driven context updates
    """
    
    def __init__(self):
        self.metrics_cache = []
    
    async def track_email_performance(
        self, 
        email_data: EmailPerformanceData
    ) -> None:
        """Track email campaign performance and update context"""
        
        context_store = await get_context_store()
        
        # Calculate performance rates
        open_rate = email_data.opened_count / email_data.sent_count if email_data.sent_count > 0 else 0
        reply_rate = email_data.replied_count / email_data.sent_count if email_data.sent_count > 0 else 0
        meeting_rate = email_data.meeting_booked_count / email_data.sent_count if email_data.sent_count > 0 else 0
        
        # Track individual metrics
        await context_store.track_performance(
            email_data.client_id, 
            "email_generation", 
            MetricType.EMAIL_OPEN_RATE.value, 
            open_rate
        )
        
        await context_store.track_performance(
            email_data.client_id, 
            "email_generation", 
            MetricType.EMAIL_REPLY_RATE.value, 
            reply_rate
        )
        
        await context_store.track_performance(
            email_data.client_id, 
            "email_generation", 
            MetricType.EMAIL_MEETING_RATE.value, 
            meeting_rate
        )
        
        # Analyze performance and create context updates
        insights = await self._analyze_email_performance(email_data, open_rate, reply_rate, meeting_rate)
        
        for insight in insights:
            update = ContextUpdate(
                client_id=email_data.client_id,
                source=ContextUpdateSource.AGENT_SUGGESTION,
                agent_type=insight["agent_type"],
                update_data=insight["data"],
                confidence=insight["confidence"],
                requires_approval=insight["requires_approval"],
                created_at=datetime.now()
            )
            
            await context_store.update_context(update)
        
        # Publish performance event
        await event_bus.publish(ContextEvent(
            event_type="email_performance_tracked",
            client_id=email_data.client_id,
            agent_type="email_generation",
            data={
                "campaign_id": email_data.campaign_id,
                "open_rate": open_rate,
                "reply_rate": reply_rate,
                "meeting_rate": meeting_rate,
                "insights_generated": len(insights)
            }
        ))
        
        logger.info(f"Tracked email performance for {email_data.client_id}: "
                   f"open={open_rate:.1%}, reply={reply_rate:.1%}, meeting={meeting_rate:.1%}")
    
    async def track_agent_performance(
        self,
        client_id: str,
        agent_type: str,
        confidence_score: float,
        generation_time: float,
        user_feedback: Optional[float] = None
    ) -> None:
        """Track agent performance metrics"""
        
        context_store = await get_context_store()
        
        # Track confidence score
        await context_store.track_performance(
            client_id, 
            agent_type, 
            MetricType.AGENT_CONFIDENCE.value, 
            confidence_score
        )
        
        # Track generation time
        await context_store.track_performance(
            client_id, 
            agent_type, 
            MetricType.GENERATION_TIME.value, 
            generation_time
        )
        
        # Track user feedback if provided
        if user_feedback is not None:
            await context_store.track_performance(
                client_id, 
                agent_type, 
                MetricType.USER_SATISFACTION.value, 
                user_feedback
            )
        
        # Analyze agent performance trends
        insights = await self._analyze_agent_performance(client_id, agent_type, confidence_score)
        
        for insight in insights:
            update = ContextUpdate(
                client_id=client_id,
                source=ContextUpdateSource.AGENT_SUGGESTION,
                agent_type=agent_type,
                update_data=insight["data"],
                confidence=insight["confidence"],
                requires_approval=insight["requires_approval"],
                created_at=datetime.now()
            )
            
            await context_store.update_context(update)
        
        logger.debug(f"Tracked agent performance for {client_id}/{agent_type}: "
                    f"confidence={confidence_score:.2f}, time={generation_time:.1f}s")
    
    async def _analyze_email_performance(
        self, 
        email_data: EmailPerformanceData,
        open_rate: float,
        reply_rate: float,
        meeting_rate: float
    ) -> List[Dict[str, Any]]:
        """Analyze email performance and generate insights"""
        
        insights = []
        
        # High-performing subject line insight
        if open_rate > 0.3:  # 30% open rate is good
            insights.append({
                "agent_type": "email_generation",
                "data": {
                    "insight_type": "high_performing_subject",
                    "subject_pattern": email_data.subject_line,
                    "open_rate": open_rate,
                    "recommendation": "Consider similar subject line patterns"
                },
                "confidence": 0.8,
                "requires_approval": False
            })
        
        # High-performing email content insight
        if reply_rate > 0.05:  # 5% reply rate is good
            insights.append({
                "agent_type": "email_generation",
                "data": {
                    "insight_type": "high_performing_content",
                    "reply_rate": reply_rate,
                    "email_variant": email_data.email_variant,
                    "recommendation": "Content style is effective"
                },
                "confidence": 0.7,
                "requires_approval": False
            })
        
        # Low performance warning
        if open_rate < 0.1 and email_data.sent_count > 50:  # Low open rate with significant sample
            insights.append({
                "agent_type": "email_generation",
                "data": {
                    "insight_type": "low_open_rate_warning",
                    "open_rate": open_rate,
                    "subject_line": email_data.subject_line,
                    "recommendation": "Consider revising subject line approach"
                },
                "confidence": 0.9,
                "requires_approval": True
            })
        
        return insights
    
    async def _analyze_agent_performance(
        self,
        client_id: str,
        agent_type: str,
        current_confidence: float
    ) -> List[Dict[str, Any]]:
        """Analyze agent performance trends"""
        
        insights = []
        
        # Low confidence warning
        if current_confidence < 0.6:
            insights.append({
                "agent_type": agent_type,
                "data": {
                    "insight_type": "low_confidence_warning",
                    "confidence_score": current_confidence,
                    "recommendation": "Agent may need additional context or prompt tuning"
                },
                "confidence": 0.8,
                "requires_approval": True
            })
        
        # High confidence insight
        if current_confidence > 0.9:
            insights.append({
                "agent_type": agent_type,
                "data": {
                    "insight_type": "high_confidence_pattern",
                    "confidence_score": current_confidence,
                    "recommendation": "Current context configuration is working well"
                },
                "confidence": 0.7,
                "requires_approval": False
            })
        
        return insights
    
    async def generate_performance_report(
        self, 
        client_id: str, 
        days: int = 7
    ) -> Dict[str, Any]:
        """Generate performance report for the last N days"""
        
        # This would query the performance tables in the context store
        # For now, return a mock report structure
        
        report = {
            "client_id": client_id,
            "report_period_days": days,
            "generated_at": datetime.now(),
            "email_performance": {
                "total_campaigns": 5,
                "avg_open_rate": 0.25,
                "avg_reply_rate": 0.08,
                "avg_meeting_rate": 0.02,
                "best_performing_subject": "Quick question about [Company]",
                "worst_performing_subject": "Partnership opportunity"
            },
            "agent_performance": {
                "product_overview": {
                    "avg_confidence": 0.85,
                    "avg_generation_time": 12.3,
                    "user_satisfaction": 4.2
                },
                "target_account": {
                    "avg_confidence": 0.78,
                    "avg_generation_time": 8.7,
                    "user_satisfaction": 4.0
                },
                "target_persona": {
                    "avg_confidence": 0.82,
                    "avg_generation_time": 10.1,
                    "user_satisfaction": 4.1
                },
                "email_generation": {
                    "avg_confidence": 0.79,
                    "avg_generation_time": 15.2,
                    "user_satisfaction": 3.9
                }
            },
            "recommendations": [
                "Email generation agent could benefit from more context about customer pain points",
                "Subject line patterns with questions are performing well",
                "Target account agent confidence is lower than other agents"
            ]
        }
        
        return report
    
    async def track_cross_client_patterns(self) -> None:
        """Analyze patterns across all clients and update global insights"""
        
        # This would analyze performance across all clients to identify patterns
        # that could benefit other clients
        
        context_store = await get_context_store()
        
        # Mock pattern analysis
        patterns = [
            {
                "pattern_type": "high_performing_subject_pattern",
                "industry": "technology",
                "company_size_bucket": "small",
                "pattern_data": {
                    "description": "Questions about specific company initiatives",
                    "example": "Quick question about [Company]'s [Initiative]",
                    "success_factors": ["personalization", "brevity", "question_format"]
                },
                "success_rate": 0.32,
                "sample_size": 150,
                "confidence_score": 0.85
            }
        ]
        
        # In a real implementation, this would:
        # 1. Query performance data across all clients
        # 2. Use ML to identify successful patterns
        # 3. Anonymize and store as cross-client insights
        
        logger.info(f"Analyzed cross-client patterns: {len(patterns)} patterns identified")


# Demo function
async def demo_performance_tracking():
    """Demo function to test performance tracking"""
    
    tracker = PerformanceTracker()
    
    # Simulate email performance data
    email_data = EmailPerformanceData(
        client_id="demo_client",
        campaign_id="campaign_123",
        email_variant="variant_a",
        subject_line="Quick question about Acme Corp's scaling challenges",
        sent_count=100,
        opened_count=32,
        replied_count=8,
        meeting_booked_count=3,
        context_version=1,
        sent_at=datetime.now() - timedelta(days=1)
    )
    
    # Track email performance
    await tracker.track_email_performance(email_data)
    
    # Track agent performance
    await tracker.track_agent_performance(
        client_id="demo_client",
        agent_type="email_generation",
        confidence_score=0.85,
        generation_time=12.5,
        user_feedback=4.2
    )
    
    # Generate report
    report = await tracker.generate_performance_report("demo_client", days=7)
    
    print("Performance Report:")
    print(f"Email Performance: {report['email_performance']['avg_open_rate']:.1%} open rate")
    print(f"Agent Performance: {len(report['agent_performance'])} agents tracked")
    print(f"Recommendations: {len(report['recommendations'])} generated")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_performance_tracking())