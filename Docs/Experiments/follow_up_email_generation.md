# Follow-Up Email Generation Enhancement

## Context
The Blossomer GTM CLI currently generates initial cold outreach emails as part of its 5-step GTM package generation flow. Users need follow-up emails to maintain engagement with prospects who don't respond to the initial outreach. Follow-up emails are critical for sales success, with most conversions happening after multiple touchpoints.

## Goals
1. **Generate a follow-up email** alongside the initial email in the existing email generation step
2. **Maintain quality standards**: 60 words max, no platitudes, genuine value proposition
3. **Seamless integration**: No disruption to existing workflow, follows current patterns
4. **Quick implementation**: This is a focused enhancement to existing functionality

## Design

### Approach
Extend the existing email generation service and prompt to produce both initial and follow-up emails in a single LLM call. This minimizes API costs and maintains consistency between the emails.

### Follow-Up Email Requirements
- **Length**: 60 words maximum
- **Opening**: Brief reinforcement of fit/value (no "following up" platitudes)
- **Body**: Link to seller's website when available
- **CTA**: Non-salesy, helpful tone
- **Timing**: Suggest 3-5 days after initial email

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

## Implementation Plan

### Task 1: Update Email Generation Prompt Template
**File**: `/app/prompts/templates/email_generation_blossomer.jinja2`

**Subtasks**:
1. **Add follow-up email section to system prompt**
   - Insert follow-up guidelines after initial email rules
   - Include example follow-up email structure
   - Specify JSON output format

2. **Update output instructions**
   - Modify JSON schema section to include follow_up_email
   - Add validation rules for follow-up length

3. **Add chain-of-thought reasoning**
   - Guide LLM to consider initial email content when crafting follow-up
   - Ensure complementary messaging without repetition

### Task 2: Update Email Generation Schema
**File**: `/app/schemas/email_generation.py`

**Subtasks**:
1. **Create FollowUpEmail model**
   ```python
   class FollowUpEmail(BaseModel):
       subject: str
       body: str
       wait_days: int = Field(default=4, ge=3, le=7)
   ```

2. **Update EmailGenerationOutput model**
   - Add `follow_up_email: Optional[FollowUpEmail]`
   - Update validation logic

3. **Backward compatibility**
   - Make follow_up_email Optional for existing data
   - Add migration logic if needed

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

## Success Metrics
- Follow-up emails consistently under 60 words
- No platitudes or salesy language
- Seamless integration with existing flow
- No performance degradation
- Positive user feedback on email quality

## Timeline
- **Estimated effort**: 4-6 hours
- **Priority**: High (quick win, high user value)
- **Dependencies**: None (builds on existing infrastructure)

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| LLM inconsistency | Strong prompt engineering with examples |
| Increased token usage | Single LLM call for both emails |
| Breaking changes | Optional schema fields, backward compatibility |
| Quality issues | Validation rules, length constraints |

## Future Enhancements
- Multiple follow-up sequence templates
- A/B testing variations
- Personalization based on engagement signals
- Integration with email automation tools