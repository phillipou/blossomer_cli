# GTM Advisor - Strategic Synthesis & Planning

## Context
The Blossomer GTM CLI generates individual GTM assets through a 5-step process: Company Overview → Target Account → Buyer Persona → Email Campaign → Export. While each output is valuable, users currently lack a synthesized strategic plan that ties everything together. They need actionable guidance on lead scoring, prospecting tools, email sequencing, and success metrics to execute their GTM strategy effectively.

## Goals
1. **Synthesize all outputs** into a cohesive GTM execution plan
2. **Create lead scoring framework** for accounts and contacts with qualification criteria vs scoring signals
3. **Recommend specific tool stack** across 9 core categories for prospecting and buying signals
4. **Design email sequencing strategy** using Blossomer's proven Lego Block methodology
5. **Define success metrics** and learning framework for continuous optimization
6. **Provide actionable execution plan** with prioritization strategy and key metrics interpretation

## Design

### Architecture
```
GTM Advisor Service (New Step 6)
    ├── Inputs: Raw Markdown Files (overview.md, account.md, persona.md, email.md)
    ├── LLM Analysis: Parse plain text + Strategic Planning
    └── Output: Complete GTM Strategic Plan (Markdown Document)
```

### Key Components

#### 1. Lead Scoring Framework
**Account Scoring Model**:
- **Qualification Criteria**: Gate-keeping attributes (employee size thresholds, industry fit, etc.)
- **Scoring Signals**: Weighted attributes for prioritization based on Company Fit Hypothesis
- **Predictive Focus**: What signals are MOST predictive of needing the product/service?
- **Simplicity**: Minimal tiers, straightforward implementation, clear rationale

**Contact Scoring Model**:
- **Qualification Criteria**: Role relevance, tenure thresholds, influence indicators
- **Scoring Signals**: Motivation to solve problems, receptiveness to outreach, purchase influence
- **Persona Alignment**: How well they fit defined personas and buying behaviors
- **Buying Intent**: Individual signals that indicate readiness to engage

#### 2. Tool Stack Recommendations (9 Categories)
1. **CRM Tool**: Single recommendation for pipeline management
2. **Email Outreach**: Platform for cold email campaigns
3. **LinkedIn Outreach**: Social selling and connection tools
4. **Contact Verification**: Email validation and deliverability
5. **Account Data**: Firmographic and technographic enrichment
6. **Persona Data**: Contact details and behavioral insights
7. **Buying Signals**: 3-5 tools including web scraping (Browserbase, Firecrawl, N8n, Clay, Apify)
8. **Email Infrastructure**: Domain setup, warmup, deliverability
9. **Workflow Automation**: Integration and sequence management

*Selection criteria based on category, description, Phil's Notes, and company-specific prospecting goals*

#### 3. Email Sequencing Strategy (Lego Block Methodology)
**Core Philosophy**: Treat cold email as a learning tool, not a closer
- **Subject**: 3-4 words, use case/pain/capability focus
- **Block 1 - Intro**: Company/persona context, genuine research
- **Block 2 - Pain Point**: Tactically useful + emotionally salient
- **Block 3 - Company Intro**: What we are + social proof
- **Block 4 - Emphasis**: Re-emphasize capability/use case/outcome
- **Block 5 - CTA**: Nudge curiosity, provide value

**Sequencing Strategy**:
- Follow-up timing and triggers
- Multi-threading across personas
- A/B testing framework for blocks
- Progressive value delivery

#### 4. Success Metrics & Learning Framework
**Prioritization Strategy**:
- Top 10%: Multi-channel engagement, deep research
- Middle 40%: Email focus, copy experimentation
- Bottom 40%: Deprioritize, minimal effort

**Metrics as Learning Signals**:
- **Open Rate**: Subject line effectiveness + targeting relevance
- **Click Rate**: Link/offer relevance to specific segments
- **Reply Rate**: Overall message resonance + targeting accuracy
- **Segmentation Analysis**: Performance by industry/persona/signal for optimization

