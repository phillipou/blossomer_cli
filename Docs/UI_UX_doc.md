# CLI User Experience Documentation

## Design Philosophy

Based on the PRD specifications, the CLI follows these core principles:
- **60-second value**: Generate complete GTM assets from domain to email in under a minute
- **Interactive by default**: Guide users through refinement at each step
- **Progressive disclosure**: Start simple, reveal complexity only when needed
- **Local-first**: No authentication, no cloud dependencies, just files on disk

## Detailed User<>CLI Interactions

### Primary Command: `gtm-cli init <domain>`

#### Interactive Mode (Default Flow)

**Startup and Step 1 - Company Overview:**
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
[R]egenerate with changes
[A]bort (or press Ctrl+C)

Choice [C/e/r/a]: 
```

**User chooses [E]dit - Editor Integration:**
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
[R]egenerate with changes
[A]bort

Choice [C/e/r/a]: 
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
[R]egenerate with changes
[A]bort

Choice [C/e/r/a]: 
```

**Step 4 - Email Campaign:**
```
[4/5] ✉️  Creating email campaign... done (4s)

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
• "support scaling challenges at {{Company}}?"
• "40% faster ticket resolution - interested?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full campaign saved to: email.json (2.8KB)

Options:
[C]ontinue to GTM plan
[E]dit full campaign in editor
[R]egenerate with changes
[A]bort

Choice [C/e/r/a]: 
```

**Step 5 - GTM Plan:**
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

#### YOLO Mode (One-Shot Generation)

**Input:** `gtm-cli init acme.com --yolo`

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

#### Existing Project Handling

**Input:** `gtm-cli init acme.com` (when project exists)

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

### Secondary Commands

#### Show Command: `gtm-cli show <asset>`

**Show All Assets:**
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

**Show Specific Asset:** `gtm-cli show plan`
Shows just the GTM plan section with formatting.

**Show as JSON:** `gtm-cli show account --json`
Outputs raw JSON for programmatic use.

#### Export Command: `gtm-cli export`

**Output:**
```
📄 Exporting GTM assets...
✅ Report saved to: gtm_projects/acme.com/export/gtm-report-2024-01-15.md

Preview: file:///.../gtm-report-2024-01-15.md
```

#### List Command: `gtm-cli list`

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

#### Edit Command: `gtm-cli edit <file>`

**Input:** `gtm-cli edit account`

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

## Error Handling Interactions

#### Generation Failures
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

#### API Rate Limits
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

## Global Options

Available for all commands:
- `-help, -h` - Show command help
- `-version, -v` - Show CLI version
- `-quiet, -q` - Minimal output
- `-verbose` - Detailed output with timings
- `-no-color` - Disable colored output
- `-yolo` - Skip all interactions (one-shot mode)

## Quality-of-Life Enhancements

### Smart Domain Handling
- Auto-normalizes various formats: `acme.com`, `www.acme.com`, `https://acme.com/about`
- Validates accessibility before proceeding
- Clear error messages for invalid domains

### Editor Integration
- Auto-detects `$EDITOR` environment variable
- Smart fallbacks: VS Code (`code`), vim, nano
- Configurable via user preferences

### Progress Indicators
- Micro-progress for each step: `→ Fetching website... ✓`
- Real-time timing information
- Total time and cost summary

### Copy-Paste Friendly Output
- Ready-to-use commands at completion
- Consistent file naming with timestamps
- Integration hints for common next steps

### Status Command
**Input:** `gtm-cli status`
**Output:**
```
acme.com: ✅ Complete (5/5) • techflow.io: ⚠️ Partial (3/5)
```

## Future Considerations

Ideas that could enhance the CLI but are beyond current scope:
- Custom prompt templates
- Batch processing multiple domains
- Integration with external tools (Clay, Apollo)
- Advanced error recovery workflows
- Webhook notifications
- Team collaboration features
- Version control for projects
- Analytics and usage tracking

## Key UX Requirements for Implementation

1. **Exact formatting**: Match the PRD's visual output exactly
2. **Choice patterns**: Implement [C/e/r/a] style interactions with keyboard shortcuts
3. **Micro-progress**: Show detailed progress states (→ Fetching... ✓, → Processing... ✓)
4. **File feedback**: Always show file sizes and save locations
5. **Smart defaults**: Domain normalization, editor detection, meaningful file names
6. **Editor integration**: Seamless handoff to user's preferred editor with auto-detection
7. **Dependency tracking**: Offer regeneration when earlier steps change
8. **Project state**: Handle existing projects with clear options
9. **Error recovery**: Provide actionable recovery with specific next steps (→ Try: ..., → Or: ...)
10. **Technical founder UX**: Time-to-value metrics, cost tracking, copy-paste commands
11. **CLI conventions**: Consistent exit codes, respects standard flags, pipe-friendly JSON output