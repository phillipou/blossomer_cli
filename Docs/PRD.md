# Blossomer GTM CLI Tool - PRD

## Overview

A lightweight CLI tool that demonstrates Blossomer's GTM intelligence by analyzing a company domain and generating a complete go-to-market package. The tool runs locally, stores outputs as JSON files, and provides an interactive experience for technical founders.

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

## The 5-Step Flow

1. **Company Overview** → 2. **Target Account** → 3. **Buyer Persona** → 4. **Email Campaign** → 5. **GTM Plan**

## Detailed Command Specifications

### 1. `gtm-cli init <domain>`

The primary command that runs the complete GTM pipeline.

### **1.1 Interactive Mode (Default)**

**Input:**

```bash
gtm-cli init acme.com

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
[3/5] 👤 Building buyer persona... done (6s)

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
[C]ontinue to next step
[E]dit full persona in editor
[A]bort

Choice [c/e/a]: C

```
Step 3 - Buyer Persona:
[3/5] 👤 Building buyer persona... done (6s)

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

Step 1/4: What should your email emphasize?

1. Pain Point: Focus on challenges they're experiencing
2. Capability: Focus on what your solution can do
3. Desired Outcome: Focus on the results they want

Select emphasis [1-3]: 1
✓ Focusing on pain points
Email Guide Step 2: Select Specific Pain Point
Step 2/4: Which pain point should we focus on?

Based on your persona analysis, here are their key pain points:

1. Maintaining support quality during rapid scaling
   "As teams grow from 10 to 50 agents, consistency drops"

2. Long agent onboarding times  
   "New agents take 6+ weeks to reach full productivity"

3. Lack of visibility into knowledge gaps
   "No way to identify what agents don't know until customers complain"

4. Other (specify your own)

Select pain point [1-4]: 1
✓ Selected: Quality challenges during scaling
Email Guide Step 3: Select Personalization Angle
Step 3/4: How should we personalize this email?

Based on your target account analysis:

1. No personalization (generic approach)

2. Reference recent Series B funding
   "Congrats on the Series B - scaling challenges ahead?"

3. Reference hiring spree  
   "Saw you're hiring 10+ support agents this quarter"

4. Reference company growth metrics
   "With 200% YoY growth, support must be challenging"

5. Other (specify your own)

Select personalization [1-5]: 2
✓ Will reference Series B funding
Email Guide Step 4: Select Call-to-Action
Step 4/4: What should the call-to-action be?

1. Ask for a meeting
   "Worth a quick 15-min call next week?"

2. Ask if it's a priority  
   "Is improving support efficiency a Q1 priority?"

3. Ask for feedback
   "Curious if this resonates with your experience?"

4. Offer free help
   "Happy to share our scaling playbook - interested?"

5. Invite to resource
   "We have a guide on this - should I send it over?"

Select CTA [1-5]: 1

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
[C]ontinue to GTM plan
[E]dit full campaign in editor
[A]bort

Choice [c/e/a]: C

Step 4 - Email Campaign (Automatic Mode):
[If user selected [A]utomatic at the persona step]

[4/5] ✉️ Auto-generating email campaign... done (4s)

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
[C]ontinue to GTM plan
[E]dit full campaign in editor
[A]bort

Choice [c/e/a]: C


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

✅ GTM assets complete! Created in: gtm_projects/acme.com/
   Total time: 30 seconds • Total cost: ~$0.15

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
gtm-cli init acme.com --yolo

```

**Output:**

```
🚀 YOLO Mode - Generating everything at once!

[1/5] 🔍 Analyzing company... done (8s)
[2/5] 🎯 Generating target account... done (5s)
[3/5] 👤 Building buyer persona... done (6s)
[4/5] ✉️  Creating email campaign... done (4s)
[5/5] 📋 Creating GTM plan... done (7s)

✅ Complete! All assets created in: gtm_projects/acme.com/

Quick Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: AI-powered QA for support teams
Target: FinTech companies (100-500 employees)
Persona: VP of Customer Success
Email: "reduce support resolution time?"
Plan: 30-day execution roadmap ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review everything: gtm-cli show all

```

### **1.3 With Additional Context**

**Input:**

```bash
gtm-cli init acme.com --context "We're a Series A startup building AI tools for customer support teams"

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
gtm-cli init acme.com  # when project already exists

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
5. GTM plan

Choice [1-5]: 4

✓ Regenerating email campaign...
[continues with step 4 flow]

```

### 2. `gtm-cli show <asset>`

Display generated assets with formatting.

### **2.1 Show All Assets**

**Input:**

```bash
gtm-cli show all

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
gtm-cli show plan  # or: overview, account, persona, email

```

Shows just the requested section with appropriate formatting.

### **2.3 Show as JSON**

**Input:**

```bash
gtm-cli show account --json

```

Outputs the raw JSON for programmatic use.

### 3. `gtm-cli export`

Export all assets as a single markdown report.

**Input:**

```bash
gtm-cli export

```

**Output:**

```
📄 Exporting GTM assets...
✅ Report saved to: gtm_projects/acme.com/export/gtm-report-2024-01-15.md

Preview: file:///.../gtm-report-2024-01-15.md

```

The markdown includes all 5 sections in a clean, shareable format.

### 4. `gtm-cli generate <step>`

Manually run or re-run a specific step.

**Input:**

```bash
gtm-cli generate email

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
- `plan`

### 5. `gtm-cli edit <file>`

Open a generated file in the system's default editor.

**Input:**

```bash
gtm-cli edit account

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
[3/5] 👤 Regenerating persona... done
[4/5] ✉️ Regenerating email... done
[5/5] 📋 Regenerating plan... done

✅ All dependent assets updated!

```

### 6. `gtm-cli list`

Show all GTM projects.

**Input:**

```bash
gtm-cli list

```

**Output:**

```
📁 GTM Projects
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

acme.com
  Created: 2024-01-15 14:30
  Modified: 2024-01-15 15:45
  Status: ✅ Complete (5/5 steps)

techflow.io
  Created: 2024-01-14 09:15
  Modified: 2024-01-14 09:22
  Status: ⚠️  Partial (3/5 steps)
  Missing: email, plan

dataops.ai
  Created: 2024-01-13 16:45
  Modified: 2024-01-13 17:10
  Status: ✅ Complete (5/5 steps)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 3 projects (2 complete, 1 partial)

```

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

#### `gtm-cli status`
Quick overview of all projects:
```
acme.com: ✅ Complete (5/5) • techflow.io: ⚠️ Partial (3/5)
```

#### Smart Editor Detection
- Auto-detects `$EDITOR` environment variable
- Falls back to common editors: VS Code, vim, nano
- Configurable via `gtm-cli config editor code`

## Error Handling

### Generation Failures with Recovery

```
❌ Could not generate persona
   → Error: Insufficient context from previous steps
   → Try: Add more company details in overview.json
   → Or: gtm-cli init acme.com --context "Series A startup building AI tools"

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