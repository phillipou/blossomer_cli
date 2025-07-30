"""
Document Snapshot Processor
Handles weekly snapshots from Google Docs, Notion, Coda
Extracts insights and updates context store
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from app.services.context_store import get_context_store, ContextUpdate, ContextUpdateSource
from app.services.context_event_bus import event_bus, ContextEvent

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents we can process"""
    MEETING_NOTES = "meeting_notes"
    STRATEGY_DOC = "strategy_doc"
    COMPETITIVE_INTEL = "competitive_intel"
    CUSTOMER_FEEDBACK = "customer_feedback"
    PRODUCT_SPEC = "product_spec"
    SALES_PLAYBOOK = "sales_playbook"
    OTHER = "other"


@dataclass
class DocumentSnapshot:
    """Represents a document snapshot from external tools"""
    source_tool: str  # "google_docs", "notion", "coda"
    document_id: str
    title: str
    content: str
    content_hash: str
    last_modified: datetime
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.md5(self.content.encode()).hexdigest()


@dataclass
class DocumentInsight:
    """Extracted insight from document processing"""
    insight_type: str
    content: str
    confidence: float
    source_section: str
    requires_approval: bool = True


class DocumentSnapshotProcessor:
    """
    Processes weekly snapshots from collaborative tools
    Classifies documents and extracts actionable insights
    """
    
    def __init__(self):
        self.previous_snapshots: Dict[str, DocumentSnapshot] = {}
    
    async def process_weekly_snapshot(
        self, 
        client_id: str, 
        documents: List[DocumentSnapshot]
    ) -> Dict[str, Any]:
        """
        Process a weekly snapshot of documents
        Returns summary of changes and extracted insights
        """
        results = {
            "client_id": client_id,
            "processed_at": datetime.now(),
            "total_documents": len(documents),
            "new_documents": 0,
            "modified_documents": 0,
            "insights_extracted": 0,
            "context_updates": 0,
            "documents": []
        }
        
        context_store = await get_context_store()
        
        for doc in documents:
            doc_result = await self._process_single_document(client_id, doc, context_store)
            results["documents"].append(doc_result)
            
            if doc_result["status"] == "new":
                results["new_documents"] += 1
            elif doc_result["status"] == "modified":
                results["modified_documents"] += 1
            
            results["insights_extracted"] += len(doc_result["insights"])
            results["context_updates"] += len(doc_result["context_updates"])
        
        # Publish summary event
        await event_bus.publish(ContextEvent(
            event_type="documents_processed",
            client_id=client_id,
            agent_type="document_processor",
            data={
                "summary": results,
                "document_count": len(documents)
            }
        ))
        
        logger.info(f"Processed {len(documents)} documents for {client_id}: "
                   f"{results['new_documents']} new, {results['modified_documents']} modified")
        
        return results
    
    async def _process_single_document(
        self, 
        client_id: str, 
        doc: DocumentSnapshot,
        context_store
    ) -> Dict[str, Any]:
        """Process a single document and extract insights"""
        
        doc_key = f"{client_id}:{doc.source_tool}:{doc.document_id}"
        previous_doc = self.previous_snapshots.get(doc_key)
        
        # Determine if this is new or modified
        status = "unchanged"
        if not previous_doc:
            status = "new"
        elif previous_doc.content_hash != doc.content_hash:
            status = "modified"
        
        result = {
            "document_id": doc.document_id,
            "title": doc.title,
            "source_tool": doc.source_tool,
            "status": status,
            "insights": [],
            "context_updates": []
        }
        
        # Only process new or modified documents
        if status in ["new", "modified"]:
            # Classify document type
            doc_type = self._classify_document(doc)
            
            # Extract insights based on document type
            insights = await self._extract_insights(doc, doc_type, previous_doc)
            result["insights"] = [
                {
                    "type": insight.insight_type,
                    "content": insight.content,
                    "confidence": insight.confidence,
                    "requires_approval": insight.requires_approval
                }
                for insight in insights
            ]
            
            # Create context updates from insights
            for insight in insights:
                if insight.confidence > 0.6:  # Only high-confidence insights
                    update = ContextUpdate(
                        client_id=client_id,
                        source=ContextUpdateSource.HUMAN_UPLOAD,
                        agent_type=self._map_insight_to_agent(insight.insight_type),
                        update_data={
                            "insight_type": insight.insight_type,
                            "content": insight.content,
                            "source_document": doc.title,
                            "source_section": insight.source_section,
                            "extracted_at": datetime.now().isoformat()
                        },
                        confidence=insight.confidence,
                        requires_approval=insight.requires_approval,
                        created_at=datetime.now()
                    )
                    
                    success = await context_store.update_context(update)
                    result["context_updates"].append({
                        "insight_type": insight.insight_type,
                        "applied_immediately": success,
                        "requires_approval": insight.requires_approval
                    })
            
            # Update our snapshot cache
            self.previous_snapshots[doc_key] = doc
        
        return result
    
    def _classify_document(self, doc: DocumentSnapshot) -> DocumentType:
        """Classify document type based on title and content"""
        
        title_lower = doc.title.lower()
        content_sample = doc.content[:500].lower()
        
        # Simple keyword-based classification
        if any(keyword in title_lower for keyword in ["meeting", "notes", "standup", "sync"]):
            return DocumentType.MEETING_NOTES
        elif any(keyword in title_lower for keyword in ["strategy", "roadmap", "plan"]):
            return DocumentType.STRATEGY_DOC
        elif any(keyword in title_lower for keyword in ["competitor", "competitive", "market analysis"]):
            return DocumentType.COMPETITIVE_INTEL
        elif any(keyword in title_lower for keyword in ["feedback", "customer", "user research"]):
            return DocumentType.CUSTOMER_FEEDBACK
        elif any(keyword in title_lower for keyword in ["spec", "requirements", "product"]):
            return DocumentType.PRODUCT_SPEC
        elif any(keyword in title_lower for keyword in ["sales", "playbook", "pitch"]):
            return DocumentType.SALES_PLAYBOOK
        else:
            return DocumentType.OTHER
    
    async def _extract_insights(
        self, 
        doc: DocumentSnapshot, 
        doc_type: DocumentType,
        previous_doc: Optional[DocumentSnapshot]
    ) -> List[DocumentInsight]:
        """Extract actionable insights from document content"""
        
        insights = []
        
        # For demo purposes, use simple keyword extraction
        # In production, this would use LLM-based extraction
        
        content = doc.content.lower()
        
        if doc_type == DocumentType.MEETING_NOTES:
            insights.extend(self._extract_meeting_insights(doc, content))
        elif doc_type == DocumentType.STRATEGY_DOC:
            insights.extend(self._extract_strategy_insights(doc, content))
        elif doc_type == DocumentType.CUSTOMER_FEEDBACK:
            insights.extend(self._extract_feedback_insights(doc, content))
        elif doc_type == DocumentType.COMPETITIVE_INTEL:
            insights.extend(self._extract_competitive_insights(doc, content))
        
        return insights
    
    def _extract_meeting_insights(self, doc: DocumentSnapshot, content: str) -> List[DocumentInsight]:
        """Extract insights from meeting notes"""
        insights = []
        
        # Look for action items and decisions
        if "action item" in content or "todo" in content:
            insights.append(DocumentInsight(
                insight_type="action_items",
                content="Meeting contained action items",
                confidence=0.8,
                source_section="meeting_notes",
                requires_approval=False
            ))
        
        # Look for customer mentions
        if any(word in content for word in ["customer", "client", "user"]):
            insights.append(DocumentInsight(
                insight_type="customer_mention",
                content="Customer feedback or discussion noted",
                confidence=0.7,
                source_section="meeting_notes",
                requires_approval=True
            ))
        
        return insights
    
    def _extract_strategy_insights(self, doc: DocumentSnapshot, content: str) -> List[DocumentInsight]:
        """Extract insights from strategy documents"""
        insights = []
        
        # Look for target market changes
        if any(word in content for word in ["target market", "icp", "ideal customer"]):
            insights.append(DocumentInsight(
                insight_type="target_market_update",
                content="Target market or ICP discussion found",
                confidence=0.9,
                source_section="strategy_doc",
                requires_approval=True
            ))
        
        # Look for positioning changes
        if any(word in content for word in ["positioning", "value prop", "messaging"]):
            insights.append(DocumentInsight(
                insight_type="positioning_update",
                content="Positioning or messaging discussion found",
                confidence=0.8,
                source_section="strategy_doc",
                requires_approval=True
            ))
        
        return insights
    
    def _extract_feedback_insights(self, doc: DocumentSnapshot, content: str) -> List[DocumentInsight]:
        """Extract insights from customer feedback"""
        insights = []
        
        # Look for pain points
        if any(word in content for word in ["pain", "problem", "challenge", "frustration"]):
            insights.append(DocumentInsight(
                insight_type="pain_point",
                content="Customer pain point identified",
                confidence=0.8,
                source_section="customer_feedback",
                requires_approval=True
            ))
        
        # Look for positive feedback
        if any(word in content for word in ["love", "great", "excellent", "positive"]):
            insights.append(DocumentInsight(
                insight_type="positive_feedback",
                content="Positive customer feedback noted",
                confidence=0.7,
                source_section="customer_feedback",
                requires_approval=False
            ))
        
        return insights
    
    def _extract_competitive_insights(self, doc: DocumentSnapshot, content: str) -> List[DocumentInsight]:
        """Extract insights from competitive intelligence"""
        insights = []
        
        # Look for competitor mentions
        if any(word in content for word in ["competitor", "competitive", "vs.", "versus"]):
            insights.append(DocumentInsight(
                insight_type="competitive_update",
                content="Competitive intelligence update",
                confidence=0.8,
                source_section="competitive_intel",
                requires_approval=True
            ))
        
        return insights
    
    def _map_insight_to_agent(self, insight_type: str) -> str:
        """Map insight types to agent types for context updates"""
        
        mapping = {
            "target_market_update": "target_account",
            "positioning_update": "product_overview",
            "pain_point": "target_persona",
            "customer_mention": "target_persona",
            "competitive_update": "product_overview",
            "positive_feedback": "email_generation",
            "action_items": "product_overview"
        }
        
        return mapping.get(insight_type, "product_overview")


