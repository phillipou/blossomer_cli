# Bidirectional JSON ↔ Markdown Sync System

**Experiment Status:** 🚧 Design Phase  
**Created:** January 18, 2025  
**Objective:** Enable users to edit human-readable markdown files that sync back to JSON data

## Problem Statement

The CLI generates JSON files (`json_output/`) that are the source of truth, but they're not user-friendly for editing. We want to enable:

1. **Human-readable editing** - Technical founders can edit markdown instead of JSON
2. **Bidirectional sync** - Changes in markdown automatically update JSON (and vice versa)
3. **Workflow continuity** - CLI continues working normally with JSON as source of truth
4. **Graceful degradation** - Sync issues don't block user workflow

## Architecture Design

### File Structure
```
gtm_projects/{domain}/
├── json_output/           # Canonical data (CLI source of truth)
│   ├── overview.json
│   ├── account.json
│   └── persona.json
├── plans/                 # Human-editable markdown files  
│   ├── overview.md
│   ├── account.md
│   ├── persona.md
│   └── .sync_state.json   # Sync metadata tracking
└── export/               # Final reports
    └── gtm-report-{date}.md
```

### The 3-Way Relationship
```
JSON (Source of Truth) ←→ Plans (Editable) → Export (Final)
     ↑                        ↓                ↓
     └── CLI generates ────── User edits ──── Reports
```

## Field Marker System

### Structured Markdown with Sync Headers
Every generated markdown file includes a sync notice and field markers:

```markdown
<!-- 
🔄 SYNC NOTICE: This file syncs with JSON data
⚠️  DO NOT remove the {#field_name} markers - they enable syncing back to JSON
✏️  Feel free to edit content, change headers, add sections - just keep the markers!
📝 Generated: 2025-01-18 10:30 AM from json_output/overview.json
-->

# Acme Corp - Company Analysis

## Business Insights {#business_profile_insights}
- Cloud-first SaaS platform for enterprise workflow automation
- Focus on compliance-heavy industries (finance, healthcare)
- Modular architecture enables rapid customer customization

## Key Capabilities {#capabilities}
- Real-time data synchronization across systems
- Advanced audit trail and compliance reporting

## My Custom Analysis
- User-added content without markers
- Will be preserved but not synced to JSON
```

### Field Marker Benefits
✅ **Minimal visual noise**: `{#field_name}` syntax  
✅ **Header flexibility**: Users can change header text and levels  
✅ **Clear boundaries**: Parser knows where each field starts/ends  
✅ **User additions**: Content without markers is preserved  
✅ **Reliable parsing**: Handles user edits gracefully  

## Core Sync Operations

### 1. Generate Plans (`json → plans`)
```bash
blossomer plans generate overview
blossomer plans generate all
```

**Process:**
1. Load `json_output/overview.json`
2. Use existing `OverviewFormatter` with field markers
3. Generate `plans/overview.md` with structured content
4. Update `.sync_state.json` with timestamps/hashes

### 2. Update JSON (`plans → json`)
```bash
blossomer plans update overview
blossomer plans update all
```

**Process:**
1. Parse `plans/overview.md` using field markers
2. Extract content between `{#field_name}` markers
3. Reconstruct JSON matching original schema
4. Validate against Pydantic models
5. Write to `json_output/overview.json`
6. Update sync metadata

### 3. Auto-Sync (Smart Detection)
```bash
blossomer plans sync
```

**Smart change detection:**
1. Compare modification times in `.sync_state.json`
2. If `plans/overview.md` newer → sync `plans → json`
3. If `json_output/overview.json` newer → sync `json → plans`
4. If both changed → Conflict resolution

### 4. Edit with Auto-Sync
```bash
blossomer plans edit overview
```

**Integrated workflow:**
1. Generate fresh `plans/overview.md` from current JSON
2. Open in user's default editor
3. When editor closes, automatically sync back to JSON
4. Show what changed

## Resilient Sync: Graceful Field Orphaning

### Philosophy: "Fail Soft, Continue Forward"
**Never block user workflow due to sync issues**

### Orphaning Behavior
When users remove field markers, the system:

