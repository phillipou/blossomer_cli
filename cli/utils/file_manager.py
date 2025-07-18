"""
Project file and directory management utilities.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from cli.utils.domain import get_project_name


@dataclass
class ProjectMetadata:
    """Metadata for a GTM project."""
    domain: str
    created_at: datetime
    modified_at: datetime
    steps_completed: List[str]
    total_steps: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'domain': self.domain,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'steps_completed': self.steps_completed,
            'total_steps': self.total_steps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Create from dictionary loaded from JSON."""
        return cls(
            domain=data['domain'],
            created_at=datetime.fromisoformat(data['created_at']),
            modified_at=datetime.fromisoformat(data['modified_at']),
            steps_completed=data['steps_completed'],
            total_steps=data.get('total_steps', 5)
        )


class ProjectManager:
    """Manages GTM project files and directories."""
    
    STEP_FILES = {
        'overview': 'overview.json',
        'account': 'account.json', 
        'persona': 'persona.json',
        'email': 'email.json',
        'plan': 'plan.json'
    }
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with base path for projects."""
        self.base_path = base_path or Path.cwd() / "gtm_projects"
        self.global_state_file = self.base_path / ".blossomer-state.json"
    
    def ensure_base_directory(self) -> None:
        """Ensure the base gtm_projects directory exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_project_path(self, domain: str) -> Path:
        """Get the path for a project directory."""
        project_name = get_project_name(domain)
        return self.base_path / project_name
    
    def project_exists(self, domain: str) -> bool:
        """Check if a project already exists."""
        project_path = self.get_project_path(domain)
        return project_path.exists() and project_path.is_dir()
    
    def create_project(self, domain: str) -> Path:
        """Create a new project directory structure."""
        self.ensure_base_directory()
        
        project_path = self.get_project_path(domain)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create json_output subdirectory for all JSON files
        json_output_path = project_path / "json_output"
        json_output_path.mkdir(exist_ok=True)
        
        # Create export subdirectory
        export_path = project_path / "export"
        export_path.mkdir(exist_ok=True)
        
        # Create initial metadata
        metadata = ProjectMetadata(
            domain=domain,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            steps_completed=[]
        )
        self._save_metadata(project_path, metadata)
        
        return project_path
    
    def save_step_data(self, domain: str, step: str, data: Dict[str, Any]) -> Path:
        """Save data for a specific step."""
        if step not in self.STEP_FILES:
            raise ValueError(f"Unknown step: {step}")
        
        project_path = self.get_project_path(domain)
        if not project_path.exists():
            project_path = self.create_project(domain)
        
        # Save the step data to json_output directory
        json_output_path = project_path / "json_output"
        json_output_path.mkdir(exist_ok=True)
        file_path = json_output_path / self.STEP_FILES[step]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        metadata = self._load_metadata(project_path)
        if step not in metadata.steps_completed:
            metadata.steps_completed.append(step)
        metadata.modified_at = datetime.now()
        self._save_metadata(project_path, metadata)
        
        return file_path
    
    def load_step_data(self, domain: str, step: str) -> Optional[Dict[str, Any]]:
        """Load data for a specific step."""
        if step not in self.STEP_FILES:
            raise ValueError(f"Unknown step: {step}")
        
        project_path = self.get_project_path(domain)
        file_path = project_path / "json_output" / self.STEP_FILES[step]
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_step_file_path(self, domain: str, step: str) -> Path:
        """Get the file path for a specific step."""
        if step not in self.STEP_FILES:
            raise ValueError(f"Unknown step: {step}")
        
        project_path = self.get_project_path(domain)
        return project_path / "json_output" / self.STEP_FILES[step]
    
    def list_projects(self) -> List[Tuple[str, ProjectMetadata]]:
        """List all projects with their metadata."""
        if not self.base_path.exists():
            return []
        
        projects = []
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                metadata = self._load_metadata(item)
                if metadata:
                    projects.append((item.name, metadata))
        
        # Sort by modification time (newest first)
        projects.sort(key=lambda x: x[1].modified_at, reverse=True)
        return projects
    
    def get_project_status(self, domain: str) -> Optional[ProjectMetadata]:
        """Get project status/metadata."""
        project_path = self.get_project_path(domain)
        if not project_path.exists():
            return None
        
        return self._load_metadata(project_path)
    
    def delete_project(self, domain: str) -> bool:
        """Delete a project and all its files."""
        project_path = self.get_project_path(domain)
        if not project_path.exists():
            return False
        
        import shutil
        shutil.rmtree(project_path)
        return True
    
    def get_export_path(self, domain: str, filename: Optional[str] = None) -> Path:
        """Get path for exported files."""
        project_path = self.get_project_path(domain)
        export_path = project_path / "export"
        
        if filename is None:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d")
            project_name = get_project_name(domain)
            filename = f"gtm-report-{project_name}-{timestamp}.md"
        
        return export_path / filename
    
    def _load_metadata(self, project_path: Path) -> Optional[ProjectMetadata]:
        """Load project metadata from .metadata.json file."""
        metadata_file = project_path / ".metadata.json"
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProjectMetadata.from_dict(data)
        except (json.JSONDecodeError, IOError, KeyError):
            return None
    
    def _save_metadata(self, project_path: Path, metadata: ProjectMetadata) -> None:
        """Save project metadata to .metadata.json file."""
        metadata_file = project_path / ".metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2)
    
    def load_global_state(self) -> Dict[str, Any]:
        """Load global CLI state."""
        if not self.global_state_file.exists():
            return self._get_default_global_state()
        
        try:
            with open(self.global_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._get_default_global_state()
    
    def save_global_state(self, state: Dict[str, Any]) -> None:
        """Save global CLI state."""
        self.ensure_base_directory()
        with open(self.global_state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    def _get_default_global_state(self) -> Dict[str, Any]:
        """Get default global state."""
        return {
            "version": "0.1.0",
            "default_editor": "auto",
            "last_used_project": None,
            "user_preferences": {
                "auto_regenerate_deps": True,
                "show_timing": True,
                "color_output": True
            },
            "api_usage": {
                "total_requests": 0,
                "last_reset": datetime.now().isoformat()
            }
        }


# Test function
if __name__ == "__main__":
    pm = ProjectManager()
    
    # Test project creation
    test_domain = "test-example.com"
    
    print(f"Testing ProjectManager with domain: {test_domain}")
    print(f"Base path: {pm.base_path}")
    print(f"Project exists: {pm.project_exists(test_domain)}")
    
    # Create test project
    project_path = pm.create_project(test_domain)
    print(f"Created project at: {project_path}")
    
    # Test saving data
    test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
    file_path = pm.save_step_data(test_domain, "overview", test_data)
    print(f"Saved test data to: {file_path}")
    
    # Test loading data
    loaded_data = pm.load_step_data(test_domain, "overview")
    print(f"Loaded data: {loaded_data}")
    
    # Test project listing
    projects = pm.list_projects()
    print(f"Projects: {projects}")
    
    # Clean up
    pm.delete_project(test_domain)
    print("Cleaned up test project")