# Demo function for testing
async def demo_document_processing():
    """Demo function to test document processing"""
    
    processor = DocumentSnapshotProcessor()
    
    # Create sample documents
    documents = [
        DocumentSnapshot(
            source_tool="google_docs",
            document_id="doc_123",
            title="Weekly Customer Sync Notes",
            content="""
            Meeting Notes - Customer Sync
            Date: 2025-01-15
            
            Key Discussion Points:
            - Customer feedback on new feature
            - Pain point: current integration is too complex
            - Action item: simplify onboarding flow
            - Positive feedback on customer support
            """,
            content_hash="",
            last_modified=datetime.now()
        ),
        DocumentSnapshot(
            source_tool="notion",
            document_id="notion_456",
            title="Q1 Strategy Update",
            content="""
            Q1 Strategy Document
            
            Target Market Updates:
            - Expanding ICP to include mid-market companies
            - New positioning around ease of use
            - Value prop emphasis on ROI and time savings
            """,
            content_hash="",
            last_modified=datetime.now()
        )
    ]
    
    # Process documents
    results = await processor.process_weekly_snapshot("demo_client", documents)
    
    print(f"Processing Results:")
    print(f"- Total documents: {results['total_documents']}")
    print(f"- New documents: {results['new_documents']}")
    print(f"- Insights extracted: {results['insights_extracted']}")
    print(f"- Context updates: {results['context_updates']}")
    
    for doc_result in results["documents"]:
        print(f"\nDocument: {doc_result['title']}")
        print(f"Status: {doc_result['status']}")
        print(f"Insights: {len(doc_result['insights'])}")
        for insight in doc_result["insights"]:
            print(f"  - {insight['type']}: {insight['content']} (confidence: {insight['confidence']})")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_document_processing())