# Blossomer GTM CLI Tool - PRD

## Implementation Status

✅ **CORE FUNCTIONALITY**: 4-step GTM generation fully working  
✅ **EXPORT COMMAND**: Markdown formatting and export functionality complete
⚠️ **IN PROGRESS**: GTM Plan generation (step 5)  
❌ **NOT IMPLEMENTED**: edit, list, status commands

## Overview

A lightweight CLI tool that demonstrates Blossomer's GTM intelligence by analyzing a company domain and generating a complete go-to-market package. The tool runs locally, stores outputs as JSON files, and provides an interactive experience for technical founders.

**Current CLI name**: `blossomer` (not `gtm-cli` as originally planned)

## Core Principles

- **60-second value**: Generate complete GTM assets from domain to email in under a minute
- **Interactive by default**: Guide users through refinement at each step
- **Progressive disclosure**: Start simple, reveal complexity only when needed
- **Local-first**: No authentication, no cloud dependencies, just files on disk
- **Reuse existing assets**: Leverage Blossomer's proven prompts and data models

## Command Structure

### Primary Commands

1. **`init`** - Start new GTM project (interactive by default)
2. **`show`** - Display generated assets
3. **`export`** - Export assets as markdown

### Secondary Commands (for power users)

1. **`generate`** - Manually run a specific step
2. **`edit`** - Open generated file in system editor
3. **`list`** - Show all projects

## The Current 4-Step Flow

1. **Company Overview** → 2. **Target Account** → 3. **Buyer Persona** → 4. **Email Campaign**

**Note**: GTM Plan (step 5) is planned but not yet implemented.

## Detailed Command Specifications

### 1. `blossomer init [domain]`

The primary command that runs the complete GTM pipeline.

### **1.1 Interactive Mode (Default)**

**Input:**

```bash
blossomer init acme.com
# OR prompt for domain interactively:
blossomer init
```

**Step 1 - Company Overview:**

```
🚀 Blossomer GTM CLI - Analyzing acme.com

[1/5] 🔍 Analyzing company...
   → Fetching website content... ✓
   → Processing with AI... ✓  
   → done (8s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPANY OVERVIEW - Quick Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: AI-powered QA for customer support teams
Category: B2B SaaS - Support Operations
Model: Usage-based pricing, 14-day trial

Key Capabilities:
• Real-time conversation analysis
• Knowledge gap identification
• Automated coaching suggestions

Target Market Signals:
• Focus on scaling support teams
• Enterprise features (SSO, API)
• Case studies from 50-500 employee companies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full analysis saved to: overview.json (2.3KB)

Options:
[C]ontinue to next step (or press Enter)
[E]dit full analysis in editor

[A]bort (or press Ctrl+C)

Choice [c/e/a]: C

```

If user chooses [E]dit:

```
Opening overview.json in your default editor...
[User edits JSON file in their editor]
✓ Changes saved. Continuing with updated analysis...

```

**Step 2 - Target Account:**

```
[2/5] 🎯 Generating target account profile... done (5s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TARGET ACCOUNT - Quick Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Profile: Mid-Market FinTech Companies
Size: 100-500 employees, $10M-$50M revenue
Geography: North America, UK

Why this profile:
• Growing support volume from customer base expansion
• Regulatory requirements drive quality needs
• Have budget but need ROI justification

Top Buying Signals:
• Recent funding round (Series A/B)
• Hiring multiple support agents
• Job posts mentioning "scale" or "quality"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full profile saved to: account.json (3.1KB)

Options:
[C]ontinue to next step
[E]dit full profile in editor
[A]bort

Choice [c/e/a]: C

```

**Step 3 - Buyer Persona:**

