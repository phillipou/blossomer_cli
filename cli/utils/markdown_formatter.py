"""
JSON-to-Markdown Formatter for Blossomer GTM CLI

This module provides utilities to convert GTM analysis JSON files into well-formatted 
Markdown for both preview display and export functionality.

Use Cases:
1. Preview Mode: Generate truncated, clean markdown for CLI command snippets
2. Export Mode: Generate complete, formatted markdown reports for external use
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import re
from datetime import datetime


class MarkdownHeaderConfig:
    """
    Centralized header hierarchy and formatting configuration.
    
    This class defines all header logic in one place to avoid chasing down
    formatting decisions across multiple files later.
    """
    
    # Header Hierarchy Levels
    DOCUMENT_TITLE = 1      # # Company Name - GTM Analysis
    MAJOR_SECTION = 2       # ## Company Overview, ## Target Account Profile
    SUB_SECTION = 3         # ### Key Insights, ### Firmographics
    DETAIL_SECTION = 4      # #### Pain Points, #### Detection Methods
    
    # Section Headers by Step Type
    SECTION_HEADERS = {
        'overview': {
            'main': 'Company Overview',
            'sub_sections': [
                'Key Insights',
                'Business Capabilities', 
                'Use Case Analysis',
                'Positioning Insights',
                'Common Objections',
                'Target Customers'
            ]
        },
        'account': {
            'main': 'Target Account Profile',
            'sub_sections': [
                'Firmographics',
                'Buying Signals',
                'Targeting Rationale'
            ]
        },
        'persona': {
            'main': 'Buyer Persona',
            'sub_sections': [
                'Demographics',
                'Use Cases',
                'Buying Signals',
                'Goals & Motivations',
                'Common Objections',
                'Purchase Journey'
            ]
        },
        'email': {
            'main': 'Email Campaign',
            'sub_sections': [
                'Subject Lines',
                'Email Structure',
                'Segment Breakdown',
                'Generation Details'
            ]
        }
    }
    
    # Dynamic Header Patterns (use data from JSON)
    DYNAMIC_PATTERNS = {
        'account_name': lambda data: data.get('target_account_name', 'Target Account'),
        'persona_name': lambda data: data.get('target_persona_name', 'Buyer Persona'),
        'company_name': lambda data: data.get('company_name', 'Company'),
        'buying_signal': lambda signal: f"{signal.get('title', 'Signal')} ({signal.get('priority', 'Medium')} Priority)",
        'use_case': lambda case: case.get('use_case', 'Use Case'),
        'email_segment': lambda segment: segment.get('type', 'segment').replace('-', ' ').title()
    }
    
    # Content Prioritization for Preview Mode
    PREVIEW_PRIORITY = {
        'overview': [
            'company_name',
            'description', 
            'business_profile_insights',  # First 3 items
            'capabilities'                # First 2 items
        ],
        'account': [
            'target_account_name',
            'target_account_description',
            'buying_signals'              # First 3 items
        ],
        'persona': [
            'target_persona_name', 
            'target_persona_description',
            'use_cases'                   # First 1 item
        ],
        'email': [
            'subjects.primary',
            'full_email_body'             # Full email body
        ]
    }
    
    # Character Limits by Preview Type
    CHAR_LIMITS = {
        'short': 200,      # Command summaries
        'medium': 500,     # Step previews  
        'long': 1000       # Detailed views
    }
    
    @classmethod
    def get_header(cls, level: int, text: str) -> str:
        """Generate markdown header with proper level."""
        return f"{'#' * level} {text}"
    
    @classmethod
    def get_section_header(cls, step_type: str, preview: bool = False) -> str:
        """Get main section header for a step type."""
        config = cls.SECTION_HEADERS.get(step_type, {})
        main_header = config.get('main', step_type.title())
        
        level = cls.MAJOR_SECTION if not preview else cls.MAJOR_SECTION
        return cls.get_header(level, main_header)
    
    @classmethod
    def get_sub_section_headers(cls, step_type: str) -> List[str]:
        """Get all sub-section headers for a step type."""
        config = cls.SECTION_HEADERS.get(step_type, {})
        sub_sections = config.get('sub_sections', [])
        return [cls.get_header(cls.SUB_SECTION, section) for section in sub_sections]
    
    @classmethod 
    def get_dynamic_header(cls, pattern_name: str, data: Any, level: int = None) -> str:
        """Generate dynamic header from JSON data."""
        if level is None:
            level = cls.MAJOR_SECTION
            
        pattern_func = cls.DYNAMIC_PATTERNS.get(pattern_name)
        if pattern_func:
            text = pattern_func(data)
            return cls.get_header(level, text)
        
        return cls.get_header(level, str(data))


class MarkdownFormatter(ABC):
    """
    Base class for converting JSON data to formatted Markdown.
    
    Provides common functionality for header generation, content truncation,
    and markdown formatting utilities.
    """
    
    def __init__(self):
        self.config = MarkdownHeaderConfig()
    
    @abstractmethod
    def format(self, data: Dict[str, Any], preview: bool = False, max_chars: int = 500) -> str:
        """Convert JSON data to formatted markdown."""
        pass
    
    def _truncate_content(self, content: str, max_chars: int) -> str:
        """
        Truncate content to max_chars while preserving word boundaries and markdown structure.
        """
        if len(content) <= max_chars:
            return content
            
        # Find the last space before max_chars to preserve word boundaries
        truncate_point = max_chars
        while truncate_point > 0 and content[truncate_point] != ' ':
            truncate_point -= 1
            
        if truncate_point == 0:  # No spaces found, hard truncate
            truncate_point = max_chars
            
        truncated = content[:truncate_point].rstrip()
        
        # Ensure we don't cut off in the middle of markdown syntax
        truncated = self._clean_markdown_truncation(truncated)
        
        return f"{truncated}..."
    
    def _clean_markdown_truncation(self, content: str) -> str:
        """Clean up markdown syntax that might be broken by truncation."""
        # Remove incomplete markdown links
        content = re.sub(r'\[([^\]]*$)', r'\1', content)
        
        # Remove incomplete bold/italic
        content = re.sub(r'\*+([^*]*$)', r'\1', content)
        
        # Remove incomplete headers (partial ### at end)
        content = re.sub(r'#+\s*$', '', content)
        
        return content.rstrip()
    
    def _format_list(self, items: List[str], ordered: bool = False, limit: int = None) -> str:
        """Format a list of items as markdown."""
        if not items:
            return ""
            
        if limit:
            items = items[:limit]
            
        formatted_items = []
        for i, item in enumerate(items, 1):
            prefix = f"{i}. " if ordered else "- "
            formatted_items.append(f"{prefix}{item}")
            
        return "\n".join(formatted_items)
    
    def _format_table(self, data: Dict[str, Any], headers: List[str] = None) -> str:
        """Format dictionary data as a markdown table."""
        if not data:
            return ""
            
        if headers is None:
            headers = ["Attribute", "Value"]
            
        # Create table header
        table_lines = [
            f"| {headers[0]} | {headers[1]} |",
            f"|{'-' * (len(headers[0]) + 2)}|{'-' * (len(headers[1]) + 2)}|"
        ]
        
        # Add data rows
        for key, value in data.items():
            # Handle arrays and complex values
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                value = str(value)
                
            # Clean key for display
            display_key = key.replace('_', ' ').title()
            table_lines.append(f"| {display_key} | {value} |")
            
        return "\n".join(table_lines)
    
    def _get_priority_content(self, data: Dict[str, Any], step_type: str, max_items: int = 3) -> Dict[str, Any]:
        """
        Extract priority content for preview mode based on step type.
        """
        priority_fields = self.config.PREVIEW_PRIORITY.get(step_type, [])
        priority_data = {}
        
        for field in priority_fields:
            if '.' in field:  # Nested field like 'subjects.primary'
                keys = field.split('.')
                value = data
                for key in keys:
                    value = value.get(key) if isinstance(value, dict) else None
                    if value is None:
                        break
                if value is not None:
                    priority_data[field] = value
            else:
                if field in data:
                    value = data[field]
                    # Limit arrays to max_items for preview
                    if isinstance(value, list):
                        value = value[:max_items]
                    priority_data[field] = value
                    
        return priority_data
    
    def _add_metadata_section(self, data: Dict[str, Any]) -> str:
        """Generate metadata section for export mode."""
        metadata = data.get('metadata', {})
        generated_at = data.get('_generated_at')
        step = data.get('_step')
        
        lines = [
            self.config.get_header(self.config.SUB_SECTION, "Generation Details"),
            ""
        ]
        
        if step:
            lines.append(f"**Step**: {step.title()}")
        if generated_at:
            lines.append(f"**Generated**: {generated_at}")
        if metadata.get('confidence'):
            lines.append(f"**Confidence**: {metadata['confidence']}")
        if metadata.get('processing_time_ms'):
            lines.append(f"**Processing Time**: {metadata['processing_time_ms']}ms")
            
        return "\n".join(lines)
    
    def _add_sync_header(self, step_type: str) -> str:
        """Generate sync notice header for structured markdown."""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        
        return f"""<!-- 