✅ **Continues processing** - doesn't stop the whole sync  
✅ **Preserves orphaned content** in markdown  
✅ **Drops orphaned field** from JSON (so CLI continues working)  
✅ **Shows clear warning** but doesn't block user  
✅ **Logs for later recovery** if user wants to fix  

### Example: Partial Sync Success
```markdown
<!-- User removed {#capabilities} marker -->
## Business Insights {#business_profile_insights}
- Cloud-first platform
- Compliance focus

## Capabilities  
- Data sync (MARKER REMOVED!)
- Reporting  

## New Section {#my_custom_field}
- My added content
```

**Sync result:**
```bash
blossomer plans update overview

🔄 Syncing plans/overview.md → json_output/overview.json

✅ business_profile_insights: Updated (2 items)
⚠️  capabilities: ORPHANED - marker missing, field dropped from JSON
ℹ️  my_custom_field: IGNORED - not in JSON schema  
ℹ️  Unmarked content: PRESERVED in markdown

📊 Result: JSON updated successfully with available fields
```

## Field Parsing Logic

### Simple Fields (strings)
```markdown
## Company Description {#description}
Acme Corp builds enterprise workflow automation tools.
```
→ `{"description": "Acme Corp builds enterprise..."}`

### Array Fields (lists)
```markdown
## Business Insights {#business_profile_insights}
- Cloud-first SaaS platform for enterprise workflow automation
- Focus on compliance-heavy industries (finance, healthcare)
- Modular architecture enables rapid customer customization
```
→ `{"business_profile_insights": ["Cloud-first SaaS...", "Focus on compliance...", "Modular architecture..."]}`

### Complex Fields (objects)
```markdown
## Buying Signals {#buying_signals}
**Signal 1: Recent Compliance Audit** (High Priority)
Compliance team actively researching automation tools
*Detection: LinkedIn posts about audit prep, job postings for compliance automation roles*

**Signal 2: Manual Process Pain** (Medium Priority)  
Mentions of manual reporting creating bottlenecks
*Detection: Employee complaints on social media, Glassdoor reviews mentioning manual processes*
```
→ Parse into structured `buying_signals` array with title, priority, description, detection_method

## Recovery Mechanisms

### Option 1: Regenerate with Merge
```bash
blossomer plans generate overview --merge
```
- Generate fresh markdown from current JSON
- Preserve user-added sections without markers
- Restore missing field markers
- Keep user's custom content

### Option 2: Manual Marker Restoration
```bash
blossomer plans repair overview
```
- Scan markdown for content that looks like known fields
- Suggest adding markers back interactively

### Option 3: Rollback
```bash
blossomer plans rollback overview
```
- Restore from `.backup/` directory
- Return to last known good state

## Sync State Tracking

### `.sync_state.json` Structure
```json
{
  "overview": {
    "last_sync": "2025-01-18T10:32:00Z",
    "synced_fields": ["business_profile_insights", "positioning_insights"],
    "orphaned_fields": ["capabilities", "common_objections"],
    "orphan_history": [
      {
        "field": "capabilities", 
        "orphaned_at": "2025-01-18T10:32:00Z",
        "last_content": "- Real-time data sync\n- Audit trail"
      }
    ],
    "json_modified": "2025-01-18T10:30:00Z",
    "plans_modified": "2025-01-18T10:32:00Z",
    "json_hash": "abc123...",
    "plans_hash": "def456...",
    "sync_direction": "plans_to_json"
  }
}
```

## CLI Integration

### New Command Group: `plans`
```bash
blossomer plans generate [step|all]    # json → plans  
blossomer plans update [step|all]      # plans → json
blossomer plans sync [step|all]        # auto-detect changes
blossomer plans edit <step>            # edit with auto-sync
blossomer plans status                 # show sync status
blossomer plans repair <step>          # restore missing markers
blossomer plans rollback <step>        # restore backup
```

### Enhanced Existing Commands
```bash
# Generate now also creates plans
blossomer generate overview
# Now also auto-generates plans/overview.md

# Export with format options
blossomer export overview --format both  # JSON + MD
```

### Workflow Integration
The key insight: **Sync enhances workflow, never breaks it**

