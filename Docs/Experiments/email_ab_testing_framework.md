# Email A/B Testing Framework Enhancement

## Context
The Blossomer GTM CLI currently generates initial cold outreach emails with follow-up emails, but lacks a systematic A/B testing framework. Users need concrete examples of how to test different messaging approaches using the Lego Block methodology to optimize their outreach performance.

## Goals ✅ COMPLETED
1. **Add email variation to email generation** - Generate one alternative email targeting different persona use case
2. **Leverage existing persona use cases** - Create email variations based on different persona use cases  
3. **Focus on writing craft** - Let email generation focus on writing, leave experiment design to GTM Advisor
4. **Include in sync files** - Show variations in editable markdown files
5. **Integration with existing flow** - Seamless addition to current email generation process

## Design Approach

### Why Email Generation vs GTM Advisor?
Email generation is the ideal place for A/B testing because:
- **Has all email context** - Current email, persona use cases, block breakdown
- **Already generates variations** - Subject alternatives, different emphasis options  
- **Knows Lego Block structure** - Email flow already maps to blocks
- **Has persona use cases** - Can create variations for each use case
- **Real email content** - Can show actual variations vs theoretical examples

### Simplified Email Variation Structure
```
Email Generation Output (Enhanced)
    ├── Main email (subjects, full_email_body, email_body_breakdown)
    ├── Follow-up email (subject, body, wait_days)
    ├── Email variation (subject, full_email_body) - targeting different use case
    └── Writing process {
            trigger, problem, help, cta,
            variation: how the variation differs,
            followup: how the follow-up differs
        }
```

### Key Testing Variables
- **Subject Line**: Test different pain points, capabilities, or outcomes (3-4 words)
- **Block 2 (Pain Point)**: Test different persona use cases and pain points
- **Block 4 (Emphasis)**: Test different capability emphasis or desired outcomes
- **Constant Blocks**: Block 1 (Intro), Block 3 (Company Intro), Block 5 (CTA) stay relatively consistent

## Implementation Plan ✅ COMPLETED

### Task 1: Add Email Variation to Email Generation Prompt ✅ COMPLETED
**File**: `/app/prompts/templates/email_generation_blossomer.jinja2`

**Completed**:
- Added email variation requirement for different persona use case
- Simplified from complex A/B framework to focused writing task
- Enhanced writing_process with variation and followup explanations
- Removed experiment design elements (GTM Advisor will handle that)

### Task 2: Update Email Generation Schema ✅ COMPLETED
**File**: `/app/schemas/__init__.py`

**Completed**:
- Created simplified EmailVariation model (subject, full_email_body)
- Updated EmailGenerationResponse with email_variation field  
- Enhanced writing_process description for variation and followup fields
- Maintained backward compatibility

### Task 3: Update Email Generation Service ✅ COMPLETED
**File**: `/app/services/email_generation_service.py`

**Completed**:
- Service already handles new schema automatically
- No changes needed - existing validation works with Optional fields
- Persona use cases already passed to template

### Task 4: Update CLI Display ✅ COMPLETED
**Files**: `/cli/commands/show.py`, `/cli/utils/markdown_formatter.py`

**Completed**:
- Updated show command to display "Variation: ✓" in summary
- Added email variation display in both preview and export modes
- Updated writing process display to show variation and followup strategies
- Added sync file support for follow-up and variation sections

### Task 5: Update Export Functionality ✅ COMPLETED
**File**: `/cli/commands/export.py`, `/cli/utils/markdown_formatter.py`

**Completed**:
- Export automatically includes email variation via markdown formatter
- Added email variation section to sync files with proper markers
- Follow-up and variation now appear in editable markdown files

## A/B Testing Framework Example

### Baseline Email (Current)
- **Subject**: "Outbound system help"
- **Block 2**: "Building an effective outbound system can be a headache, especially when quick wins matter"
- **Block 4**: "If you're open, I'd love to share some simple strategies that could help you accelerate your growth"
- **Target Use Case**: Rapid outbound sales setup

### Variation 1: Scaling Focus
- **Subject**: "Outreach scaling help"  
- **Block 2**: "Manual or generic outreach methods limit growth and responsiveness to market opportunities"
- **Block 4**: "We've helped startups achieve faster market penetration with scalable, tailored outbound systems"
- **Target Use Case**: Scaling outbound outreach
- **Hypothesis**: Does scaling pain resonate better than setup pain?

### Variation 2: Speed Focus  
- **Subject**: "Sales velocity boost"
- **Block 2**: "Lengthy onboarding and technical integrations slow down outbound campaign launches"
- **Block 4**: "Our ready-to-implement tactics start delivering results immediately, reducing time-to-value"
- **Target Use Case**: Reducing onboarding delays
- **Hypothesis**: Does speed/time focus outperform general setup messaging?

## Success Metrics ✅ ACHIEVED
- Email variation included in all email generation outputs
- Users can see alternative email targeting different use case
- Variations are based on actual persona use cases from analysis
- Writing process explains both variation and follow-up strategies
- Integration doesn't disrupt existing email generation flow
- Follow-up and variation appear in editable sync files

## Timeline ✅ COMPLETED
- **Actual effort**: ~3 hours
- **Priority**: High (enhances core email functionality)
- **Dependencies**: Existing email generation infrastructure
- **Status**: All tasks completed

## Risks & Mitigations
| Risk | Mitigation | Status |
|------|------------|--------|
| Output complexity | Keep A/B framework optional, clean presentation | Planned |
| Performance impact | Single LLM call, minimal processing overhead | Planned |
| User confusion | Clear documentation, simple examples | Planned |
| Breaking changes | Optional schema fields, backward compatibility | Planned |

## Future Enhancements
- Statistical significance calculators
- Integration with email tools for actual A/B testing
- Performance tracking across variations
- Machine learning for variation recommendations