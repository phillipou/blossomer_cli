# Bug Tracking
-[] This will analyze your website and generate your GTM plan.
-[x] for [y/n] question and answers, enter should default to y. In some areas, it's an invalid input
    - **Root Cause**: questionary.confirm() and typer.confirm() were using default=None instead of default=True
    - **Fix**: Changed all confirm prompts to use default=True in init.py, generate.py, preview_utils.py, and init_sync.py
    - **Additional Fix**: Found and fixed typer.confirm() calls that were missed in initial pass
-[x] "Company Overview file not found" when user elects to edit after preview. Should launch the markdown file and allow user to eidt
    - **Root Cause**: edit_step_content was looking for .json files instead of .md files in the plans/ directory
    - **Fix**: Updated to look for markdown files in plans/ directory and show helpful error if not found
    - **Note**: Markdown generation is handled automatically by _auto_generate_plans_file when JSON is saved
-[x] "What would you like to do?" -> add the ability to select option by hitting 1,2,3
    - **Root Cause**: Questionary doesn't have shortcuts enabled by default, all menus used plain choices
    - **Final Fix**: Used questionary.Choice with shortcut_key parameter and use_shortcuts=True
    - **Functionality**: Supports BOTH arrow key navigation AND number key shortcuts (1-9)
    - **Implementation**: Creates Choice objects with shortcut_key and enables use_shortcuts in select()
    - **User Experience**: Navigate with arrows OR press numbers (1-9) directly for instant selection
-[x] text like "Full buyer persona saved to json_output/persona.json" -> should instead point to the markdown file (e.g. persona.md)
    - **Root Cause**: File save messages were referencing JSON files instead of markdown files
    - **Fix**: Updated preview_utils.py to show markdown file paths (plans/{step}.md) instead of JSON paths
-[x] replace cyan wth the nice blue/purple in "Guide Email Builder" title
    - **Root Cause**: Panel was using default blue border style without specific title coloring
    - **Fix**: Changed title to use blue_violet color and border_style to match

## Guided Email Builder
-[x] numbered selection doesn't work for guided email builder
    - **Root Cause**: Guided email builder was manually adding numbers to choices
    - **Fix**: Updated all steps to use show_menu_with_numbers() and fixed index-based selection logic
-[x] No Personalization sould be first option in step 4
    - **Root Cause**: "No Personalization" was added last in the choices list
    - **Fix**: Reordered choices to put "No Personalization" first, updated selection logic accordingly

## Completion Experience
-[x] Seeing "✓ GTM Strategic Plan generated successfully" and also "No data found for GTM Strategic plan"
    - **Root Cause**: Completion panel was trying to show preview that might fail if markdown wasn't generated
    - **Fix**: Updated completion UX to show cleaner options without attempting preview
-[x] Update GTM Generation Complete UX to only show 2 options `blossomer show plan` and `blossomer edit [overview|account|persona|email|plan]` 
    - **Root Cause**: Completion panel showed outdated commands (show all, export)
    - **Fix**: Updated panel_utils.py to show only 'blossomer show plan' and 'blossomer edit [step]'
    -[x] should show "View results: blossomer show plan" command will open the editor to show them the strategic_plan.md. If they have multiple projects, it' should default to the current project
        - **Fix**: Updated completion panel and implemented auto-detection in commands
    -[x] `blossomer edit [overview|account|persona|email|plan]` let's you edit the corresponding .md file
        - **Fix**: Implemented edit_step.py command with domain auto-detection

## Blossomer CLI Commands
-[x] Implement `blossomer list` show all GTM projects
    - **Implementation**: Created list_projects.py with table view of all projects, status, and file counts
-[x] steps can be defined as overview, account, persona, email, plan (e.g. `blossomer edit --domain blossomer.io --step overview`)
    - **Implementation**: Updated all commands to use consistent step names
-[x] implement `blossomer edit --domain <domain> --step <step>` opens markdown of step in editor
    - **Implementation**: Created edit_step.py with domain auto-detection and markdown generation from JSON
-[x] implement `blossomer list --domain <domain>` shows all the created .md files of the project plan
    - **Implementation**: Added --domain flag to list command showing project files with details
-[x] implement `blossomer show --domain <domain> --step <step>` to show .md file
    - **Implementation**: Updated show command to use step parameter with domain auto-detection
-[x] remove all other commands besides init, list, and show for simplicity
    - **Implementation**: Removed generate, export, status commands and eval/plans/advisor subcommands from main.py
