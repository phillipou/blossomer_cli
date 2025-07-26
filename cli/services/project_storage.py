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
        self.state_file = self.base_dir / ".blossomer-state.json"
    
    def get_project_dir(self, domain: str) -> Path:
        """Get the project directory for a given domain"""
        # Normalize domain for filesystem
        safe_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        safe_domain = safe_domain.replace("/", "_").replace(":", "_")
        result_path = self.base_dir / safe_domain
        logger.info(f"get_project_dir: {domain} -> {safe_domain} -> {result_path}")
        return result_path
    
    def create_project(self, domain: str) -> Path:
        """Create a new project directory and metadata"""
        project_dir = self.get_project_dir(domain)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create json_output subdirectory for all JSON files
        json_output_dir = project_dir / "json_output"
        json_output_dir.mkdir(exist_ok=True)
        
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
        
        # Save to json_output directory
        json_output_dir = project_dir / "json_output"
        json_output_dir.mkdir(exist_ok=True)
        step_file = json_output_dir / f"{step}.json"
        with open(step_file, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        # Auto-generate corresponding markdown file in plans/ directory
        try:
            self._auto_generate_plans_file(domain, step, data_dict)
        except Exception as e:
            logger.warning(f"Failed to auto-generate plans file for {step}: {e}")
        
        # Update metadata
        self._update_project_metadata(domain, step)
        
        logger.info(f"Saved {step} data to {step_file}")
        return step_file
    
    def load_step_data(self, domain: str, step: str) -> Optional[Dict[str, Any]]:
        """Load data for a specific step"""
        project_dir = self.get_project_dir(domain)
        step_file = project_dir / "json_output" / f"{step}.json"
        
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
        step_files = ["overview.json", "account.json", "persona.json", "email.json", "strategy.json"]
        json_output_dir = project_dir / "json_output"
        
        for step_file in step_files:
            if (json_output_dir / step_file).exists():
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
            "strategy": ["overview", "account", "persona", "email"]
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
        json_output_dir = project_dir / "json_output"
        for step in dependent_steps:
            step_file = json_output_dir / f"{step}.json"
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
    
    def get_file_path(self, domain: str, step: str) -> Path:
        """Get the file path for a specific step's markdown file"""
        project_dir = self.get_project_dir(domain)
        plans_dir = project_dir / "plans"
        
        # Map step keys to actual filenames
        step_to_filename = {
            "overview": "overview.md",
            "account": "account.md", 
            "persona": "persona.md",
            "email": "email.md",
            "plan": "strategy.md",  # plan step maps to strategy.md
            "advisor": "strategy.md"  # advisor step also maps to strategy.md
        }
        
        filename = step_to_filename.get(step, f"{step}.md")
        return plans_dir / filename
    
    def _auto_generate_plans_file(self, domain: str, step: str, data_dict: Dict[str, Any]) -> None:
        """Auto-generate markdown file in plans/ directory when JSON is saved"""
        try:
            # Import here to avoid circular dependencies
            from cli.utils.markdown_formatter import get_formatter
            
            # Create plans directory
            project_dir = self.get_project_dir(domain)
            plans_dir = project_dir / "plans"
            plans_dir.mkdir(exist_ok=True)
            
            # Get formatter and generate structured markdown
            formatter = get_formatter(step)
            markdown_content = formatter.format_with_markers(data_dict, step)
            
            # Save markdown file using the same filename mapping as get_file_path
            step_to_filename = {
                "overview": "overview.md",
                "account": "account.md", 
                "persona": "persona.md",
                "email": "email.md",
                "plan": "strategy.md",  # plan step maps to strategy.md
                "advisor": "strategy.md"  # advisor step also maps to strategy.md
            }
            filename = step_to_filename.get(step, f"{step}.md")
            plans_file = plans_dir / filename
            with open(plans_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Auto-generated plans file: {plans_file}")
            
        except Exception as e:
            logger.error(f"Failed to auto-generate plans file for {step}: {e}")
            # Don't raise - this is a nice-to-have feature that shouldn't break JSON saving


# Global instance
project_storage = ProjectStorage()