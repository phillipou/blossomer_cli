"""
Sync Manager for Bidirectional JSON ↔ Markdown Sync

This module manages the coordination between JSON files (source of truth) and 
editable markdown files (plans/), handling change detection, conflict resolution,
and maintaining sync state.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from cli.utils.markdown_formatter import get_formatter
from cli.utils.markdown_parser import create_parser
from cli.utils.file_manager import ProjectManager


class SyncDirection(Enum):
    """Direction of sync operation."""
    JSON_TO_PLANS = "json_to_plans"
    PLANS_TO_JSON = "plans_to_json"
    NO_CHANGE = "no_change"
    CONFLICT = "conflict"


@dataclass
class SyncState:
    """Current sync state for a project step."""
    last_sync: datetime
    json_modified: datetime
    plans_modified: datetime
    json_hash: str
    plans_hash: str
    sync_direction: SyncDirection
    synced_fields: List[str]
    orphaned_fields: List[str]


@dataclass
class ConflictResolution:
    """Result of conflict resolution."""
    action: str  # 'use_json', 'use_plans', 'merge', 'manual'
    message: str
    needs_user_input: bool = False


class SyncManager:
    """Manages bidirectional sync between JSON and plans directories."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize sync manager."""
        self.project_manager = ProjectManager(base_path)
        self.parser = create_parser()
        
        # Supported step types
        self.step_types = ['overview', 'account', 'persona', 'email']
    
    def get_project_path(self, domain: str) -> Path:
        """Get the project directory path."""
        return self.project_manager.get_project_path(domain)
    
    def get_plans_path(self, domain: str) -> Path:
        """Get the plans directory path."""
        return self.get_project_path(domain) / "plans"
    
    def get_sync_state_file(self, domain: str) -> Path:
        """Get the sync state file path."""
        return self.get_plans_path(domain) / ".sync_state.json"
    
    def ensure_plans_directory(self, domain: str) -> None:
        """Ensure the plans directory exists."""
        plans_path = self.get_plans_path(domain)
        plans_path.mkdir(parents=True, exist_ok=True)
    
    def sync_project(self, domain: str, step: Optional[str] = None, auto_resolve: bool = True) -> Dict[str, Any]:
        """
        Sync all or specific step files for a project.
        
        Args:
            domain: Project domain
            step: Specific step to sync (None for all steps)
            auto_resolve: Whether to automatically resolve simple conflicts
            
        Returns:
            Summary of sync operations performed
        """
        summary = {
            'synced_steps': [],
            'conflicts': [],
            'errors': [],
            'orphaned_fields': {}
        }
        
        steps_to_sync = [step] if step else self.step_types
        
        for step_name in steps_to_sync:
            try:
                result = self.sync_step(domain, step_name, auto_resolve)
                summary['synced_steps'].append({
                    'step': step_name,
                    'direction': result['direction'],
                    'fields_synced': result.get('fields_synced', 0),
                    'warnings': result.get('warnings', [])
                })
                
                if result.get('orphaned_fields'):
                    summary['orphaned_fields'][step_name] = result['orphaned_fields']
                    
                if result.get('conflict'):
                    summary['conflicts'].append({
                        'step': step_name,
                        'conflict': result['conflict']
                    })
                    
            except Exception as e:
                summary['errors'].append({
                    'step': step_name,
                    'error': str(e)
                })
        
        return summary
    
    def sync_step(self, domain: str, step: str, auto_resolve: bool = True) -> Dict[str, Any]:
        """
        Sync a specific step between JSON and plans.
        
        Args:
            domain: Project domain
            step: Step name (overview, account, persona, email)
            auto_resolve: Whether to automatically resolve simple conflicts
            
        Returns:
            Result of sync operation
        """
        # Detect current state
        sync_state = self.detect_changes(domain, step)
        
        if sync_state == SyncDirection.NO_CHANGE:
            return {'direction': 'no_change', 'message': 'No changes detected'}
        
        elif sync_state == SyncDirection.JSON_TO_PLANS:
            return self.sync_json_to_plans(domain, step)
        
        elif sync_state == SyncDirection.PLANS_TO_JSON:
            return self.sync_plans_to_json(domain, step)
        
        elif sync_state == SyncDirection.CONFLICT:
            if auto_resolve:
                resolution = self.resolve_conflicts(domain, step)
                if resolution.action == 'use_plans':
                    return self.sync_plans_to_json(domain, step)
                elif resolution.action == 'use_json':
                    return self.sync_json_to_plans(domain, step)
                else:
                    return {
                        'direction': 'conflict',
                        'conflict': resolution,
                        'message': 'Manual conflict resolution required'
                    }
            else:
                return {
                    'direction': 'conflict',
                    'message': 'Conflict detected - manual resolution required'
                }
    
    def detect_changes(self, domain: str, step: str) -> SyncDirection:
        """
        Detect which direction sync should go based on file modification times.
        
        Args:
            domain: Project domain
            step: Step name
            
        Returns:
            Direction that sync should proceed
        """
        project_path = self.get_project_path(domain)
        json_file = project_path / "json_output" / f"{step}.json"
        plans_file = self.get_plans_path(domain) / f"{step}.md"
        
        # Check if files exist
        json_exists = json_file.exists()
        plans_exists = plans_file.exists()
        
        if not json_exists and not plans_exists:
            return SyncDirection.NO_CHANGE
        
        if json_exists and not plans_exists:
            return SyncDirection.JSON_TO_PLANS
        
        if not json_exists and plans_exists:
            return SyncDirection.PLANS_TO_JSON
        
        # Both files exist - compare modification times
        json_mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
        plans_mtime = datetime.fromtimestamp(plans_file.stat().st_mtime)
        
        # Load sync state to compare against last known sync
        sync_state = self.load_sync_state(domain, step)
        
        if sync_state:
            # Check if both files changed since last sync
            json_changed = json_mtime > sync_state.last_sync
            plans_changed = plans_mtime > sync_state.last_sync
            
            if json_changed and plans_changed:
                return SyncDirection.CONFLICT
            elif json_changed:
                return SyncDirection.JSON_TO_PLANS
            elif plans_changed:
                return SyncDirection.PLANS_TO_JSON
            else:
                return SyncDirection.NO_CHANGE
        else:
            # No sync state - use simple time comparison
            time_diff = (plans_mtime - json_mtime).total_seconds()
            
            if abs(time_diff) < 5:  # Within 5 seconds - consider no change
                return SyncDirection.NO_CHANGE
            elif plans_mtime > json_mtime:
                return SyncDirection.PLANS_TO_JSON
            else:
                return SyncDirection.JSON_TO_PLANS
    
    def sync_json_to_plans(self, domain: str, step: str) -> Dict[str, Any]:
        """Update plans markdown file from JSON data."""
        try:
            # Load JSON data
            json_data = self.project_manager.load_step_data(domain, step)
            if not json_data:
                return {'direction': 'json_to_plans', 'error': f'No JSON data found for {step}'}
            
            # Generate structured markdown with field markers
            formatter = get_formatter(step)
            markdown_content = formatter.format_with_markers(json_data, step)
            
            # Ensure plans directory exists
            self.ensure_plans_directory(domain)
            
            # Write markdown file
            plans_file = self.get_plans_path(domain) / f"{step}.md"
            plans_file.write_text(markdown_content, encoding='utf-8')
            
            # Update sync state
            self.save_sync_state(domain, step, SyncDirection.JSON_TO_PLANS, 
                               list(json_data.keys()), [])
            
            return {
                'direction': 'json_to_plans',
                'message': f'Generated {step}.md from JSON data',
                'fields_synced': len(json_data),
                'output_file': str(plans_file)
            }
            
        except Exception as e:
            return {
                'direction': 'json_to_plans',
                'error': f'Failed to sync JSON to plans: {e}'
            }
    
    def sync_plans_to_json(self, domain: str, step: str) -> Dict[str, Any]:
        """Update JSON data from edited plans markdown."""
        try:
            # Load plans markdown
            plans_file = self.get_plans_path(domain) / f"{step}.md"
            if not plans_file.exists():
                return {'direction': 'plans_to_json', 'error': f'No plans file found: {step}.md'}
            
            markdown_content = plans_file.read_text(encoding='utf-8')
            
            # Parse markdown to JSON
            parse_result = self.parser.parse_with_orphan_handling(markdown_content, step)
            
            if not parse_result.is_success():
                return {
                    'direction': 'plans_to_json',
                    'error': 'No fields could be parsed from markdown',
                    'warnings': parse_result.warnings
                }
            
            # Save JSON data
            self.project_manager.save_step_data(domain, step, parse_result.synced_fields)
            
            # Update sync state
            self.save_sync_state(domain, step, SyncDirection.PLANS_TO_JSON,
                               list(parse_result.synced_fields.keys()), 
                               parse_result.orphaned_fields)
            
            return {
                'direction': 'plans_to_json',
                'message': f'Updated JSON from {step}.md',
                'fields_synced': parse_result.success_count,
                'warnings': parse_result.warnings,
                'orphaned_fields': parse_result.orphaned_fields,
                'infos': parse_result.infos
            }
            
        except Exception as e:
            return {
                'direction': 'plans_to_json',
                'error': f'Failed to sync plans to JSON: {e}'
            }
    
    def resolve_conflicts(self, domain: str, step: str) -> ConflictResolution:
        """
        Automatically resolve simple conflicts.
        
        For now, implements a simple "plans wins" strategy since user editing
        is the primary use case. More sophisticated conflict resolution can
        be added later.
        """
        # Simple resolution: plans file wins (user editing takes precedence)
        return ConflictResolution(
            action='use_plans',
            message=f'Auto-resolved conflict for {step}: Using plans file (user edits take precedence)',
            needs_user_input=False
        )
    
    def load_sync_state(self, domain: str, step: str) -> Optional[SyncState]:
        """Load sync state for a specific step."""
        sync_file = self.get_sync_state_file(domain)
        
        if not sync_file.exists():
            return None
        
        try:
            with open(sync_file, 'r') as f:
                all_state = json.load(f)
            
            step_state = all_state.get(step)
            if not step_state:
                return None
            
            return SyncState(
                last_sync=datetime.fromisoformat(step_state['last_sync']),
                json_modified=datetime.fromisoformat(step_state['json_modified']),
                plans_modified=datetime.fromisoformat(step_state['plans_modified']),
                json_hash=step_state['json_hash'],
                plans_hash=step_state['plans_hash'],
                sync_direction=SyncDirection(step_state['sync_direction']),
                synced_fields=step_state.get('synced_fields', []),
                orphaned_fields=step_state.get('orphaned_fields', [])
            )
            
        except Exception:
            return None
    
    def save_sync_state(self, domain: str, step: str, direction: SyncDirection, 
                       synced_fields: List[str], orphaned_fields: List[str]) -> None:
        """Save sync state for a specific step."""
        self.ensure_plans_directory(domain)
        sync_file = self.get_sync_state_file(domain)
        
        # Load existing state
        all_state = {}
        if sync_file.exists():
            try:
                with open(sync_file, 'r') as f:
                    all_state = json.load(f)
            except Exception:
                pass
        
        # Get file stats
        project_path = self.get_project_path(domain)
        json_file = project_path / "json_output" / f"{step}.json"
        plans_file = self.get_plans_path(domain) / f"{step}.md"
        
        now = datetime.now()
        
        # Create state entry
        all_state[step] = {
            'last_sync': now.isoformat(),
            'json_modified': datetime.fromtimestamp(json_file.stat().st_mtime).isoformat() if json_file.exists() else now.isoformat(),
            'plans_modified': datetime.fromtimestamp(plans_file.stat().st_mtime).isoformat() if plans_file.exists() else now.isoformat(),
            'json_hash': self._calculate_file_hash(json_file) if json_file.exists() else "",
            'plans_hash': self._calculate_file_hash(plans_file) if plans_file.exists() else "",
            'sync_direction': direction.value,
            'synced_fields': synced_fields,
            'orphaned_fields': orphaned_fields
        }
        
        # Save state
        with open(sync_file, 'w') as f:
            json.dump(all_state, f, indent=2)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file contents."""
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()[:16]  # First 16 chars
        except Exception:
            return ""
    
    def get_sync_status(self, domain: str) -> Dict[str, Any]:
        """Get sync status for all steps in a project."""
        status = {}
        
        for step in self.step_types:
            sync_state = self.load_sync_state(domain, step)
            direction = self.detect_changes(domain, step)
            
            project_path = self.get_project_path(domain)
            json_file = project_path / "json_output" / f"{step}.json"
            plans_file = self.get_plans_path(domain) / f"{step}.md"
            
            status[step] = {
                'json_exists': json_file.exists(),
                'plans_exists': plans_file.exists(),
                'sync_needed': direction != SyncDirection.NO_CHANGE,
                'sync_direction': direction.value,
                'last_sync': sync_state.last_sync.isoformat() if sync_state else None,
                'synced_fields': sync_state.synced_fields if sync_state else [],
                'orphaned_fields': sync_state.orphaned_fields if sync_state else []
            }
        
        return status
    
    def create_backup(self, domain: str, step: str) -> Dict[str, str]:
        """Create backup copies of both JSON and plans files."""
        backup_dir = self.get_project_path(domain) / ".backup"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backups = {}
        
        # Backup JSON file
        json_file = self.get_project_path(domain) / "json_output" / f"{step}.json"
        if json_file.exists():
            json_backup = backup_dir / f"{step}_json_{timestamp}.json"
            json_backup.write_text(json_file.read_text())
            backups['json'] = str(json_backup)
        
        # Backup plans file
        plans_file = self.get_plans_path(domain) / f"{step}.md"
        if plans_file.exists():
            plans_backup = backup_dir / f"{step}_plans_{timestamp}.md"
            plans_backup.write_text(plans_file.read_text())
            backups['plans'] = str(plans_backup)
        
        return backups