### Blossomer Methodology Template

*The following template showcases Blossomer's philosophy and should be incorporated into the final GTM plan output:*

#### Core Principles — What's the role of cold Email?
Treat cold email as a learning tool.

Everyone's inbox is flooded with AI-generated sales spam. If you want to stand out, you need to rethink what cold email is for and how to use it effectively in a modern outbound strategy.

Cold email gives you fast, scalable signal on:
* Whether your targeting is working
* What pain points and language resonate with your buyers
* Which personas are more open to engaging

It's a great medium for testing messaging and hypotheses, but it's not a silver bullet. Email won't single-handedly generate all your demand — and it shouldn't try to.

To truly convert cold relationships into pipeline, it needs to be layered with other touches:
* Engaging on LinkedIn
* Publishing helpful content
* Hosting or participating in conversations

Used right, email acts as a first impression and a signal generator — not a closer.

#### How to Cold Email Effectively
1. **Be helpful, not salesy.** Treat your outreach like a nudge from a curious expert — not a pitch from a stranger.
2. **Focus on being relevant, not clever.** A message that speaks to their world will always outperform a hyper-personalized one that doesn't land.
3. **Aim to make a good impression, not close a deal.** Your goal is to start a conversation — or at least leave them thinking, "that was interesting."

#### Messaging Structure ("Lego Block" Model)
Each cold email is composed of subject + 5 core building blocks:

**Subject**: Speaks to the use case, pain point, capability or desired outcome of your persona. 3-4 words, should sound like an internal memo

**Blocks**:
1. **Block 1 - Intro**: Show you've done your homework and anchor to company or persona context. If it's not personalized, it should answer at least answer "Why are you reaching out?" Always strive to be earnest and sound genuine here. No empty compliments.
2. **Block 2 - Pain Point**: Anchor the value prop in something tactically useful and emotionally salient. Each email emphasizes one core pain point, and pairs it with a desired outcome we think this persona will care about.
3. **Block 3 - Company Intro**: Company intro with social proof if available. Answers: "What are we? What makes us unique?" Usually constant; but could vary slightly based on type/vertical/signal
4. **Block 4 - Emphasis**: Re-emphasize related capability, use case, pain point or desired outcome
5. **Block 5 - CTA**: Nudge curiosity, not force a meeting. Make it easy to respond yes and provide value if you can.

#### Interpreting Key Metrics: Learning from Your Outreach
Treat your cold email metrics not just as performance indicators, but as crucial feedback loops for learning and refining your strategy – especially your targeting accuracy and messaging effectiveness.

They provide signals on what's working and what needs adjustment. Here's how to interpret the main ones within our "Lego Block" framework:

