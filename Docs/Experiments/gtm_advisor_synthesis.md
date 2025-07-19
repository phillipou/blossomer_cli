# GTM Advisor - Strategic Synthesis & Planning

## Context
The Blossomer GTM CLI generates individual GTM assets through a 5-step process: Company Overview → Target Account → Buyer Persona → Email Campaign → Export. While each output is valuable, users currently lack a synthesized strategic plan that ties everything together. They need actionable guidance on lead scoring, prospecting tools, email sequencing, and success metrics to execute their GTM strategy effectively.

## Goals
1. **Synthesize all outputs** into a cohesive GTM execution plan
2. **Provide lead scoring framework** based on ICP characteristics
3. **Recommend specific tools & APIs** for prospecting and buying signals
4. **Design email sequencing strategy** with timing and triggers
5. **Define success metrics** and KPIs for GTM execution
6. **Create actionable 30/60/90 day plan** with clear milestones

## Design

### Architecture
```
GTM Advisor Service (New Step 6)
    ├── Inputs: All previous outputs (Overview, ICP, Persona, Emails)
    ├── LLM Analysis: Synthesis + Strategic Planning
    └── Output: Comprehensive GTM Plan {
            lead_scoring: {...},
            prospecting_tools: {...},
            email_sequence: {...},
            metrics: {...},
            execution_timeline: {...}
        }
```

### Key Components

#### 1. Lead Scoring Framework
- Firmographic fit score (company size, industry, tech stack)
- Behavioral signals (website visits, content engagement)
- Buying intent indicators (job postings, funding, tool adoption)
- Weighted scoring model with thresholds

#### 2. Tool Recommendations
- **Prospecting Tools**: Apollo, Clay, Instantly, etc.
- **Intent Data**: 6sense, Bombora, G2 intent
- **Enrichment APIs**: Clearbit, ZoomInfo, FullContact
- **Automation**: Zapier, Make, n8n integrations

#### 3. Email Sequencing Strategy
- Initial email → Follow-up timing
- Multi-thread approach (multiple personas)
- Trigger-based sequences (engagement, events)
- A/B testing recommendations

#### 4. Success Metrics
- Leading indicators (emails sent, opens, replies)
- Pipeline metrics (meetings booked, opportunities created)
- Conversion benchmarks by industry/persona
- Optimization recommendations

## Implementation Plan

### Task 1: Create GTM Advisor Prompt Template
**File**: `/app/prompts/templates/gtm_advisor.jinja2`

**Subtasks**:
1. **Design comprehensive prompt structure**
   - System prompt with synthesis instructions
   - Sections for each planning component
   - Chain-of-thought reasoning guides
   
2. **Create input aggregation logic**
   - Pull insights from all previous outputs
   - Structure data for LLM consumption
   - Highlight key findings to synthesize

3. **Define output JSON schema**
   - Lead scoring rubric structure
   - Tool recommendation format
   - Sequence planning schema
   - Metrics and timeline structure

4. **Add industry-specific guidance**
   - Tailor recommendations by vertical
   - Include relevant benchmarks
   - Suggest specialized tools

### Task 2: Create GTM Advisor Schema
**File**: `/app/schemas/gtm_advisor.py`

**Subtasks**:
1. **Define core models**
   ```python
   class LeadScoringCriteria(BaseModel):
       criterion: str
       weight: float
       scoring_guide: Dict[str, int]
   
   class ToolRecommendation(BaseModel):
       category: str
       tool_name: str
       purpose: str
       pricing_tier: str
       integration_notes: str
   
   class EmailSequenceStep(BaseModel):
       day: int
       action: str
       channel: str
       trigger: Optional[str]
       content_theme: str
   ```

2. **Create output model**
   ```python
   class GTMAdvisorOutput(BaseModel):
       lead_scoring: LeadScoringFramework
       prospecting_tools: List[ToolRecommendation]
       email_sequence: EmailSequencePlan
       success_metrics: MetricsFramework
       execution_timeline: ExecutionPlan
   ```

3. **Add validation logic**
   - Ensure scoring weights sum to 100%
   - Validate timeline milestones
   - Check tool category completeness

### Task 3: Create GTM Advisor Service
**File**: `/app/services/gtm_advisor_service.py`

