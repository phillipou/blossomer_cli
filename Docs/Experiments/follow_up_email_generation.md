# Follow-Up Email Generation Enhancement

## Context
The Blossomer GTM CLI currently generates initial cold outreach emails as part of its 5-step GTM package generation flow. Users need follow-up emails to maintain engagement with prospects who don't respond to the initial outreach. Follow-up emails are critical for sales success, with most conversions happening after multiple touchpoints.

## Goals ✅ COMPLETED
1. **Generate a follow-up email** alongside the initial email in the existing email generation step ✅
2. **Maintain quality standards**: 60 words max, no platitudes, genuine value proposition ✅
3. **Seamless integration**: No disruption to existing workflow, follows current patterns ✅
4. **Quick implementation**: This is a focused enhancement to existing functionality ✅
5. **Variety enforcement**: Follow-up emails must take different angles than initial emails ✅
6. **Website link integration**: Include properly formatted website links ✅

## Design

### Approach
Extend the existing email generation service and prompt to produce both initial and follow-up emails in a single LLM call. This minimizes API costs and maintains consistency between the emails.

### Follow-Up Email Requirements ✅ IMPLEMENTED
- **Length**: 60 words maximum ✅
- **Opening**: Brief reinforcement of fit/value (no "following up" platitudes) ✅
- **Body**: Must include properly formatted website link as markdown ✅
- **CTA**: Non-salesy, helpful tone ✅
- **Timing**: Suggest 3-5 days after initial email ✅
- **Variety**: Must take different angle than initial email (pain→capability, etc.) ✅

### Data Flow
```
Email Generation Service
    ├── Input: Company context + ICP + Persona
    ├── LLM Call (single prompt)
    └── Output: {
            initial_email: {...},
            follow_up_email: {
                subject: string,
                body: string,
                wait_days: number
            }
        }
```

## Implementation Results ✅ COMPLETED

### Task 1: Update Email Generation Prompt Template ✅
**File**: `/app/prompts/templates/email_generation_blossomer.jinja2`

**Completed Subtasks**:
1. **Added follow-up email section to system prompt** ✅
   - Inserted comprehensive follow-up guidelines with examples
   - Added variety enforcement requirements (different angles)
   - Updated JSON output format to include follow_up_email object

2. **Updated output instructions** ✅
   - Modified JSON schema to include follow_up_email with subject, body, wait_days
   - Added validation rules for 60-word limit
   - Added website link formatting requirements

3. **Added variety enforcement logic** ✅
   - Guide LLM to analyze initial email emphasis 
   - Choose different emphasis for follow-up (pain→capability, etc.)
   - Ensure new information, not rephrased content

### Task 2: Update Email Generation Schema ✅
**File**: `/app/schemas/__init__.py`

**Completed Subtasks**:
1. **Created FollowUpEmail model** ✅
   ```python
   class FollowUpEmail(BaseModel):
       subject: str = Field(..., description="Follow-up email subject line (3-4 words)")
       body: str = Field(..., description="Complete follow-up email body (60 words max)")
       wait_days: int = Field(default=4, ge=3, le=7, description="Days to wait before sending")
   ```

2. **Updated EmailGenerationResponse model** ✅
   - Added `follow_up_email: Optional[FollowUpEmail]` 
   - Updated metadata to include word counts for both emails
   - Maintained backward compatibility

3. **Backward compatibility maintained** ✅
   - follow_up_email is Optional for existing data
   - No breaking changes to existing API

### Task 3: Update Email Generation Service
**File**: `/app/services/email_generation_service.py`

**Subtasks**:
1. **Update prompt inputs**
   - Pass seller website URL if available
   - Include flag for follow-up generation

2. **Handle LLM response**
   - Parse follow-up email from response
   - Validate follow-up meets requirements

3. **Error handling**
   - Graceful degradation if follow-up generation fails
   - Log warnings but don't block main flow

### Task 4: Update CLI Display
**Files**: `/cli/commands/generate.py`, `/cli/utils/formatting.py`

**Subtasks**:
1. **Display follow-up email in terminal**
   - Add section after initial email display
   - Show wait days recommendation
   - Use consistent Rich formatting

2. **Update email regeneration flow**
   - Allow regenerating both emails together
   - Option to regenerate just follow-up

### Task 5: Update Export Functionality
**File**: `/cli/commands/export.py`

**Subtasks**:
1. **Include follow-up in markdown export**
   - Add "Follow-Up Email" section
   - Format with proper spacing
   - Include timing recommendation

2. **Update JSON export**
   - Ensure follow-up data is included
   - Maintain backward compatibility

### Task 6: Testing
**Files**: Create `/tests/test_follow_up_email.py`

**Subtasks**:
1. **Unit tests**
   - Schema validation
   - Follow-up length constraints
   - Prompt template rendering

2. **Integration tests**
   - Full email generation flow
   - Export functionality
   - Error scenarios

3. **Manual testing checklist**
   - Run through complete GTM flow
   - Verify follow-up quality
   - Test edge cases (no website, etc.)

## What Was Actually Implemented ✅

### Core Features Delivered
1. **Follow-up email generation** - Generates both initial and follow-up emails in single LLM call
2. **Variety enforcement** - Follow-ups must take different angles (pain→capability, capability→results, etc.)
3. **Website link integration** - Properly formatted markdown links in follow-up emails
4. **CLI display updates** - Shows both emails in preview and detailed views
5. **Export functionality** - Includes follow-up emails in markdown exports
6. **Evaluation framework** - Added 6th criterion to LLM judge for variety assessment

### Updated Components
- **Prompt Template**: Added comprehensive follow-up guidelines with examples
- **Schema**: Added FollowUpEmail model and updated response schema  
- **CLI Display**: Updated show commands and preview utilities
- **Markdown Formatter**: Enhanced to display follow-up emails
- **Evaluation**: Extended LLM judge with follow-up variety criterion
- **Tests**: Created comprehensive test suite

### Key Quality Enhancements
- **JSON parsing fixes** - Resolved evaluation template parsing errors
- **Character limits** - Enforced 60-word limit for follow-ups
- **Link formatting** - Natural integration of website links
- **Different angles** - Explicit variety requirements prevent repetition

## Success Metrics ✅ ACHIEVED
- Follow-up emails consistently under 60 words ✅
- No platitudes or salesy language ✅
- Seamless integration with existing flow ✅
- No performance degradation ✅
- Comprehensive evaluation framework ✅

## Timeline ✅ COMPLETED
- **Estimated effort**: 4-6 hours → **Actual: ~6 hours** ✅
- **Priority**: High (quick win, high user value) → **Delivered** ✅
- **Dependencies**: None (builds on existing infrastructure) → **Confirmed** ✅

## Risks & Mitigations ✅ ADDRESSED
| Risk | Mitigation | Status |
|------|------------|--------|
| LLM inconsistency | Strong prompt engineering with examples | ✅ Comprehensive guidelines added |
| Increased token usage | Single LLM call for both emails | ✅ Maintained single call approach |
| Breaking changes | Optional schema fields, backward compatibility | ✅ All changes backward compatible |
| Quality issues | Validation rules, length constraints | ✅ Added word limits and evaluation |
| JSON parsing errors | Proper escaping in evaluation templates | ✅ Fixed evaluation parsing issues |
| Follow-up repetition | Explicit variety enforcement in prompt | ✅ Different angle requirements added |

## Future Enhancements
- Multiple follow-up sequence templates
- A/B testing variations
- Personalization based on engagement signals
- Integration with email automation tools