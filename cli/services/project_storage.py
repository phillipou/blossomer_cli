"""
Project Storage Service - JSON file storage and retrieval for CLI GTM projects
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProjectMetadata(BaseModel):
    """Metadata for GTM project tracking"""
    domain: str
    created_at: datetime
    updated_at: datetime
    last_step: Optional[str] = None
    completed_steps: List[str] = []
    total_cost: Optional[float] = None
    total_time_seconds: Optional[float] = None


class ProjectStorage:
    """Handles JSON file storage and retrieval for GTM projects"""
    
    def __init__(self, base_dir: str = "gtm_projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Global state file
        self.state_file = self.base_dir / ".gtm-cli-state.json"
    
    def get_project_dir(self, domain: str) -> Path:
        """Get the project directory for a given domain"""
        # Normalize domain for filesystem
        safe_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        safe_domain = safe_domain.replace("/", "_").replace(":", "_")
        return self.base_dir / safe_domain
    
    def create_project(self, domain: str) -> Path:
        """Create a new project directory and metadata"""
        project_dir = self.get_project_dir(domain)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create export subdirectory
        export_dir = project_dir / "export"
        export_dir.mkdir(exist_ok=True)
        
        # Initialize metadata
        metadata = ProjectMetadata(
            domain=domain,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.save_metadata(domain, metadata)
        
        logger.info(f"Created project directory: {project_dir}")
        return project_dir
    
    def project_exists(self, domain: str) -> bool:
        """Check if a project already exists"""
        return self.get_project_dir(domain).exists()
    
    def save_step_data(self, domain: str, step: str, data: Union[BaseModel, Dict[str, Any]]) -> Path:
        """Save data for a specific step"""
        project_dir = self.get_project_dir(domain)
        if not project_dir.exists():
            project_dir = self.create_project(domain)
        
        # Convert Pydantic models to dict
        if isinstance(data, BaseModel):
            data_dict = data.model_dump()
        else:
            data_dict = data
        
        # Add generation timestamp
        data_dict["_generated_at"] = datetime.now().isoformat()
        data_dict["_step"] = step
        
        # Save to appropriate file
        step_file = project_dir / f"{step}.json"
        with open(step_file, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        self._update_project_metadata(domain, step)
        
        logger.info(f"Saved {step} data to {step_file}")
        return step_file
    
    def load_step_data(self, domain: str, step: str) -> Optional[Dict[str, Any]]:
        """Load data for a specific step"""
        project_dir = self.get_project_dir(domain)
        step_file = project_dir / f"{step}.json"
        
        if not step_file.exists():
            return None
        
        try:
            with open(step_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {step} data from {step_file}")
            return data
        except Exception as e:
            logger.error(f"Failed to load {step} data: {e}")
            return None
    
    def get_available_steps(self, domain: str) -> List[str]:
        """Get list of completed steps for a project"""
        project_dir = self.get_project_dir(domain)
        if not project_dir.exists():
            return []
        
        steps = []
        step_files = ["overview.json", "account.json", "persona.json", "email.json", "plan.json"]
        
        for step_file in step_files:
            if (project_dir / step_file).exists():
                step_name = step_file.replace(".json", "")
                steps.append(step_name)
        
        return steps
    
    def save_metadata(self, domain: str, metadata: ProjectMetadata) -> None:
        """Save project metadata"""
        project_dir = self.get_project_dir(domain)
        metadata_file = project_dir / ".metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)
    
    def load_metadata(self, domain: str) -> Optional[ProjectMetadata]:
        """Load project metadata"""
        project_dir = self.get_project_dir(domain)
        metadata_file = project_dir / ".metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProjectMetadata.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all available projects"""
        projects = []
        
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                metadata = self.load_metadata(project_dir.name)
                available_steps = self.get_available_steps(project_dir.name)
                
                project_info = {
                    "domain": project_dir.name,
                    "path": str(project_dir),
                    "available_steps": available_steps,
                    "step_count": len(available_steps)
                }
                
                if metadata:
                    project_info.update({
                        "created_at": metadata.created_at,
                        "updated_at": metadata.updated_at,
                        "last_step": metadata.last_step,
                        "completed_steps": metadata.completed_steps
                    })
                
                projects.append(project_info)
        
        # Sort by most recently updated
        projects.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
        return projects
    
    def delete_project(self, domain: str) -> bool:
        """Delete a project and all its data"""
        project_dir = self.get_project_dir(domain)
        
        if not project_dir.exists():
            return False
        
        try:
            import shutil
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project: {domain}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete project {domain}: {e}")
            return False
    
    def get_dependency_chain(self, domain: str) -> Dict[str, List[str]]:
        """Get the dependency chain for project steps"""
        return {
            "overview": [],
            "account": ["overview"],
            "persona": ["overview", "account"],
            "email": ["overview", "account", "persona"],
            "plan": ["overview", "account", "persona", "email"]
        }
    
    def get_dependent_steps(self, step: str) -> List[str]:
        """Get steps that depend on the given step"""
        dependencies = self.get_dependency_chain("")
        dependent_steps = []
        
        for dependent_step, deps in dependencies.items():
            if step in deps:
                dependent_steps.append(dependent_step)
        
        return dependent_steps
    
    def mark_steps_stale(self, domain: str, changed_step: str) -> List[str]:
        """Mark dependent steps as stale when a step is regenerated"""
        dependent_steps = self.get_dependent_steps(changed_step)
        project_dir = self.get_project_dir(domain)
        
        stale_steps = []
        for step in dependent_steps:
            step_file = project_dir / f"{step}.json"
            if step_file.exists():
                # Add stale marker to the file
                try:
                    with open(step_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    data["_stale"] = True
                    data["_stale_reason"] = f"Dependency '{changed_step}' was regenerated"
                    data["_stale_timestamp"] = datetime.now().isoformat()
                    
                    with open(step_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    stale_steps.append(step)
                    logger.info(f"Marked {step} as stale due to {changed_step} regeneration")
                except Exception as e:
                    logger.error(f"Failed to mark {step} as stale: {e}")
        
        return stale_steps
    
    def _update_project_metadata(self, domain: str, completed_step: str) -> None:
        """Update project metadata when a step is completed"""
        metadata = self.load_metadata(domain)
        if not metadata:
            metadata = ProjectMetadata(
                domain=domain,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        metadata.updated_at = datetime.now()
        metadata.last_step = completed_step
        
        if completed_step not in metadata.completed_steps:
            metadata.completed_steps.append(completed_step)
        
        self.save_metadata(domain, metadata)


# Global instance
project_storage = ProjectStorage()