```
[3/4] 👤 Building buyer persona... done (6s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUYER PERSONA - Quick Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: VP of Customer Success
Reports to: COO or CEO
Team: 15-30 direct reports

Key Priorities:
• Reduce ticket resolution time
• Improve CSAT scores
• Scale team efficiently

Biggest Challenges:
• Maintaining quality during growth
• Long agent onboarding times
• Lack of visibility into knowledge gaps

What gets their attention:
• ROI data from similar companies
• Time-to-value under 30 days
• Integration with existing stack
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full persona saved to: persona.json (4.2KB)

Options:
[C]ontinue to email campaign
[E]dit full persona in editor
[A]bort

Choice [c/e/a]: C

```
Step 3 - Buyer Persona:
[3/4] 👤 Building buyer persona... done (6s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUYER PERSONA - Quick Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: VP of Customer Success
Reports to: COO or CEO
Team: 15-30 direct reports

Key Priorities:
- Reduce ticket resolution time
- Improve CSAT scores  
- Scale team efficiently

Biggest Challenges:
- Maintaining quality during growth
- Long agent onboarding times
- Lack of visibility into knowledge gaps

What gets their attention:
- ROI data from similar companies
- Time-to-value under 30 days
- Integration with existing stack
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full persona saved to: persona.json (4.2KB)

Options:
[C]ontinue to GTM plan
[E]dit full campaign in editor
[A]bort

Choice [c/e/a]: C

Generate email automatically or go through guided email builder?
[A]utomatic / [G]uided

Choice [A/g]: G
Step 4 - Email Campaign (Guided Mode):
Email Guide Step 1: Select Point of Emphasis
📧 Email Campaign Builder - Guided Mode

Step 1/5: What should your email emphasize?

1. Use Case: Focus on specific workflows your solution impacts
2. Pain Point: Focus on challenges they're experiencing
3. Capability: Focus on what your solution can do
4. Desired Outcome: Focus on the results they want

Select emphasis [1-4]: 2
✓ Focusing on pain points

Email Guide Step 2: Select Specific Content
Step 2/5: Which pain point should we focus on?

Based on your persona analysis, here are their key pain points:

1. Maintaining support quality during rapid scaling
2. Long agent onboarding times
3. Lack of visibility into knowledge gaps
4. Other (specify custom instructions to the LLM)

Select pain point [1-4]: 1
✓ Selected: Quality challenges during scaling

Email Guide Step 3: Add Social Proof (Optional)
Step 3/5: Do you have any social proof to include?

Social proof examples: "We worked with Deel recently and doubled their QA coverage"
Leave blank to skip, or enter your social proof:

[Enter social proof or press Enter to skip]: We helped TechCorp reduce support response time by 40% in 30 days

✓ Social proof added

Email Guide Step 4: Select Personalization Approach
Step 4/5: How should we personalize this email?

Based on your buying signals analysis, here are personalization options:

1. Recent Series B funding
2. Hiring spree activity  
3. Company growth metrics
4. Tech stack adoption
5. Other (specify custom instructions to the LLM)

Select personalization [1-5]: 1
✓ Will reference Series B funding

Email Guide Step 5: Select Call-to-Action
Step 5/5: What should the call-to-action be?

1. Ask for a meeting (e.g. "Worth a quick 15-min call next week?")
2. Ask if it's a priority (e.g. "Is improving support efficiency a Q1 priority?")
3. Ask for feedback (e.g "Curious if this resonates with your experience?")
4. Offer free help (e.g "Happy to share our scaling playbook - interested?")
5. Invite to resource (e.g. "We have a guide on this - should I send it over?")
6. Other (write your own custom CTA)

Select CTA [1-6]: 1

✓ Will ask for a meeting

Generating your personalized email campaign... done (4s)
Email Preview After Generation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMAIL CAMPAIGN - Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: support quality dropping post-series b?

Hi {{FirstName}},

Congrats on the Series B! With that kind of growth, 
I imagine maintaining support quality is getting 
harder. 

Most teams your size see consistency drop as they 
scale from 10 to 50 agents. Different agents give 
different answers, and there's no way to catch it 
until customers complain.

We help companies like yours maintain quality 
through real-time knowledge gap detection. Worth 
a quick 15-min call next week to discuss?

Best,
{{Your name}}

Alternative subjects:
- "scaling support without losing quality?"
- "series b growing pains in support?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full campaign saved to: email.json (2.8KB)

Options:
[C]ontinue (analysis complete)
[E]dit full campaign in editor
[A]bort

Choice [c/e/a]: C

✅ **Email campaign completed! (4/4 steps)**

Created in: gtm_projects/acme.com/
   → overview.json (Company analysis)
   → account.json (Target account profile) 
   → persona.json (Buyer persona)
   → email.json (Email campaign)

📋 Quick commands:
   blossomer show all
   blossomer generate overview --force  # regenerate any step

Note: GTM Plan generation (step 5) coming soon!

Step 4 - Email Campaign (Automatic Mode):
[If user selected [A]utomatic at the persona step]

[4/4] ✉️ Auto-generating email campaign... done (4s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EMAIL CAMPAIGN - Quick Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: reduce support resolution time?

Hi {{FirstName}},

Noticed {{Company}}'s recent Series B - congrats! 
With rapid growth, maintaining support quality 
gets harder. 

Most teams your size see 40% longer resolution 
times as they scale. We help identify knowledge 
gaps in real-time so agents get answers faster.

Worth a quick chat to see if this could help 
{{Company}}?

Alternative subjects:
- "support scaling challenges at {{Company}}?"
- "40% faster ticket resolution - interested?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full campaign saved to: email.json (2.8KB)

Options:
[C]ontinue (analysis complete)
[E]dit full campaign in editor
[A]bort

Choice [c/e/a]: C

✅ **Complete! All 4 steps finished.**


**Step 5 - GTM Plan (NEW):**

```
[5/5] 📋 Creating your GTM action plan... done (7s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GTM EXECUTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on your analysis, here's your 30-day plan:

WEEK 1: Build Your List
□ Set up Clay.com workspace
□ Import firmographic criteria from account.json
□ Build list of 100 target companies
□ Enrich with funding data from Crunchbase
□ Filter by "hiring support agents" signal

WEEK 2: Find Your Personas
□ Use Apollo.io to find VP Customer Success
□ Cross-reference with LinkedIn Sales Nav
□ Verify emails with Hunter.io
□ Build list of 100 qualified contacts

WEEK 3: Launch Campaign
□ Set up Instantly.ai with email templates
□ A/B test your 3 subject lines
□ Send 20 emails/day with personalization
□ Monitor open rates (target: 40%+)

WEEK 4: Optimize & Scale
□ Analyze response patterns
□ Refine messaging based on replies
□ Scale to 50 emails/day
□ Set up follow-up sequences

RECOMMENDED TOOL STACK:
• Clay.com - $149/mo (list building)
• Apollo.io - $99/mo (contact finding)
• Instantly.ai - $97/mo (email automation)
• Total: ~$350/mo

EXPECTED RESULTS:
• 500 emails sent
• 40% open rate = 200 opens
• 5% reply rate = 25 replies
• 10% to meeting = 2-3 qualified meetings

QUICK WINS:
1. Join FinTech Slack communities
2. Comment on LinkedIn posts from target personas
3. Create case study from beta customer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full plan saved to: plan.json (5.1KB)

✅ **Email campaign completed! All 4 steps done.**

Created in: gtm_projects/acme.com/
   Total time: 25 seconds • Total cost: ~$0.12

📋 Quick copy commands:
   gtm-cli show all
   gtm-cli export
   gtm-cli edit plan

Next steps:
• Review all assets: gtm-cli show all
• Export as report: gtm-cli export
• Start executing: Follow the plan above!

```

### **1.2 YOLO Mode (One-Shot Generation)**

**Input:**

```bash
blossomer init acme.com --yolo
```

**Output:**

```
🚀 YOLO Mode - Generating everything at once!

[1/4] 🔍 Analyzing company... done (8s)
[2/4] 🎯 Generating target account... done (5s)
[3/4] 👤 Building buyer persona... done (6s)
[4/4] ✉️ Creating email campaign... done (4s)

✅ Complete! All assets created in: gtm_projects/acme.com/

Quick Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: AI-powered QA for support teams
Target: FinTech companies (100-500 employees)
Persona: VP of Customer Success
Email: "reduce support resolution time?"
Next: GTM plan generation coming soon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review everything: blossomer show all

```

### **1.3 With Additional Context**

**Input:**

```bash
blossomer init acme.com --context "We're a Series A startup building AI tools for customer support teams"
```

**Smart Domain Handling:**
The CLI automatically handles various domain formats:
- `acme.com` → `https://acme.com`
- `www.acme.com` → `https://www.acme.com`  
- `https://acme.com/about` → `https://acme.com`

The context is used to improve all generation steps but doesn't change the interactive flow.

### **1.4 Handling Existing Projects**

**Input:**

```bash
blossomer init acme.com  # when project already exists
```

**Output:**

```
⚠️  Project already exists: gtm_projects/acme.com/

What would you like to do?
[V]iew existing analysis
[U]pdate specific steps
[O]verwrite everything
[A]bort

Choice [V/u/o/a]: U

Which step to update?
1. Company overview
2. Target account
3. Buyer persona
4. Email campaign

Choice [1-4]: 4

✓ Regenerating email campaign...
[continues with step 4 flow]

```

### 2. `blossomer show [asset]`

Display generated assets with formatting.

### **2.1 Show All Assets**

**Input:**

```bash
blossomer show all
```

**Output:**

```
📊 GTM Assets for acme.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 COMPANY OVERVIEW
[Full formatted display of company analysis]

🎯 TARGET ACCOUNT
[Full formatted display of account profile]

👤 BUYER PERSONA
[Full formatted display of persona]

✉️ EMAIL CAMPAIGN
[Full formatted display of email]

📋 GTM EXECUTION PLAN
[Full formatted display of 30-day plan]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 5 assets generated

```

### **2.2 Show Specific Asset**

**Input:**

```bash
blossomer show overview  # or: account, persona, email, all
# Note: 'plan' not yet available
```

Shows just the requested section with appropriate formatting.

### **2.3 Show as JSON**

**Input:**

```bash
blossomer show account --json
```

Outputs the raw JSON for programmatic use.

### 3. `blossomer export` ✅ IMPLEMENTED

Export GTM assets as beautifully formatted markdown reports for sharing and documentation.

**Features:**
- **Individual step export**: Export specific GTM steps (overview, account, persona, email)
- **Complete report export**: All steps combined into a comprehensive report
- **Professional formatting**: Clean markdown with headers, tables, lists, and code blocks
- **Smart filename generation**: Meaningful names with domain and date

**Input Options:**

```bash
# Export specific step
blossomer export overview
blossomer export account  
blossomer export persona
blossomer export email

# Export all steps as complete report
blossomer export all

# Export with custom filename
blossomer export overview --output my-analysis.md
blossomer export all --output gtm-complete-report.md

# Export current directory (auto-detect domain)
blossomer export all --output ./reports/
```

**Sample Output:**

```bash
📄 Exporting GTM assets for blossomer.io...
✅ Company Overview exported: OVERVIEW-blossomer-io-2025-01-15.md
✅ Target Account exported: ACCOUNT-blossomer-io-2025-01-15.md  
✅ Buyer Persona exported: PERSONA-blossomer-io-2025-01-15.md
✅ Email Campaign exported: EMAIL-blossomer-io-2025-01-15.md

📋 Complete report saved to: REPORT-blossomer-io-2025-01-15.md (12.5KB)
   Preview: file:///Users/user/gtm_projects/blossomer.io/export/REPORT-blossomer-io-2025-01-15.md
```

**Markdown Output Format:**

Each export includes:
- **Headers**: Structured hierarchy (##, ###, ####)
- **Tables**: Firmographics, demographics, buying signals  
- **Lists**: Insights, capabilities, rationale, goals
- **Code blocks**: Email content with segment annotations
- **Metadata**: Generation details, confidence levels, processing notes
- **Stale data warnings**: When dependencies have been regenerated

**Use Cases:**
- **Share with stakeholders**: Send formatted reports to team members
- **Client presentations**: Professional documentation for prospects
- **Archive analysis**: Save snapshots of GTM intelligence
- **Integration workflows**: Import into other documentation systems

### 4. `blossomer generate <step>`

Manually run or re-run a specific step.

**Input:**

```bash
blossomer generate email
```

**Output:**

```
✉️ Regenerating email campaign...

[Shows same interactive flow as step 4 in init]

```

**Available steps:**

- `overview` / `company`
- `account`
- `persona`
- `email`
- `plan` (not yet implemented)

### 5. `blossomer edit <file>` (NOT YET IMPLEMENTED)

Open a generated file in the system's default editor.

**Input:**

```bash
blossomer edit account
# Currently shows: "Command not yet implemented"
```

**Output:**

```
Opening account.json in your default editor...
[User makes changes and saves]

✓ Changes saved to account.json

What would you like to do?
[R]egenerate dependent steps (persona, email, plan)
[C]ontinue without regenerating
[Q]uit

Choice [R/c/q]: R

Regenerating dependent assets...
[3/4] 👤 Regenerating persona... done
[4/4] ✉️ Regenerating email... done

Note: GTM plan regeneration not yet available

✅ All available dependent assets updated!

```

### 6. `blossomer list` (NOT YET IMPLEMENTED)

Show all GTM projects.

**Input:**

```bash
blossomer list
# Currently shows: "Command not yet implemented"
```

**Output:**

```
📁 GTM Projects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

acme.com
  Created: 2024-01-15 14:30
  Modified: 2024-01-15 15:45
  Status: ✅ Complete (4/4 steps)

techflow.io
  Created: 2024-01-14 09:15
  Modified: 2024-01-14 09:22
  Status: ⚠️ Partial (3/4 steps)
  Missing: email

dataops.ai
  Created: 2024-01-13 16:45
  Modified: 2024-01-13 17:10
  Status: ✅ Complete (4/4 steps)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 projects (2 complete, 1 partial)

**Note: Currently shows 'Command not yet implemented'**

```

## Guided Email Setup Implementation - ✅ IMPLEMENTED

### Implementation Status

**✅ COMPLETED** - The guided email setup has been fully implemented and integrated into the CLI:

- ✅ **5-Step Interactive Flow**: Use Case/Pain Point/Capability/Desired Outcome selection + Social Proof collection
- ✅ **Dynamic Content Extraction**: Pulls from target_persona.json use_cases and buying_signals arrays
- ✅ **Custom Instructions Support**: "Other" option with custom LLM instructions for steps 2 & 3
- ✅ **Template Integration**: Updated email_generation_blossomer.jinja2 to handle guided mode
- ✅ **CLI Integration**: Seamlessly integrated into init command flow
- ✅ **Dynamic Array Sizing**: Handles variable array sizes with proper numbering

### Implementation Details

#### Files Modified:
- **`cli/utils/guided_email_builder.py`**: Complete 5-step guided flow implementation (added social proof collection)
- **`app/prompts/templates/email_generation_blossomer.jinja2`**: Added guided mode template logic
- **`cli/commands/init_sync.py`**: Already had guided flow integration

#### User Prompt Variables for Email Generation

The email generation prompt now supports these guided mode variables:

```json
{
  "guided_mode": true,
  "emphasis": "use_case|pain_point|capability|desired_outcome",
  "selected_content": {
    "type": "use_case|pain_point|capability|desired_outcome", 
    "value": "Selected content from target_persona.json arrays",
    "description": "Full description of selected content",
    "custom_instructions": "Optional custom LLM instructions if user selected 'Other'",
    "custom": false
  },
  "personalization": {
    "type": "buying_signal|custom",
    "title": "Selected buying signal title",
    "example": "Example personalization approach",
    "custom_instructions": "Optional custom LLM instructions if user selected 'Other'",
    "custom": false
  },
  "social_proof": "Optional user-provided social proof text",
  "call_to_action": {
    "type": "meeting|priority_check|feedback|free_help|resource|custom",
    "text": "Selected CTA text",
    "intent": "schedule_meeting|gauge_interest|start_conversation|provide_value|share_content|custom_action",
    "custom": false
  }
}
```

#### Data Flow from Target Persona Step

The implementation extracts data from target_persona.json:

- **use_cases[]**: Extracts `use_case`, `pain_point`, `capability`, `desired_outcome` fields
- **buying_signals[]**: Extracts `title`, `description` for personalization options
- **Fallback defaults**: Provides sensible defaults when persona data is incomplete

#### Dynamic Implementation Features

✅ **Variable Array Handling**: Supports any number of options from persona data
✅ **Unique Content Filtering**: Prevents duplicate options in selection lists  
✅ **Graceful Fallbacks**: Uses default options when persona data is missing
✅ **Custom Instructions**: Full LLM customization when "Other" is selected
✅ **Dynamic Numbering**: Options are numbered based on actual array length

### Step-by-Step Implementation Logic

1. **Emphasis Selection**: User picks from 4 options (use_case, pain_point, capability, desired_outcome)
2. **Content Selection**: Shows filtered options from use_cases array based on emphasis choice + "Other" option
3. **Social Proof Collection**: Optional text input for social proof (can be skipped)
4. **Personalization**: Shows buying_signals array options + "Other" option for custom instructions
5. **Call-to-Action**: Shows 5 predefined CTA types + "Other" option for custom text

### UI/UX Improvements

✅ **Clean Display Formatting**: 
- **Step 2**: Shows only content after colon (e.g., "Faster lead engagement, increased outreach" instead of full verbose descriptions)
- **Step 3**: Shows only text before colon (e.g., "Recent Series B funding" instead of full personalization examples)
- **Hardcoded CTAs**: Fixed CTA options for consistent experience across all sessions

✅ **Enhanced User Experience**:
- Clean, readable option lists without overwhelming detail
- Consistent numbering that adapts to actual data array sizes
- Professional presentation that matches CLI design standards

### Testing Results

✅ **Content Extraction**: All emphasis types correctly extract unique options from persona data
✅ **Dynamic Sizing**: Handles arrays of any size with proper numbering
✅ **Fallback Behavior**: Provides defaults when persona data is missing
✅ **Template Integration**: Guided mode variables correctly passed to email generation template
✅ **UI Formatting**: Clean, readable displays without verbose text clutter

## Prompt Updates Required

To support the CLI summary feature, each prompt template needs to generate an additional `cli_summary` field:

```json
{
  // ... existing fields ...
  "cli_summary": {
    "title": "Short descriptive title",
    "key_points": [
      "Bullet point 1",
      "Bullet point 2",
      "Bullet point 3"
    ],
    "metrics": {
      "key1": "value1",
      "key2": "value2"
    }
  }
}

```

This allows the CLI to show meaningful previews without overwhelming users with the full JSON output.

## Global Options

Available for all commands:

- `-help, -h` - Show command help
- `-version, -v` - Show CLI version  
- `-quiet, -q` - Minimal output
- `-verbose` - Detailed output with timings
- `-no-color` - Disable colored output
- `-yolo` - Skip all interactions (one-shot mode)

### New Quality-of-Life Commands

#### `blossomer status` (NOT YET IMPLEMENTED)
Quick overview of all projects:
```
acme.com: ✅ Complete (4/4) • techflow.io: ⚠️ Partial (3/4)
# Currently shows: "Command not yet implemented"
```

#### Smart Editor Detection
- Auto-detects `$EDITOR` environment variable
- Falls back to common editors: VS Code, vim, nano
- Configurable via `blossomer config editor code` (not yet implemented)

## Error Handling

### Generation Failures with Recovery

```
❌ Could not generate persona
   → Error: Insufficient context from previous steps
   → Try: Add more company details in overview.json
   → Or: blossomer init acme.com --context "Series A startup building AI tools"

Options:
[R]etry generation
[E]dit account.json to add context
[S]kip this step
[A]bort

Choice [R/e/s/a]: E

Opening account.json in your default editor...

```

### API Key Issues

```
❌ Error: OpenAI API rate limit reached

You've hit your API rate limit. Options:
1. Wait 60 seconds and retry
2. Switch to a different API key
3. Continue with existing assets

Choice [1/2/3]: 1

Waiting 60 seconds... [progress bar]
✓ Retrying generation...

```

## File Storage Structure

```
gtm_projects/
├── acme.com/
│   ├── overview.json      # Company analysis
│   ├── account.json       # Target account profile
│   ├── persona.json       # Buyer persona
│   ├── email.json         # Email campaign
│   ├── plan.json          # GTM execution plan
│   ├── .metadata.json     # Generation metadata
│   └── export/
│       └── gtm-report-2024-01-15.md
└── .gtm-cli-state.json    # Global state/preferences

```

## Success Metrics

The CLI should:

- Generate initial assets in under 30 seconds
- Provide meaningful summaries that let users decide whether to edit
- Make editing seamless with system editor integration
- Guide users naturally through the 5-step flow
- Generate actionable GTM plans that users can immediately execute
- Handle errors gracefully with clear recovery options

# Tech Stack

## Typer

**Why Typer over Click:**

- Built on Click but with **type hints** (perfect match for your Pydantic models)
- **Auto-completion** out of the box
- Cleaner syntax that matches your FastAPI style
- Better **help generation** from docstrings
- Native support for **subcommands** and **command groups**

## Rich (Console Formatting)

**Why Rich:**

- Creates the **beautiful formatted output** shown in your specs
- Progress bars, tables, panels, syntax highlighting
- **Markdown rendering** in the terminal
- Works great with Typer

## **Questionary** (Interactive Prompts)

**Why Questionary:**

- Beautiful **interactive prompts** that match your UX design
- Better than `input()` or Typer's basic prompts
- Supports the **[c/e/a]** style choices in your spec
- Auto-completion, validation, and styling