**Open Rate**
* **What it Primarily Signals**: Effectiveness of your Subject Line (derived from Block 2's Pain/Outcome), sender reputation, deliverability, AND high-level targeting relevance (Is this general topic relevant to this type of person/company?).
* **Interpretation**:
    * High Open Rate: Suggests your subject lines are resonating OR your target segment generally finds this topic relevant. Good deliverability.
    * Low Open Rate: Could mean weak subject lines, deliverability issues, OR fundamental targeting issues – you might be reaching out to personas or companies who have zero relevance to the subject matter.
* **Actionable Insight**: A/B test Subject Lines. Check deliverability. Crucially, analyze Open Rates by target segment (e.g., industry, persona, signal). Are rates low overall, or just for specific segments, indicating a potential targeting problem for those groups?

**Click Rate (CTR)**
* **What it Primarily Signals**: Interest in any specific links shared AND the relevance of that link/offer to the specific target audience. (Note: As our primary goal is often a reply via Block 4, CTR might be secondary.)
* **Interpretation**:
    * Clicks: Indicate curiosity about your company or a specific offer, validating its relevance to that segment.
    * Low Clicks: Suggests the link/offer isn't compelling OR it's not relevant to the needs/interests of the specific segment you sent it to.
* **Actionable Insight**: Ensure links provide clear value. Evaluate if the linked offer makes sense for the specific target segment receiving it.

**Reply Rate**
* **What it Primarily Signals**: This is often the most important metric for learning. It reflects the overall resonance of your message (Block 1 Intro showing relevance + Block 2 Pain/Outcome + Block 3 Company Intro), the effectiveness of your Block 4 CTA, AND critically, the accuracy of your detailed targeting (Did you reach the right person, at the right company, who actually experiences this pain?).
* **Interpretation**:
    * High Reply Rate (incl. positive, negative, neutral): Strongly suggests your targeting for that segment is accurate, your Block 1 intro established relevance, the Block 2 message resonated, and the Block 4 CTA was effective.
    * Low Reply Rate: Indicates a potential breakdown. It could be message resonance (Block 2), CTA friction (Block 4), OR a significant sign that your targeting is off – wrong persona, wrong company profile, wrong timing/signal.
* **Actionable Insight**: A/B test Block 2 (Pain/Outcome) pairings and Block 4 (CTAs). Critically analyze reply rates by target segment. If a segment consistently yields low replies, revisit your targeting criteria (ICP, persona definitions, buying signals) for that group before overhauling messaging. Use reply content (e.g., "Not the right person," "We don't use Zendesk," "Too small for this") to directly diagnose targeting vs. messaging issues.

**📈 Analyzing Across Segments is Key**
Don't just look at overall rates. Segment your results by industry, company size, persona, buying signal used, or Block 1 variation. If metrics are poor only for "VP of CX personas in Retail," but strong elsewhere, that points to a specific targeting or message-persona mismatch problem, not necessarily a flaw in the entire campaign. This segmentation helps you isolate variables and learn faster.

Remember, the goal is continuous learning. Use these metrics to systematically test both your targeting assumptions and your messaging components to improve the effectiveness of your outreach over time.

## Current Implementation Status 🎉 COMPLETED!

### ✅ Completed Components (Major Milestone)
1. **GTM Advisor Prompt Template** ✅ - Comprehensive system/user prompt with strategic guidance
2. **GTM Advisor Schema** ✅ - Complete Pydantic models for all output components  
3. **Tools Database Integration** ✅ - CSV-based tool recommendations with Phil's notes (40+ tools)
4. **Lead Scoring Framework** ✅ - Account and contact models with precision requirements
5. **Blossomer Methodology Integration** ✅ - Complete framework with prioritization strategy
6. **🎉 GTM Advisor Service** ✅ - COMPLETED! Data aggregation and LLM orchestration with markdown file integration
7. **🎉 CLI Integration** ✅ - COMPLETED! Full Step 5 integration into main init flow
8. **🎉 Strategic Plan Generation** ✅ - COMPLETED! Complete markdown strategic plans with scoring frameworks and tool recommendations
9. **🎉 PersonaFormatter Enhancement** ✅ - COMPLETED! Full persona data formatting with demographics, use cases, buying signals, and journey

### 🏆 Major Achievement: Complete 5-Step Pipeline
The Blossomer GTM CLI now delivers a **complete end-to-end GTM intelligence pipeline**:
- **Step 1-4**: Company analysis → Target account → Buyer persona → Email campaign
- **Step 5**: 🎉 **GTM Strategic Plan** - Comprehensive strategic plan with:
  - Account and contact scoring frameworks (qualification criteria + scoring signals)
  - Tool stack recommendations across 9 categories with Phil's expert picks
  - Blossomer's proven Lego Block email methodology
  - Prioritization strategy (10%/40%/40% model) 
  - Metrics interpretation guide with actionable insights
  - Complete execution roadmap

### Key Design Decisions Implemented
- **Template-Driven LLM Generation** - LLM receives structured template with instructions to fill all placeholders
- **Markdown File Integration** - GTM advisor loads rich markdown content instead of raw JSON
- **CSV Tools Database** - 40+ tools across 9 categories with Phil's recommendations properly prioritized
- **Precision Requirements** - Every scoring criteria must be detectable with available tools and includes specific detection methods
- **Full Persona Formatting** - Enhanced PersonaFormatter includes demographics, use cases, buying signals, goals, objections, and purchase journey

### 🚀 User Impact
- **Complete GTM Packages**: Users now get comprehensive strategic plans instead of incomplete 4-step flows
- **Actionable Intelligence**: Ready-to-execute strategies with specific tool recommendations and scoring models
- **Professional Output**: Strategic plans demonstrate Blossomer's full GTM intelligence capabilities
- **Rich Persona Data**: Detailed buyer personas with complete journey mapping and signal detection

## Implementation Plan

### Task 1: Create GTM Advisor Prompt Template
**File**: `/app/prompts/templates/gtm_advisor.jinja2`

**Subtasks**:
1. **Design comprehensive prompt structure**
   - System prompt emphasizing strategic synthesis role as GTM advisor
   - Input sections for all 4 previous outputs (overview, account, persona, email)
   - Account scoring model development (qualification vs scoring criteria)
   - Contact scoring model development with persona alignment
   - Tool stack recommendations across 9 specific categories
   - Blossomer Lego Block methodology integration
   
2. **Create lead scoring guidance**
   - Include example scoring model prompts from your provided templates
   - Emphasize first principles thinking: "What signals are MOST predictive of needing this product?"
   - Extract Company Fit Hypothesis from overview capabilities and positioning insights
   - Map persona pain points and use cases to scoring signals
   - Simplicity guidelines: minimal tiers, straightforward implementation
   - Clear distinction between qualification gates and scoring signals

3. **Define tool recommendation logic**
   - **Required 9 categories**: CRM, Outreach (Email), Outreach (LinkedIn), Contact Verification, Account Data, Persona Data, Buying Signals, Email Infrastructure, Orchestration
   - **Tools database integration**: Load from `/app/data/gtm_tools.csv` with 40+ tools across all categories
   - **Selection criteria**: Prioritize Phil's recommended tools (8 total), then choose based on company-specific needs
   - **Recommended tools available**: Attio (CRM), Smartlead.ai (Email/Infrastructure), HeyReach (LinkedIn), FullEnrich (Verification), Apify/Browserbase/Firecrawl (Buying Signals), Lemwarm (Infrastructure)
   - **Category coverage**: All 9 categories covered with multiple options per category

4. **Integrate Blossomer methodology template**
   - Copy the complete methodology template from experiment document
   - Core principles section (cold email as learning tool)
   - Lego Block framework (5 blocks + subject) with examples
   - Metrics interpretation framework with actionable insights
   - Prioritization strategy (10%/40%/40% model) with execution guidelines

5. **Add synthesis-specific guidance**
   - Connect overview positioning insights to scoring criteria
   - Map account buying signals to contact scoring signals
   - Align email strategy with Lego Block recommendations
   - Create coherent narrative across all GTM components

### Task 2: Create GTM Advisor Schema
**File**: `/app/schemas/gtm_advisor.py`

**Subtasks**:
1. **Define core models**
   ```python
   class QualificationCriteria(BaseModel):
       criterion: str
       type: str  # "binary", "threshold", "qualitative"
       description: str
       threshold: Optional[str]
   
   class ScoringSignal(BaseModel):
       signal: str
       weight: float
       scoring_guide: Dict[str, int]
       rationale: str
   
   class AccountScoringModel(BaseModel):
       qualification_criteria: List[QualificationCriteria]
       scoring_signals: List[ScoringSignal]
       total_possible_score: int
   
   class ContactScoringModel(BaseModel):
       qualification_criteria: List[QualificationCriteria] 
       scoring_signals: List[ScoringSignal]
       total_possible_score: int
   
   class ToolRecommendation(BaseModel):
       category: str  # CRM, Outreach (Email), Outreach (LinkedIn), etc.
       tool_name: str
       description: str
       website: str
       phils_notes: Optional[str]
       recommended: bool
       selection_rationale: str  # Why this tool was chosen for this company
   
   class LegoBlock(BaseModel):
       block_number: int
       block_name: str
       purpose: str
       example: str
       guidelines: List[str]
   
   class PrioritizationStrategy(BaseModel):
       top_10_percent: str
       middle_40_percent: str
       bottom_40_percent: str
       rationale: str
   ```

2. **Create output model**
   ```python
   class GTMAdvisorOutput(BaseModel):
       account_scoring: AccountScoringModel
       contact_scoring: ContactScoringModel
       tool_stack: Dict[str, ToolRecommendation]  # 9 categories
       lego_block_framework: List[LegoBlock]
       prioritization_strategy: PrioritizationStrategy
       metrics_interpretation: Dict[str, Any]
       execution_plan: ExecutionPlan
   ```

3. **Add validation logic**
   - Ensure scoring weights sum to 100% for each model
   - Validate all 9 tool categories are present
   - Check Lego Block completeness (5 blocks)
   - Ensure prioritization adds to 100%

### Task 3: Create GTM Advisor Service
**File**: `/app/services/gtm_advisor_service.py`

**Subtasks**:
1. **Implement data aggregation**
   ```python
   async def aggregate_gtm_data(self, domain: str):
       # Load all previous outputs from json_output directory
       overview = self.load_json_output(domain, "overview.json")
       account = self.load_json_output(domain, "account.json")  
       persona = self.load_json_output(domain, "persona.json")
       email = self.load_json_output(domain, "email.json")
       
       # Structure for synthesis
       return {
           "company_context": {
               "name": overview["company_name"],
               "description": overview["description"],
               "capabilities": overview["capabilities"],
               "positioning": overview["positioning_insights"]
           },
           "target_account": {
               "profile": account["target_account_description"],
               "firmographics": account["firmographics"],
               "buying_signals": account["buying_signals"]
           },
           "target_persona": {
               "name": persona["target_persona_name"],
               "description": persona["target_persona_description"],
               "use_cases": persona["use_cases"],
               "buying_journey": persona["purchase_journey"],
               "pain_points": [uc["pain_points"] for uc in persona["use_cases"]]
           },
           "email_strategy": {
               "subjects": email["subjects"],
               "writing_process": email["writing_process"],
               "follow_up": email.get("follow_up_email")
           }
       }
   ```

2. **Create synthesis logic**
   - Extract Company Fit Hypothesis from overview capabilities and positioning
   - Identify most predictive signals from account and persona buying signals
   - Map persona pain points to scoring criteria
   - Build comprehensive context for LLM analysis

3. **Implement LLM orchestration**
   - Use TemplateRunner for prompt execution
   - Handle large context windows (all 4 previous outputs)
   - Implement retry logic for complex synthesis
   - Pass structured data to Jinja2 template

4. **Add output post-processing**
   - Validate tool recommendations match required 9 categories
   - Ensure scoring weights sum to 100% for both models
   - Verify Lego Block framework completeness
   - Format prioritization strategy percentages

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
- All tool recommendations are real/accessible across 9 categories
- Account and contact scoring frameworks align with ICP and persona insights
- Lead scoring models use first principles thinking with minimal tiers
- Blossomer methodology template fully integrated
- Prioritization strategy follows 10%/40%/40% model
- Export creates share-ready strategic documents

## Timeline 🎉 COMPLETED - MAJOR MILESTONE ACHIEVED!
- **Actual effort**: ~16 hours (perfectly estimated!)
- **Priority**: ✅ COMPLETED - Major value delivered to users
- **Dependencies**: All previous steps complete ✅, tools database complete ✅
- **Status**: 🏆 **FULLY IMPLEMENTED AND WORKING** - Complete 5-step GTM pipeline
- **Achievement**: End-to-end GTM intelligence from domain analysis to executable strategic plan

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