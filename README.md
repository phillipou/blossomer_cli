# Blossomer GTM CLI

This CLI tool is a **prototype of the internal AI workflows used at Blossomer**. We've open-sourced it so you can tweak the prompts and systems to work perfectly for your specific needs. Think of it as a peek behind the curtain of how modern GTM intelligence actually works.

**With Blossomer's CLI, you can generate:**

- **Company Overview**: Automatically analyze any website to extract business model, value propositions, and competitive positioning
- **Target Account Profile**: Generate detailed ICP definitions with firmographic criteria and buying signals  
- **Buyer Persona**: Create comprehensive personas with pain points, goals, and purchase journey mapping
- **Email Campaigns**: Build personalized outreach sequences using our proven "Lego Block" methodology
- **Strategic Plan**: Generate complete execution roadmaps with tool recommendations and success metrics

## Quick Start

### Prerequisites

- Python 3.8 or higher
- **Firecrawl API key** - Get one at [firecrawl.dev](https://firecrawl.dev) for website scraping
- **TensorBlock API key** - Get one at [tensorblock.co](https://tensorblock.co) for AI model access (supports 19+ models including GPT-4, Claude, Gemini)

### Installation

```bash
# Clone and install
git clone https://github.com/phillipou/blossomer_cli.git
cd blossomer_cli
make install

# Set up your API keys
export FIRECRAWL_API_KEY="your-firecrawl-key-here"
export FORGE_API_KEY="your-tensorblock-key-here"

# Generate your first GTM package
blossomer init <your-company-website>
```

**What you'll see:**
```
🚀 Installing Blossomer CLI...
✅ Installation complete!

🎯 Try it out:
   blossomer init stripe.com
```

## Concepts

### Project Organization
Projects are **named after the domain of the company's website**. When you run `blossomer init stripe.com`, it creates a project folder called `stripe.com` that contains all the generated GTM assets for that company.

```
gtm_projects/
├── stripe.com/          # Project for Stripe
├── shopify.com/         # Project for Shopify  
├── notion.so/           # Project for Notion
└── your-company.com/    # Project for your company
```

This makes it easy to:
- **Work on multiple companies** simultaneously
- **Switch between projects** using `--domain` flags
- **Organize your GTM research** by company
- **Share specific company analyses** as needed

### Project Structure

Generated projects are organized like this:

```
gtm_projects/
├── stripe.com/
│   ├── .metadata.json        # Project metadata
│   ├── plans/                # Human-readable markdown files
│   │   ├── overview.md       # Company analysis
│   │   ├── account.md        # Target account profile
│   │   ├── persona.md        # Buyer persona
│   │   ├── email.md          # Email campaigns
│   │   └── strategy.md       # Strategic execution plan
│   └── json_output/          # Raw data (for integrations)
└── acme.com/
    └── ...
```

### The 5-Step GTM Generation Process
1. **Company Overview**: Scrapes and analyzes the website to understand business model and positioning
2. **Target Account Profile**: Defines ideal customer profile with buying signals and firmographic criteria
3. **Buyer Persona**: Creates detailed personas with pain points, goals, and decision-making process
4. **Email Campaigns**: Generates personalized outreach using proven messaging frameworks
5. **Strategic Plan**: Builds complete execution roadmap with tools, metrics, and prioritization

Each step builds on the previous ones, creating a comprehensive GTM package that's immediately actionable.

## Examples

### Generate Complete GTM Package

```bash
# Interactive mode (recommended)
blossomer init acme.com

# Skip prompts and generate everything
blossomer init acme.com --yolo

# With additional context
blossomer init acme.com --context "Series A SaaS startup"
```

### View Your Generated Assets

```bash
# Show all generated content
blossomer show all

# View specific components
blossomer show overview     # Company analysis
blossomer show account      # Target account profile  
blossomer show persona      # Buyer persona
blossomer show email        # Email campaigns
blossomer show plan         # Strategic execution plan

# Export as markdown report
blossomer export all
```

### Regenerate Specific Components

```bash
# Regenerate email campaign
blossomer generate email

# Force regenerate company overview
blossomer generate overview --force

# Regenerate with specific domain
blossomer generate persona --domain acme.com
```

### Manage Multiple Projects

```bash
# List all your GTM projects
blossomer list

# View specific project files
blossomer list --domain acme.com

# Switch between projects
blossomer show overview --domain stripe.com
```

### Edit and Customize

```bash
# Open generated content in your default editor
blossomer edit overview
blossomer edit persona
blossomer edit email
```

## Example Workflow

```bash
$ blossomer init stripe.com
🔍 Analyzing stripe.com...
   → Fetching website content... ✓
   → Processing with AI... ✓
   → Company overview generated (12s)

📋 Target Account Analysis...
   → Analyzing market positioning... ✓
   → Identifying key segments... ✓
   → Account profile generated (8s)

👤 Buyer Persona Development...
   → Analyzing decision makers... ✓
   → Building persona profile... ✓
   → Persona generated (6s)

✉️ Email Campaign Creation...
   → Crafting personalized messaging... ✓
   → Email campaign generated (5s)

📊 Strategic Plan Generation...
   → Building execution roadmap... ✓
   → Strategic plan generated (10s)

✅ Complete GTM package generated for stripe.com (5/5 steps)

$ blossomer show all
# Displays beautifully formatted GTM package...

$ blossomer export all
✅ Complete GTM package exported: REPORT-stripe-2025-01-21.md (127.3KB)
```

## Global Options

```bash
--verbose          # Enable detailed timing and progress info
--debug           # Show cache hits and debugging details
--quiet, -q       # Minimal output mode
--no-color        # Disable colored output
--version, -v     # Show version information
--help           # Display help for any command
```

## Uninstall

```bash
# Remove the package
pip uninstall blossomer-gtm-cli

# Clean up project data (optional)
rm -rf gtm_projects/
```

## Configuration

Set up your environment variables:

```bash
# Required API keys
export FIRECRAWL_API_KEY="your-firecrawl-key"
export FORGE_API_KEY="your-tensorblock-key"

# Optional settings
export BLOSSOMER_DEBUG=true           # Enable debug output
export BLOSSOMER_QUIET=true          # Minimal output mode
```

Add these to your `~/.bashrc`, `~/.zshrc`, or create a `.env` file in the project directory.


## Next Steps

This is of course just the tip of the iceberg! There's so much more to dive into including:
- How to incorporate other channels (LinkedIn, inbound leads, paid advertising)?
- How to analyze data and iterate on these campaigns?
- How to integrate this into your CRM and workflows?

If you need any additional help or want us to work with you hands-on, reach out to us at [blossomer.io](https://blossomer.io) or contact our founder Phil (phil@blossomer.io).

## License

MIT License - feel free to fork, modify, and use this however works best for your team.

---

*Built by the Blossomer team to democratize AI-driven GTM intelligence. Now go build something amazing!* 🚀