🔄 SYNC NOTICE: This file syncs with JSON data
⚠️  DO NOT remove the {{#field_name}} markers - they enable syncing back to JSON
✏️  Feel free to edit content, change headers, add sections - just keep the markers!
📝 Generated: {now} from json_output/{step_type}.json
-->

"""
    
    def _get_header_with_marker(self, level: int, title: str, field_name: str = None) -> str:
        """Get header with optional field marker for sync."""
        if field_name:
            return f"{'#' * level} {title} {{#{field_name}}}"
        else:
            return self.config.get_header(level, title)
    
    @abstractmethod
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """
        Format data as structured markdown with field markers for bidirectional sync.
        This enables editing the markdown and syncing back to JSON.
        """
        pass


# Individual formatter classes will be implemented here
class OverviewFormatter(MarkdownFormatter):
    """Formatter for overview.json - Company analysis data."""
    
    def format(self, data: Dict[str, Any], preview: bool = False, max_chars: int = 500) -> str:
        """
        Format company overview JSON to markdown.
        
        Preview mode shows: Company name + description + top 3 business insights
        Export mode shows: Full analysis with all sections
        """
        lines = []
        
        # Get company info
        company_name = data.get('company_name', 'Company')
        company_url = data.get('company_url', '')
        description = data.get('description', '')
        
        if preview:
            # Preview mode: prioritized content only
            priority_data = self._get_priority_content(data, 'overview', max_items=3)
            
            # Company header
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, company_name))
            lines.append("")
            
            # Description
            if description:
                lines.append(f"**{description}**")
                lines.append("")
            
            # Top business insights
            insights = priority_data.get('business_profile_insights', [])
            if insights:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Key Insights"))
                lines.append(self._format_list(insights[:3]))
                lines.append("")
            
            # Capabilities if space allows
            capabilities = priority_data.get('capabilities', [])
            if capabilities:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Core Capabilities"))
                lines.append(self._format_list(capabilities[:2]))
                
        else:
            # Export mode: complete formatting
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, "Company Overview"))
            lines.append("")
            
            # Company details
            lines.append(f"**Company**: {company_name}")
            if company_url:
                lines.append(f"**Website**: {company_url}")
            lines.append("")
            
            if description:
                lines.append(f"**Description**: {description}")
                lines.append("")
            
            # Business Profile Insights
            business_insights = data.get('business_profile_insights', [])
            if business_insights:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Business Profile"))
                lines.append(self._format_list(business_insights))
                lines.append("")
            
            # Capabilities
            capabilities = data.get('capabilities', [])
            if capabilities:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Core Capabilities"))
                lines.append(self._format_list(capabilities))
                lines.append("")
            
            # Use Case Analysis
            use_cases = data.get('use_case_analysis_insights', [])
            if use_cases:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Use Case Analysis"))
                lines.append(self._format_list(use_cases))
                lines.append("")
            
            # Positioning Insights
            positioning = data.get('positioning_insights', [])
            if positioning:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Market Positioning"))
                lines.append(self._format_list(positioning))
                lines.append("")
            
            # Common Objections
            objections = data.get('objections', [])
            if objections:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Common Objections"))
                lines.append(self._format_list(objections))
                lines.append("")
            
            # Target Customer Insights
            target_insights = data.get('target_customer_insights', [])
            if target_insights:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Target Customers"))
                lines.append(self._format_list(target_insights))
                lines.append("")
            
            # Metadata section
            metadata_section = self._add_metadata_section(data)
            if metadata_section:
                lines.append(metadata_section)
        
        content = "\n".join(lines).strip()
        
        # Apply character limit for preview mode
        if preview and len(content) > max_chars:
            content = self._truncate_content(content, max_chars)
            
        return content
    
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """Format overview data with field markers for bidirectional sync."""
        lines = []
        
        # Add sync header
        lines.append(self._add_sync_header(step_type))
        
        # Get company info
        company_name = data.get('company_name', 'Company')
        company_url = data.get('company_url', '')
        description = data.get('description', '')
        
        # Document title
        lines.append(self.config.get_header(self.config.DOCUMENT_TITLE, f"{company_name} - Company Analysis"))
        lines.append("")
        
        # Company Description (with marker)
        if description:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Company Description", "description"))
            lines.append(description)
            lines.append("")
        
        # Company URL (with marker)
        if company_url:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Website", "company_url"))
            lines.append(company_url)
            lines.append("")
        
        # Business Profile Insights (with marker)
        business_insights = data.get('business_profile_insights', [])
        if business_insights:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Business Insights", "business_profile_insights"))
            lines.append(self._format_list(business_insights))
            lines.append("")
        
        # Capabilities (with marker)
        capabilities = data.get('capabilities', [])
        if capabilities:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Core Capabilities", "capabilities"))
            lines.append(self._format_list(capabilities))
            lines.append("")
        
        # Use Case Analysis (with marker)
        use_cases = data.get('use_case_analysis_insights', [])
        if use_cases:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Use Case Analysis", "use_case_analysis_insights"))
            lines.append(self._format_list(use_cases))
            lines.append("")
        
        # Positioning Insights (with marker)
        positioning = data.get('positioning_insights', [])
        if positioning:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Market Positioning", "positioning_insights"))
            lines.append(self._format_list(positioning))
            lines.append("")
        
        # Common Objections (with marker)
        objections = data.get('objections', [])
        if objections:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Common Objections", "objections"))
            lines.append(self._format_list(objections))
            lines.append("")
        
        # Target Customer Insights (with marker)
        target_insights = data.get('target_customer_insights', [])
        if target_insights:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Target Customer Insights", "target_customer_insights"))
            lines.append(self._format_list(target_insights))
            lines.append("")
        
        return "\n".join(lines).strip()


class AccountFormatter(MarkdownFormatter):
    """Formatter for account.json - Target account profile data."""
    
    def format(self, data: Dict[str, Any], preview: bool = False, max_chars: int = 500) -> str:
        """
        Format target account JSON to markdown.
        
        Preview mode shows: Account name + description + top 3 buying signals
        Export mode shows: Full profile with firmographics table and all signals
        """
        lines = []
        
        # Get account info
        account_name = data.get('target_account_name', 'Target Account')
        account_description = data.get('target_account_description', '')
        
        if preview:
            # Preview mode: prioritized content only
            priority_data = self._get_priority_content(data, 'account', max_items=3)
            
            # Account header
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, account_name))
            lines.append("")
            
            # Description
            if account_description:
                lines.append(f"**{account_description}**")
                lines.append("")
            
            # Top buying signals
            buying_signals = priority_data.get('buying_signals', [])
            if buying_signals:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Key Buying Signals"))
                for signal in buying_signals[:3]:
                    title = signal.get('title', 'Signal')
                    priority = signal.get('priority', 'Medium')
                    description = signal.get('description', '')
                    lines.append(f"- **{title}** ({priority})")
                    if description:
                        lines.append(f"  {description}")
                
        else:
            # Export mode: complete formatting
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, "Target Account Profile"))
            lines.append("")
            
            # Account name and description
            lines.append(self.config.get_dynamic_header('account_name', data, self.config.SUB_SECTION))
            lines.append("")
            
            if account_description:
                lines.append(account_description)
                lines.append("")
            
            # Firmographics table
            firmographics = data.get('firmographics', {})
            if firmographics:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Firmographics"))
                lines.append(self._format_table(firmographics))
                lines.append("")
            
            # Buying Signals
            buying_signals = data.get('buying_signals', [])
            if buying_signals:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Buying Signals"))
                lines.append("")
                
                for i, signal in enumerate(buying_signals, 1):
                    title = signal.get('title', f'Signal {i}')
                    priority = signal.get('priority', 'Medium')
                    signal_type = signal.get('type', 'Unknown')
                    description = signal.get('description', '')
                    detection = signal.get('detection_method', '')
                    
                    # Signal header with priority
                    lines.append(self.config.get_header(
                        self.config.DETAIL_SECTION, 
                        f"{title} ({priority} Priority)"
                    ))
                    
                    if description:
                        lines.append(description)
                        lines.append("")
                    
                    lines.append(f"**Type**: {signal_type}")
                    if detection:
                        lines.append(f"**Detection**: {detection}")
                    lines.append("")
            
            # Targeting Rationale
            rationale = data.get('target_account_rationale', [])
            if rationale:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Targeting Rationale"))
                lines.append(self._format_list(rationale))
                lines.append("")
            
            # Buying Signals Rationale
            signals_rationale = data.get('buying_signals_rationale', [])
            if signals_rationale:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Signal Analysis"))
                lines.append(self._format_list(signals_rationale))
                lines.append("")
            
            # Stale data warning
            if data.get('_stale'):
                stale_reason = data.get('_stale_reason', 'Unknown reason')
                lines.append("> ⚠️ **Note**: This data may be outdated. " + stale_reason)
                lines.append("")
            
            # Metadata section
            metadata_section = self._add_metadata_section(data)
            if metadata_section:
                lines.append(metadata_section)
        
        content = "\n".join(lines).strip()
        
        # Apply character limit for preview mode
        if preview and len(content) > max_chars:
            content = self._truncate_content(content, max_chars)
            
        return content
    
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """Format account data with field markers for bidirectional sync."""
        lines = []
        
        # Add sync header
        lines.append(self._add_sync_header(step_type))
        
        # Account name and description
        account_name = data.get('target_account_name', 'Target Account')
        account_description = data.get('target_account_description', '')
        
        # Document title
        lines.append(self.config.get_header(self.config.DOCUMENT_TITLE, f"{account_name} - Target Account Profile"))
        lines.append("")
        
        # Account Name (with marker)
        lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Account Name", "target_account_name"))
        lines.append(account_name)
        lines.append("")
        
        # Account Description (with marker)
        if account_description:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Account Description", "target_account_description"))
            lines.append(account_description)
            lines.append("")
        
        # Firmographics (with marker)
        firmographics = data.get('firmographics', {})
        if firmographics:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Firmographics", "firmographics"))
            lines.append(self._format_table(firmographics))
            lines.append("")
        
        # Buying Signals (with marker)
        buying_signals = data.get('buying_signals', [])
        if buying_signals:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Buying Signals", "buying_signals"))
            lines.append("")
            
            for i, signal in enumerate(buying_signals, 1):
                title = signal.get('title', f'Signal {i}')
                priority = signal.get('priority', 'Medium')
                signal_type = signal.get('type', 'Unknown')
                description = signal.get('description', '')
                detection = signal.get('detection_method', '')
                
                # Signal header with priority
                lines.append(self.config.get_header(
                    self.config.DETAIL_SECTION, 
                    f"{title} ({priority} Priority)"
                ))
                
                if description:
                    lines.append(description)
                    lines.append("")
                
                lines.append(f"**Type**: {signal_type}")
                if detection:
                    lines.append(f"**Detection**: {detection}")
                lines.append("")
        
        # Targeting Rationale (with marker)
        rationale = data.get('target_account_rationale', [])
        if rationale:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Targeting Rationale", "target_account_rationale"))
            lines.append(self._format_list(rationale))
            lines.append("")
        
        # Buying Signals Rationale (with marker)
        signals_rationale = data.get('buying_signals_rationale', [])
        if signals_rationale:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Buying Signals Rationale", "buying_signals_rationale"))
            lines.append(self._format_list(signals_rationale))
            lines.append("")
        
        # Messaging (with marker)
        messaging = data.get('messaging', {})
        if messaging:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Messaging Guidelines", "messaging"))
            lines.append("")
            
            # Value Propositions
            value_props = messaging.get('value_propositions', [])
            if value_props:
                lines.append(self.config.get_header(self.config.DETAIL_SECTION, "Value Propositions"))
                lines.append(self._format_list(value_props))
                lines.append("")
            
            # Proof Points
            proof_points = messaging.get('proof_points', [])
            if proof_points:
                lines.append(self.config.get_header(self.config.DETAIL_SECTION, "Proof Points"))
                lines.append(self._format_list(proof_points))
                lines.append("")
            
            # Positioning Statements
            positioning = messaging.get('positioning_statements', [])
            if positioning:
                lines.append(self.config.get_header(self.config.DETAIL_SECTION, "Positioning Statements"))
                lines.append(self._format_list(positioning))
                lines.append("")
        
        return "\n".join(lines).strip()


class PersonaFormatter(MarkdownFormatter):
    """Formatter for persona.json - Buyer persona data."""
    
    def format(self, data: Dict[str, Any], preview: bool = False, max_chars: int = 500) -> str:
        """
        Format buyer persona JSON to markdown.
        
        Preview mode shows: Persona name + description + primary use case
        Export mode shows: Full persona with demographics, use cases, goals, journey
        """
        lines = []
        
        # Get persona info
        persona_name = data.get('target_persona_name', 'Target Persona')
        persona_description = data.get('target_persona_description', '')
        
        if preview:
            # Preview mode: prioritized content only
            priority_data = self._get_priority_content(data, 'persona', max_items=1)
            
            # Persona header
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, persona_name))
            lines.append("")
            
            # Description
            if persona_description:
                lines.append(f"**{persona_description}**")
                lines.append("")
            
            # Primary use case
            use_cases = priority_data.get('use_cases', [])
            if use_cases and len(use_cases) > 0:
                use_case = use_cases[0]
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Primary Use Case"))
                lines.append(f"**{use_case.get('use_case', 'Use Case')}**")
                lines.append("")
                
                pain_points = use_case.get('pain_points', '')
                if pain_points:
                    lines.append(f"*Pain Points:* {pain_points}")
                    lines.append("")
                
                desired_outcome = use_case.get('desired_outcome', '')
                if desired_outcome:
                    lines.append(f"*Desired Outcome:* {desired_outcome}")
                
        else:
            # Export mode: complete formatting
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, "Buyer Persona"))
            lines.append("")
            
            # Persona name and description
            lines.append(self.config.get_dynamic_header('persona_name', data, self.config.SUB_SECTION))
            lines.append("")
            
            if persona_description:
                lines.append(persona_description)
                lines.append("")
            
            # Demographics table
            demographics = data.get('demographics', {})
            if demographics:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Demographics"))
                lines.append(self._format_table(demographics))
                lines.append("")
            
            # Use Cases
            use_cases = data.get('use_cases', [])
            if use_cases:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Use Cases"))
                lines.append("")
                
                for i, use_case in enumerate(use_cases, 1):
                    use_case_name = use_case.get('use_case', f'Use Case {i}')
                    pain_points = use_case.get('pain_points', '')
                    capability = use_case.get('capability', '')
                    desired_outcome = use_case.get('desired_outcome', '')
                    
                    # Use case header
                    lines.append(self.config.get_header(
                        self.config.DETAIL_SECTION, 
                        use_case_name
                    ))
                    
                    if pain_points:
                        lines.append(f"**Pain Points**: {pain_points}")
                        lines.append("")
                    
                    if capability:
                        lines.append(f"**Solution**: {capability}")
                        lines.append("")
                    
                    if desired_outcome:
                        lines.append(f"**Desired Outcome**: {desired_outcome}")
                        lines.append("")
            
            # Buying Signals
            buying_signals = data.get('buying_signals', [])
            if buying_signals:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Buying Signals"))
                lines.append("")
                
                for signal in buying_signals:
                    title = signal.get('title', 'Signal')
                    priority = signal.get('priority', 'Medium')
                    description = signal.get('description', '')
                    detection = signal.get('detection_method', '')
                    
                    lines.append(f"- **{title}** ({priority})")
                    if description:
                        lines.append(f"  {description}")
                    if detection:
                        lines.append(f"  *Detection: {detection}*")
                    lines.append("")
            
            # Goals & Motivations
            goals = data.get('goals', [])
            if goals:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Goals & Motivations"))
                lines.append(self._format_list(goals))
                lines.append("")
            
            # Common Objections
            objections = data.get('objections', [])
            if objections:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Common Objections"))
                lines.append(self._format_list(objections))
                lines.append("")
            
            # Purchase Journey
            journey = data.get('purchase_journey', [])
            if journey:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Purchase Journey"))
                lines.append(self._format_list(journey, ordered=True))
                lines.append("")
            
            # Targeting Rationale
            rationale = data.get('target_persona_rationale', [])
            if rationale:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Targeting Rationale"))
                lines.append(self._format_list(rationale))
                lines.append("")
            
            # Stale data warning
            if data.get('_stale'):
                stale_reason = data.get('_stale_reason', 'Unknown reason')
                lines.append("> ⚠️ **Note**: This data may be outdated. " + stale_reason)
                lines.append("")
            
            # Metadata section
            metadata_section = self._add_metadata_section(data)
            if metadata_section:
                lines.append(metadata_section)
        
        content = "\n".join(lines).strip()
        
        # Apply character limit for preview mode
        if preview and len(content) > max_chars:
            content = self._truncate_content(content, max_chars)
            
        return content
    
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """Format persona data with field markers for bidirectional sync."""
        lines = []
        
        # Add sync header
        lines.append(self._add_sync_header(step_type))
        
        # Persona name and description
        persona_name = data.get('target_persona_name', 'Target Persona')
        persona_description = data.get('target_persona_description', '')
        
        # Document title
        lines.append(self.config.get_header(self.config.DOCUMENT_TITLE, f"{persona_name} - Buyer Persona"))
        lines.append("")
        
        # Persona Description (with marker)
        if persona_description:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Persona Description", "target_persona_description"))
            lines.append(persona_description)
            lines.append("")
        
        # Placeholder for other fields - TODO: implement full persona formatting
        lines.append("<!-- TODO: Implement full PersonaFormatter.format_with_markers -->")
        
        return "\n".join(lines).strip()


class EmailFormatter(MarkdownFormatter):
    """Formatter for email.json - Email campaign data with coherent email rendering."""
    
    def format(self, data: Dict[str, Any], preview: bool = False, max_chars: int = 500) -> str:
        """
        Format email campaign JSON to markdown with coherent email structure.
        
        Preview mode shows: Formatted email as it would appear
        Export mode shows: Full email + alternatives + breakdown analysis
        """
        lines = []
        
        # Get email info
        subjects = data.get('subjects', {})
        primary_subject = subjects.get('primary', 'Email Subject')
        alternative_subjects = subjects.get('alternatives', [])
        full_email_body = data.get('full_email_body', '')
        email_body_breakdown = data.get('email_body_breakdown', [])
        writing_process = data.get('writing_process', {})
        
        if preview:
            # Preview mode: Show the email as it would appear using full_email_body
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, f"Email Preview"))
            lines.append("")
            
            # Use full_email_body directly for preview
            if full_email_body:
                lines.append(f"**Subject:** {primary_subject}")
                lines.append("")
                lines.append(full_email_body)
            else:
                # Fallback to breakdown if full_email_body is not available
                coherent_email = self._render_coherent_email(primary_subject, email_body_breakdown)
                lines.append(coherent_email)
                
        else:
            # Export mode: Complete formatting with analysis
            lines.append(self.config.get_header(self.config.MAJOR_SECTION, "Email Campaign"))
            lines.append("")
            
            # Coherent Email Rendering
            lines.append(self.config.get_header(self.config.SUB_SECTION, "Final Email"))
            lines.append("")
            
            if full_email_body:
                lines.append("```email")
                lines.append(f"Subject: {primary_subject}")
                lines.append("")
                lines.append(full_email_body)
                lines.append("```")
            else:
                # Fallback to breakdown if full_email_body is not available
                coherent_email = self._render_coherent_email(primary_subject, email_body_breakdown)
                lines.append("```email")
                lines.append(coherent_email)
                lines.append("```")
            lines.append("")
            
            # Alternative Subject Lines
            if alternative_subjects:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Alternative Subject Lines"))
                lines.append("")
                for alt in alternative_subjects:
                    lines.append(f"- {alt.strip()}")
                lines.append("")
            
            # Email Structure Breakdown
            if email_body_breakdown:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Email Structure Analysis"))
                lines.append("")
                
                # Show each segment with its purpose
                for segment in email_body_breakdown:
                    segment_type = segment.get('type', 'text')
                    text = segment.get('text', '')
                    
                    # Simple label based on segment type
                    label = segment_type.replace('-', ' ').title()
                    
                    lines.append(f"**{label}**")
                    lines.append(f"> {text}")
                    lines.append("")
            
            # Writing Process Analysis
            if writing_process:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Writing Process"))
                lines.append("")
                
                trigger = writing_process.get('trigger', '')
                problem = writing_process.get('problem', '')
                help_offered = writing_process.get('help', '')
                cta = writing_process.get('cta', '')
                
                if trigger:
                    lines.append(f"**Trigger**: {trigger}")
                if problem:
                    lines.append(f"**Problem**: {problem}")
                if help_offered:
                    lines.append(f"**Help Offered**: {help_offered}")
                if cta:
                    lines.append(f"**Call to Action**: {cta}")
                lines.append("")
            
            # Generation Metadata
            metadata = data.get('metadata', {})
            if metadata:
                lines.append(self.config.get_header(self.config.SUB_SECTION, "Generation Details"))
                lines.append("")
                
                confidence = metadata.get('confidence', '')
                personalization = metadata.get('personalization_level', '')
                processing_time = metadata.get('processing_time_ms', '')
                
                details = []
                if confidence:
                    details.append(f"**Confidence**: {confidence.title()}")
                if personalization:
                    details.append(f"**Personalization**: {personalization.title()}")
                if processing_time:
                    details.append(f"**Processing Time**: {processing_time}ms")
                
                if details:
                    lines.extend(details)
                    lines.append("")
            
            # Standard metadata section
            metadata_section = self._add_metadata_section(data)
            if metadata_section:
                lines.append(metadata_section)
        
        content = "\n".join(lines).strip()
        
        # Apply character limit for preview mode
        if preview and len(content) > max_chars:
            content = self._truncate_content(content, max_chars)
            
        return content
    
    def _render_coherent_email(self, subject: str, email_body_breakdown: List[Dict[str, str]]) -> str:
        """
        Render a coherent email from the structured email_body array.
        
        Expected output format:
        **Subject:** subject line
        
        Email body paragraph 1
        Email body paragraph 2
        Email body paragraph 3
        
        Call to action
        """
        lines = []
        
        # Subject line
        lines.append(f"**Subject:** {subject}")
        lines.append("")
        
        # Process email body segments
        if email_body_breakdown:
            # Skip the subject segment (if present) since we already handled it
            body_segments = [seg for seg in email_body_breakdown if seg.get('type') != 'subject']
            
            # Group non-CTA segments into paragraphs, keep CTA separate
            body_paragraphs = []
            cta_text = ""
            
            for segment in body_segments:
                text = segment.get('text', '').strip()
                segment_type = segment.get('type', '')
                
                if segment_type == 'cta':
                    cta_text = text
                else:
                    if text:  # Only add non-empty text
                        body_paragraphs.append(text)
            
            # Add body paragraphs
            if body_paragraphs:
                # Join related sentences into coherent paragraphs
                # For now, put each segment on its own line for readability
                for paragraph in body_paragraphs:
                    lines.append(paragraph)
                
                lines.append("")  # Empty line before CTA
            
            # Add call to action
            if cta_text:
                lines.append(cta_text)
        
        return "\n".join(lines).strip()
    
    def format_with_markers(self, data: Dict[str, Any], step_type: str) -> str:
        """Format email data with field markers for bidirectional sync."""
        lines = []
        
        # Add sync header
        lines.append(self._add_sync_header(step_type))
        
        # Email subject and basic info
        subjects = data.get('subjects', {})
        primary_subject = subjects.get('primary', 'Email Campaign')
        
        # Document title
        lines.append(self.config.get_header(self.config.DOCUMENT_TITLE, f"{primary_subject} - Email Campaign"))
        lines.append("")
        
        # Primary Subject (with marker)
        lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Primary Subject", "subjects.primary"))
        lines.append(primary_subject)
        lines.append("")
        
        # Alternative Subjects (with marker)
        alternatives = subjects.get('alternatives', [])
        if alternatives:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Alternative Subjects", "subjects.alternatives"))
            for alt in alternatives:
                lines.append(f"- {alt}")
            lines.append("")
        
        # Full Email Body (with marker)
        full_body = data.get('full_email_body', '')
        if full_body:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Full Email Body", "full_email_body"))
            lines.append(full_body)
            lines.append("")
        
        # Email Body Breakdown (with marker)
        breakdown = data.get('email_body_breakdown', [])
        if breakdown:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Email Body Breakdown", "email_body_breakdown"))
            lines.append("")
            for section in breakdown:
                section_type = section.get('type', 'unknown').title()
                text = section.get('text', '')
                lines.append(self.config.get_header(self.config.DETAIL_SECTION, f"{section_type}"))
                lines.append(text)
                lines.append("")
        
        # Writing Process (with marker)
        process = data.get('writing_process', {})
        if process:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Writing Process", "writing_process"))
            lines.append("")
            
            trigger = process.get('trigger', '')
            if trigger:
                lines.append(f"**Trigger**: {trigger}")
                lines.append("")
            
            problem = process.get('problem', '')
            if problem:
                lines.append(f"**Problem**: {problem}")
                lines.append("")
            
            help_text = process.get('help', '')
            if help_text:
                lines.append(f"**Help**: {help_text}")
                lines.append("")
            
            cta = process.get('cta', '')
            if cta:
                lines.append(f"**CTA**: {cta}")
                lines.append("")
        
        # Metadata (with marker)
        metadata = data.get('metadata', {})
        if metadata:
            lines.append(self._get_header_with_marker(self.config.SUB_SECTION, "Generation Metadata", "metadata"))
            lines.append("")
            
            generation_id = metadata.get('generation_id', '')
            if generation_id:
                lines.append(f"**Generation ID**: {generation_id}")
            
            confidence = metadata.get('confidence', '')
            if confidence:
                lines.append(f"**Confidence**: {confidence.title()}")
            
            personalization = metadata.get('personalization_level', '')
            if personalization:
                lines.append(f"**Personalization**: {personalization.replace('-', ' ').title()}")
            
            processing_time = metadata.get('processing_time_ms', '')
            if processing_time:
                lines.append(f"**Processing Time**: {processing_time}ms")
            
            if generation_id or confidence or personalization or processing_time:
                lines.append("")
        
        return "\n".join(lines).strip()


def get_formatter(step_type: str) -> MarkdownFormatter:
    """
    Factory function to get the appropriate formatter for a step type.
    
    Args:
        step_type: The type of GTM step ('overview', 'account', 'persona', 'email')
        
    Returns:
        MarkdownFormatter instance for the specified step type
        
    Raises:
        ValueError: If step_type is not recognized
    """
    formatters = {
        'overview': OverviewFormatter,
        'account': AccountFormatter, 
        'persona': PersonaFormatter,
        'email': EmailFormatter
    }
    
    if step_type not in formatters:
        raise ValueError(f"Unknown step type: {step_type}. Supported types: {list(formatters.keys())}")
        
    return formatters[step_type]()


def get_formatter_with_markers(step_type: str) -> MarkdownFormatter:
    """
    Factory function to get formatter specifically for generating structured markdown with field markers.
    This is a convenience function that returns the same formatter but clarifies intent.
    """
    return get_formatter(step_type)


# Testing/Demo functionality
if __name__ == "__main__":
    # Demo the header configuration
    config = MarkdownHeaderConfig()
    
    print("=== Header Configuration Demo ===")
    print(config.get_header(1, "Company Name - GTM Analysis"))
    print(config.get_section_header('overview'))
    print(config.get_header(3, "Key Insights"))
    
    # Demo dynamic headers
    sample_data = {'target_account_name': 'Enterprise SaaS Companies'}
    print(config.get_dynamic_header('account_name', sample_data))
    
    print("\n=== Formatter Factory Demo ===")
    try:
        formatter = get_formatter('overview')
        print(f"✓ Overview formatter: {type(formatter).__name__}")
        
        formatter = get_formatter('invalid')
    except ValueError as e:
        print(f"✓ Error handling: {e}")