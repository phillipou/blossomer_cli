"""
Markdown Parser for Bidirectional JSON ↔ Markdown Sync

This module provides utilities to parse structured markdown files (with field markers)
back to JSON format, enabling users to edit human-readable markdown and sync changes
back to the CLI's JSON data store.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SyncResult:
    """Results from a markdown parsing operation."""
    synced_fields: Dict[str, Any]
    orphaned_fields: List[str]
    warnings: List[str]
    infos: List[str]
    success_count: int
    
    def __init__(self):
        self.synced_fields = {}
        self.orphaned_fields = []
        self.warnings = []
        self.infos = []
        self.success_count = 0
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add an info message."""
        self.infos.append(message)
    
    def is_success(self) -> bool:
        """Sync succeeds if ANY fields were processed successfully."""
        return self.success_count > 0


class MarkdownParser:
    """Parse structured markdown with field markers back to JSON format."""
    
    # Expected fields for each step type (for validation)
    EXPECTED_FIELDS = {
        'overview': [
            'description', 'company_url', 'business_profile_insights', 
            'capabilities', 'use_case_analysis_insights', 'positioning_insights',
            'objections', 'target_customer_insights'
        ],
        'account': [
            'target_account_description', 'firmographics', 'buying_signals',
            'targeting_rationale'
        ],
        'persona': [
            'target_persona_description', 'demographics', 'use_cases',
            'buying_signals', 'goals', 'objections', 'purchase_journey'
        ],
        'email': [
            'subjects', 'email_body', 'segments', 'personalization_notes'
        ]
    }
    
    def __init__(self):
        # Regex pattern to find field markers: {#field_name}
        self.field_marker_pattern = r'^(#{1,6})\s+(.+?)\s*\{#(\w+)\}'
        
        # Pattern to extract sync metadata from header comments
        self.sync_meta_pattern = r'<!--\s*\n🔄 SYNC NOTICE:.*?📝 Generated: (.+?) from json_output/(\w+)\.json\s*\n-->'
    
    def parse_with_orphan_handling(self, content: str, step_type: str) -> SyncResult:
        """
        Parse markdown with graceful orphan handling.
        
        Args:
            content: Raw markdown content
            step_type: Type of step (overview, account, persona, email)
            
        Returns:
            SyncResult with parsed fields, warnings, and info about orphaned content
        """
        result = SyncResult()
        expected_fields = self.EXPECTED_FIELDS.get(step_type, [])
        
        # Extract metadata from sync header
        metadata = self.extract_sync_metadata(content)
        if metadata:
            result.add_info(f"Parsed sync metadata: generated {metadata['generated_at']} from {metadata['source_file']}")
        
        # Extract marked sections
        marked_sections = self.extract_marked_sections(content)
        
        # Process found fields
        for field_name, field_content in marked_sections.items():
            if field_name in expected_fields:
                try:
                    parsed_value = self.parse_field_content(field_content, field_name, step_type)
                    result.synced_fields[field_name] = parsed_value
                    result.success_count += 1
                except Exception as e:
                    result.add_warning(f"{field_name}: Parse error - {e}")
            else:
                result.add_info(f"{field_name}: Ignored (not in JSON schema for {step_type})")
        
        # Check for orphaned fields (expected but missing markers)
        for expected_field in expected_fields:
            if expected_field not in marked_sections:
                result.add_warning(f"{expected_field}: ORPHANED - marker missing, field dropped")
                result.orphaned_fields.append(expected_field)
        
        # Check for unmarked content
        unmarked_content = self.find_unmarked_content(content, marked_sections)
        if unmarked_content:
            result.add_info(f"Unmarked content preserved: {len(unmarked_content)} sections")
        
        return result
    
    def extract_sync_metadata(self, content: str) -> Optional[Dict[str, str]]:
        """Extract metadata from sync header comment."""
        match = re.search(self.sync_meta_pattern, content, re.DOTALL)
        if match:
            return {
                'generated_at': match.group(1).strip(),
                'source_file': f"json_output/{match.group(2)}.json"
            }
        return None
    
    def extract_marked_sections(self, content: str) -> Dict[str, str]:
        """
        Find all {#field_name} markers and extract content until next header.
        
        Returns:
            Dictionary mapping field_name to the content between headers
        """
        sections = {}
        lines = content.split('\n')
        current_field = None
        current_content = []
        
        for line in lines:
            # Check if this line has a field marker
            marker_match = re.match(self.field_marker_pattern, line)
            
            if marker_match:
                # Save previous field if we were collecting one
                if current_field and current_content:
                    sections[current_field] = '\n'.join(current_content).strip()
                
                # Start collecting new field
                current_field = marker_match.group(3)  # Extract field name
                current_content = []
                
            elif current_field:
                # Check if this is a new header without marker (end of current field)
                if re.match(r'^#{1,6}\s+', line) and '{#' not in line:
                    # Save current field and stop collecting
                    sections[current_field] = '\n'.join(current_content).strip()
                    current_field = None
                    current_content = []
                else:
                    # Continue collecting content for current field
                    current_content.append(line)
        
        # Save the last field if we were collecting one
        if current_field and current_content:
            sections[current_field] = '\n'.join(current_content).strip()
        
        return sections
    
    def parse_field_content(self, content: str, field_name: str, step_type: str) -> Any:
        """
        Parse the content of a specific field based on its expected type.
        
        Args:
            content: Raw content between field markers
            field_name: Name of the field
            step_type: Type of step for context
            
        Returns:
            Parsed value (string, list, or complex object)
        """
        content = content.strip()
        
        if not content:
            return None
        
        # Simple string fields
        if field_name in ['description', 'company_url', 'target_account_description', 'target_persona_description']:
            return content
        
        # List fields (markdown bullet points)
        if field_name in ['business_profile_insights', 'capabilities', 'use_case_analysis_insights', 
                          'positioning_insights', 'objections', 'target_customer_insights']:
            return self.parse_list_content(content)
        
        # Complex object fields (buying_signals, use_cases, etc.)
        if field_name in ['buying_signals', 'use_cases', 'demographics', 'firmographics']:
            return self.parse_complex_field(content, field_name)
        
        # Email-specific fields
        if field_name in ['subjects', 'email_body', 'segments']:
            return self.parse_email_field(content, field_name)
        
        # Default: return as string
        return content
    
    def parse_list_content(self, content: str) -> List[str]:
        """Parse markdown list content into array of strings."""
        items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Handle both - and * bullet points, and numbered lists
            if re.match(r'^[-*]\s+', line):
                items.append(line[2:].strip())
            elif re.match(r'^\d+\.\s+', line):
                # Remove number and dot
                items.append(re.sub(r'^\d+\.\s+', '', line).strip())
            elif line and not line.startswith('#'):
                # Non-empty line that's not a header - treat as continuation
                if items:
                    items[-1] += ' ' + line
                else:
                    items.append(line)
        
        return [item for item in items if item]  # Filter empty items
    
    def parse_complex_field(self, content: str, field_name: str) -> Any:
        """Parse complex fields like buying_signals, use_cases, etc."""
        # For now, return as structured text - TODO: implement full parsing
        # This would parse markdown like:
        # **Signal 1: Title** (Priority)
        # Description text
        # *Detection: method*
        
        if field_name == 'buying_signals':
            return self.parse_buying_signals(content)
        elif field_name == 'use_cases':
            return self.parse_use_cases(content)
        elif field_name == 'demographics':
            return self.parse_demographics(content)
        elif field_name == 'firmographics':
            return self.parse_firmographics(content)
        else:
            # Fallback: return as string for now
            return content
    
    def parse_buying_signals(self, content: str) -> List[Dict[str, Any]]:
        """Parse buying signals from structured markdown."""
        signals = []
        
        # Split by signal patterns: **Signal N: Title** (Priority)
        signal_pattern = r'\*\*([^*]+)\*\*\s*\(([^)]+)\)'
        sections = re.split(signal_pattern, content)
        
        # Process sections in groups of 3 (text_before, title, priority, description)
        for i in range(1, len(sections), 3):
            if i + 2 < len(sections):
                title = sections[i].strip()
                priority = sections[i + 1].strip().lower()
                description_text = sections[i + 2].strip()
                
                # Extract detection method if present
                detection_match = re.search(r'\*Detection:\s*([^*\n]+)\*', description_text)
                detection_method = detection_match.group(1).strip() if detection_match else ""
                
                # Clean description (remove detection line)
                description = re.sub(r'\*Detection:[^*\n]+\*', '', description_text).strip()
                
                signals.append({
                    'title': title,
                    'priority': priority,
                    'description': description,
                    'detection_method': detection_method
                })
        
        return signals
    
    def parse_use_cases(self, content: str) -> List[Dict[str, Any]]:
        """Parse use cases from structured markdown."""
        # Placeholder implementation
        return [{'use_case': content, 'parsed': False}]
    
    def parse_demographics(self, content: str) -> Dict[str, Any]:
        """Parse demographics table or list."""
        # Placeholder implementation - would parse markdown tables
        return {'raw_content': content, 'parsed': False}
    
    def parse_firmographics(self, content: str) -> Dict[str, Any]:
        """Parse firmographics table or list."""
        # Placeholder implementation - would parse markdown tables
        return {'raw_content': content, 'parsed': False}
    
    def parse_email_field(self, content: str, field_name: str) -> Any:
        """Parse email-specific fields."""
        # Placeholder implementation
        return {'raw_content': content, 'field': field_name, 'parsed': False}
    
    def find_unmarked_content(self, content: str, marked_sections: Dict[str, str]) -> List[str]:
        """Find content sections that don't have field markers."""
        # This would identify sections of content that aren't between field markers
        # For now, return empty list
        return []
    
    def validate_parsed_data(self, data: Dict[str, Any], step_type: str) -> Tuple[bool, List[str]]:
        """
        Validate that parsed data matches expected schema.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        expected_fields = self.EXPECTED_FIELDS.get(step_type, [])
        
        # Check for required fields (basic validation)
        missing_fields = [field for field in expected_fields if field not in data]
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
        
        # Type validation could go here
        # For now, just check that lists are actually lists
        for field_name, value in data.items():
            if field_name.endswith('_insights') or field_name in ['capabilities', 'objections']:
                if not isinstance(value, list):
                    errors.append(f"Field '{field_name}' should be a list, got {type(value)}")
        
        return len(errors) == 0, errors


# Factory function for easy usage
def create_parser() -> MarkdownParser:
    """Create a new markdown parser instance."""
    return MarkdownParser()