```bash
# User generates email after editing persona (with orphaned fields)
blossomer generate email

🔄 Loading persona data...
⚠️  Persona has orphaned fields (buying_signals missing)
✅ Using available persona data to generate email
✅ Email generated successfully

💡 Tip: Run 'blossomer plans repair persona' to restore missing fields
```

**CLI behavior:**
- ✅ Load whatever JSON fields are available
- ✅ Continue with generation using partial data
- ✅ Show friendly warning but don't block
- ✅ Offer easy recovery option

## Implementation Classes

### Core Utilities
```python
# cli/utils/markdown_parser.py
class ResilientMarkdownParser:
    def parse_with_orphan_handling(self, content: str, step_type: str) -> SyncResult
    def extract_marked_sections(self, content: str) -> Dict[str, str]
    def parse_field_content(self, content: str, field_name: str) -> Any

# cli/utils/sync_manager.py  
class SyncManager:
    def sync_project(self, domain: str, step: Optional[str] = None)
    def detect_changes(self, domain: str, step: str) -> SyncState
    def sync_json_to_plans(self, domain: str, step: str)
    def sync_plans_to_json(self, domain: str, step: str)
    def resolve_conflicts(self, domain: str, step: str) -> ConflictResolution

# cli/utils/sync_result.py
class SyncResult:
    synced_fields: Dict[str, Any]
    orphaned_fields: List[str]
    warnings: List[str]
    infos: List[str]
    success_count: int
    
    def is_success(self) -> bool  # True if ANY fields synced
```

### Enhanced Formatter
```python
# Extend existing cli/utils/markdown_formatter.py
class StructuredMarkdownFormatter(MarkdownFormatter):
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """Generate markdown with {#field_name} markers for sync"""
        
    def add_sync_header(self, step_type: str) -> str:
        """Add sync notice warning to top of file"""
```

## Safety Mechanisms

1. **Backup on every sync**: Keep `.backup/` with previous versions
2. **Schema validation**: Ensure parsed data matches Pydantic models
3. **Dry run mode**: `--dry-run` shows what would change
4. **Rollback capability**: Restore last known good state
5. **Orphan preservation**: Never lose user content
6. **Conflict detection**: Handle simultaneous edits gracefully

## Success Metrics

✅ **Never blocks workflow** - CLI always continues with available data  
✅ **Graceful degradation** - Partial sync is better than no sync  
✅ **Clear feedback** - Users understand what happened and how to fix  
✅ **Easy recovery** - Simple commands restore missing pieces  
✅ **Preserves user work** - Custom content never lost  
✅ **Flexible editing** - Users edit freely without fear of breaking things  

## Benefits

### For Users
- ✅ **Human-readable editing** in any markdown editor
- ✅ **Version control friendly** - markdown diffs are readable
- ✅ **Editor agnostic** - works with vim, VS Code, obsidian, etc.
- ✅ **Non-destructive** - always preserves both formats
- ✅ **Flexible** - can add custom sections and notes

### For Development
- ✅ **Incremental implementation** - can build step by step
- ✅ **Extends existing system** - builds on current markdown formatter
- ✅ **Clear mental model** - `json_output` = data, `plans` = editable, `export` = final
- ✅ **Resilient design** - handles edge cases gracefully

## Implementation Priority

1. **✅ Enhanced markdown formatter** - add field markers to existing system
2. **🚧 Markdown parser** - extract field data back to JSON
3. **🚧 Basic sync manager** - handle change detection and sync operations
4. **🚧 CLI integration** - new `plans` command group
5. **🚧 Recovery utilities** - repair, rollback, merge operations
6. **🚧 Testing & validation** - ensure reliability

## Future Enhancements

- **File watching** - auto-sync on file changes
- **Conflict resolution UI** - interactive merge tool
- **Template customization** - user-defined markdown templates
- **Multi-format support** - sync to other formats (YAML, etc.)
- **Collaborative editing** - handle team workflows

---

**Status:** Design complete, ready for implementation  
**Next Step:** Begin with enhanced markdown formatter to add field markers  
**Integration Point:** Reference from main Implementation.md