**Subtasks**:
1. **Implement data aggregation**
   ```python
   async def aggregate_gtm_data(self, domain: str):
       # Load all previous outputs
       overview = self.load_output("company_overview.json")
       icp = self.load_output("target_account.json")
       persona = self.load_output("target_persona.json")
       emails = self.load_output("email_campaign.json")
       return self.structure_for_synthesis(...)
   ```

2. **Create synthesis logic**
   - Extract key insights from each output
   - Identify patterns and connections
   - Build comprehensive context

3. **Implement LLM orchestration**
   - Use TemplateRunner for prompt execution
   - Handle large context windows
   - Implement retry logic

4. **Add output post-processing**
   - Validate tool recommendations exist
   - Ensure timeline is realistic
   - Format for display

### Task 4: Create GTM Advisor CLI Command
**File**: `/cli/commands/gtm_advisor.py`

**Subtasks**:
1. **Create standalone command**
   ```python
   @app.command()
   def advisor(
       domain: str = typer.Argument(...),
       regenerate: bool = typer.Option(False)
   ):
       """Generate strategic GTM plan from analysis"""
   ```

2. **Implement interactive flow**
   - Check for required dependencies
   - Show synthesis progress
   - Allow section regeneration

3. **Add rich terminal display**
   - Formatted scoring rubric
   - Tool comparison table
   - Timeline visualization
   - Metrics dashboard

### Task 5: Integrate into Main Flow
**File**: `/cli/commands/init_sync.py`

**Subtasks**:
1. **Add as Step 6**
   - Update progress indicators
   - Add to step navigation
   - Handle dependencies

2. **Update workflow logic**
   - Make advisor optional initially
   - Add skip/regenerate options
   - Update completion messages

3. **Modify state management**
   - Track advisor completion
   - Update project metadata
   - Handle rollback scenarios

### Task 6: Update Export Functionality
**Files**: `/cli/commands/export.py`, `/cli/utils/markdown_export.py`

**Subtasks**:
1. **Create advisor markdown template**
   - Executive summary section
   - Detailed plan sections
   - Visual elements (tables, charts)

2. **Update export command**
   - Include advisor output
   - Maintain section ordering
   - Add table of contents

3. **Create standalone plan export**
   - Option for plan-only export
   - Include all context
   - Formatted for sharing

### Task 7: Create Visualization Components
**File**: `/cli/utils/advisor_visualization.py`

**Subtasks**:
1. **Lead scoring visualization**
   - Create scoring rubric table
   - Add weight distribution chart
   - Show example calculations

2. **Tool comparison display**
   - Feature matrix table
   - Pricing tier indicators
   - Integration complexity

3. **Timeline visualization**
   - 30/60/90 day milestones
   - Gantt-style display
   - Progress indicators

### Task 8: Testing Suite
**Files**: `/tests/test_gtm_advisor.py`, `/tests/integration/test_advisor_flow.py`

**Subtasks**:
1. **Unit tests**
   - Schema validation
   - Aggregation logic
   - Scoring calculations

2. **Integration tests**
   - Full synthesis flow
   - Export functionality
   - Error scenarios

3. **LLM output tests**
   - Quality benchmarks
   - Consistency checks
   - Edge case handling

4. **Performance tests**
   - Large context handling
   - Response time benchmarks
   - Memory usage

## Success Metrics
- Comprehensive plans generated in <30 seconds
- All tool recommendations are real/accessible
- Scoring frameworks align with ICP
- Timeline is realistic and actionable
- Export creates share-ready documents

## Timeline
- **Estimated effort**: 12-16 hours
- **Priority**: High (core value proposition)
- **Dependencies**: All previous steps must be complete

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Context window limits | Summarize inputs, use key insights only |
| Generic recommendations | Industry-specific prompt sections |
| Outdated tool info | Maintain tool database, regular updates |
| Overwhelming output | Progressive disclosure, summary first |
| Hallucinated metrics | Grounded benchmarks, validation rules |

## Future Enhancements
- Industry benchmark database
- Tool API integrations for real-time data
- Success story case studies
- ROI calculator based on metrics
- Integration with CRM/automation platforms
- Collaborative planning features
- Progress tracking dashboard