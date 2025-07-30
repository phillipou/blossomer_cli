# Dynamic Context Architecture

This document describes the new dynamic context management system that replaces static JSON handoffs with intelligent, multi-source context.

## Overview

The Context Store transforms how agents communicate and learn:
- **Before**: Agent A → Static JSON → Agent B
- **After**: Context Store ← Multiple Sources → Enhanced Agents

## Key Components

### 1. Context Store (`app/services/context_store.py`)
- PostgreSQL with JSONB for flexible context storage
- Redis caching for performance
- Handles context updates with approval workflow
- Tracks performance metrics per context version

### 2. Dynamic Context Orchestrator (`app/services/dynamic_context_orchestrator.py`)
- Enhanced orchestrator that injects cross-client patterns
- Extracts insights from agent responses
- Updates context automatically based on agent outputs

### 3. Event Bus (`app/services/context_event_bus.py`)
- Simple pub/sub system for module coordination
- 20 lines of core logic for loose coupling

### 4. Document Processor (`app/services/document_processor.py`)
- Processes weekly snapshots from Google Docs/Notion/Coda
- Classifies documents and extracts actionable insights
- Updates context based on meeting notes and strategy docs

### 5. Performance Tracker (`app/services/performance_tracker.py`)
- Tracks email performance and agent effectiveness
- Generates insights for context improvement
- Identifies cross-client patterns

## Context Update Pathways

### 1. Analysis Agents Processing Real-World Data
```python
# Agent extracts insights from responses
insights = self._extract_insights_from_response(analysis_type, response)
update = ContextUpdate(
    source=ContextUpdateSource.ANALYSIS_AGENT,
    requires_approval=False  # Auto-approve agent insights
)
```

### 2. Direct Human Uploads
```python
# Meeting notes and documents
update = ContextUpdate(
    source=ContextUpdateSource.HUMAN_UPLOAD,
    requires_approval=True  # Human review required
)
```

### 3. Agent Suggestions with Approval
```python
# Performance-based suggestions
update = ContextUpdate(
    source=ContextUpdateSource.AGENT_SUGGESTION,
    requires_approval=True,
    confidence=0.8
)
```

### 4. Cross-Client Pattern Learning
```python
# Anonymized patterns across clients
patterns = await store.get_cross_client_patterns(
    industry="technology",
    company_size="small"
)
```

### 5. Self-Updating Best Practices
```python
# System identifies improvements
update = ContextUpdate(
    source=ContextUpdateSource.BEST_PRACTICE_UPDATE,
    requires_approval=False
)
```

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements-context.txt
```

### 2. Initialize Database
```bash
blossomer context init-db
```

### 3. Run with Dynamic Context
```python
# Agents now automatically use enhanced context
result = await generate_product_overview_service(
    request, 
    client_id="acme_corp",
    use_dynamic_context=True
)
```

### 4. Monitor Context
```bash
# Check context status
blossomer context status acme_corp

# Review pending updates
blossomer context pending-approvals

# Approve updates
blossomer context approve 123 --by="john_doe"
```

## Architecture Benefits

### For 5-6 Client Scale
- **Simple enough**: No over-engineering for boutique scale
- **PostgreSQL**: Proven, reliable data storage
- **Redis caching**: Optional performance boost
- **Human-in-the-loop**: Approval workflow for sensitive updates

### Context Quality
- **Cross-client learning**: Patterns from successful campaigns
- **Performance feedback**: Email metrics improve future generation
- **Document integration**: Weekly snapshots keep context current
- **Agent insights**: Automatic context enrichment

### Privacy & Security
- **Client isolation**: Strict separation of client data
- **Anonymized patterns**: Cross-client learning without data leakage
- **Approval workflow**: Human oversight for sensitive updates

## Technology Stack

- **PostgreSQL + asyncpg**: Core data storage
- **Redis**: Optional caching layer
- **Current LLM integration**: TensorBlock Forge (no changes needed)
- **Event bus**: Simple 20-line pub/sub system

## Migration Path

The system supports gradual migration:

1. **Phase 1**: Run both systems in parallel
2. **Phase 2**: Route specific clients to dynamic context
3. **Phase 3**: Full migration once validated

```python
# Backward compatibility maintained
result = await generate_product_overview_service(
    request,
    use_dynamic_context=False  # Use original system
)
```

## Future Enhancements

- **ML-based pattern detection**: Automatic insight extraction
- **Real-time document sync**: Move beyond weekly snapshots
- **Advanced analytics**: Deeper performance analysis
- **A/B testing framework**: Systematic context optimization

## Implementation Notes

This architecture follows the MVP approach from `phase3_execution_plan.md`:
- **Simple solutions first**: PostgreSQL + Redis over complex frameworks
- **Incremental complexity**: Start simple, add sophistication as needed
- **Real-world validation**: Learn what matters before building complex systems

The foundation is designed to support the full vision while delivering immediate value at boutique scale.