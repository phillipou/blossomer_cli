"""GTM Advisor service for synthesizing strategic plans from previous analysis."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import csv

from cli.services.llm_singleton import get_llm_client
from cli.services.context_orchestrator_service import ContextOrchestratorService
from app.prompts.base import render_template

logger = logging.getLogger(__name__)


class GTMAdvisorService:
    """Service for creating comprehensive GTM strategic plans."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.orchestrator = ContextOrchestratorService()
    
    async def generate_strategic_plan(
        self, 
        domain: str, 
        project_dir: Optional[Path] = None
    ) -> str:
        """
        Generate a comprehensive GTM strategic plan.
        
        Args:
            domain: Company domain
            project_dir: Optional project directory path
            
        Returns:
            Complete strategic plan as markdown string
        """
        try:
            # Set up project directory
            if project_dir is None:
                project_dir = Path("gtm_projects") / domain
            
            logger.info(f"Generating GTM strategic plan for {domain}")
            
            # Load all required markdown files
            markdown_content = self._load_markdown_files(project_dir)
            
            # Load tools database
            tools_by_category = self._load_tools_database()
            
            # Load the output template
            template_content = self._load_output_template()
            
            # Prepare template context
            context = {
                **markdown_content,
                "tools_by_category": tools_by_category,
                "template_structure": template_content
            }
            
            # Render the prompt using the base template function
            system_prompt, user_prompt = render_template("gtm_advisor", context)
            
            # Generate strategic plan using LLM
            from app.core.forge_llm_service import LLMRequest
            
            llm_request = LLMRequest(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                parameters={"temperature": 0.7, "max_tokens": 8000}
            )
            
            response = await self.llm_client.generate(llm_request)
            strategic_plan = response.text
            
            # Save the strategic plan
            output_path = self._save_strategic_plan(project_dir, strategic_plan)
            
            logger.info(f"GTM strategic plan generated and saved to {output_path}")
            return strategic_plan
            
        except Exception as e:
            logger.error(f"Failed to generate GTM strategic plan for {domain}: {str(e)}")
            raise
    
    def _load_markdown_files(self, project_dir: Path) -> Dict[str, str]:
        """Load all required markdown files from the project directory."""
        plans_dir = project_dir / "plans"
        
        required_files = {
            "overview_content": "overview.md",
            "account_content": "account.md", 
            "persona_content": "persona.md",
            "email_content": "email.md"
        }
        
        markdown_content = {}
        
        for key, filename in required_files.items():
            file_path = plans_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required file {filename} not found in {plans_dir}. "
                    f"Please complete all previous steps before generating strategic plan."
                )
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        raise ValueError(f"File {filename} is empty")
                    markdown_content[key] = content
                    
            except Exception as e:
                raise RuntimeError(f"Failed to read {filename}: {str(e)}")
        
        logger.info(f"Loaded {len(markdown_content)} markdown files")
        return markdown_content
    
    def _load_output_template(self) -> str:
        """Load the output template structure."""
        template_file = Path("app/prompts/templates/gtm_advisor_output.md")
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Template file is empty")
                return content
        except Exception as e:
            raise RuntimeError(f"Failed to read template file: {str(e)}")
    
    def _load_tools_database(self) -> Dict[str, list]:
        """Load the GTM tools database from CSV."""
        tools_file = Path("app/data/gtm_tools.csv")
        
        if not tools_file.exists():
            logger.warning(f"Tools database not found at {tools_file}")
            return {}
        
        tools_by_category = {}
        
        try:
            with open(tools_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    category = row.get('Category', '').strip()
                    if not category:
                        continue
                    
                    tool = {
                        'name': row.get('Tool Name', '').strip(),
                        'description': row.get('Descriptions', '').strip(),
                        'website': row.get('Website', '').strip(),
                        'phils_notes': row.get("Phil's Notes", '').strip() or None,
                        'recommended': row.get('Recommended', '').lower() == 'true'
                    }
                    
                    # Skip tools with missing essential data
                    if not tool['name'] or not tool['description']:
                        continue
                    
                    if category not in tools_by_category:
                        tools_by_category[category] = []
                    
                    tools_by_category[category].append(tool)
            
            logger.info(f"Loaded {sum(len(tools) for tools in tools_by_category.values())} tools across {len(tools_by_category)} categories")
            
        except Exception as e:
            logger.error(f"Failed to load tools database: {str(e)}")
            return {}
        
        return tools_by_category
    
    def _save_strategic_plan(self, project_dir: Path, strategic_plan: str) -> Path:
        """Save the strategic plan to the project directory."""
        # Save to plans directory as markdown
        plans_dir = project_dir / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = plans_dir / "gtm_plan.md"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(strategic_plan)
            
            # Also save metadata
            metadata = {
                "_generated_at": self._get_current_timestamp(),
                "_step": "strategic_plan",
                "_service": "gtm_advisor"
            }
            
            metadata_path = project_dir / "json_output" / "strategic_plan.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save strategic plan: {str(e)}")
        
        return output_path
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_strategic_plan_status(self, domain: str, project_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Check if strategic plan exists and get its status."""
        if project_dir is None:
            project_dir = Path("gtm_projects") / domain
        
        strategic_plan_path = project_dir / "plans" / "gtm_plan.md"
        metadata_path = project_dir / "json_output" / "strategic_plan.json"
        
        if not strategic_plan_path.exists():
            return {
                "exists": False,
                "path": None,
                "metadata": None
            }
        
        # Load metadata if available
        metadata = None
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except Exception:
                pass
        
        return {
            "exists": True,
            "path": strategic_plan_path,
            "metadata": metadata,
            "file_size": strategic_plan_path.stat().st_size
        }
    
    def validate_prerequisites(self, domain: str, project_dir: Optional[Path] = None) -> Dict[str, bool]:
        """Validate that all prerequisite files exist."""
        if project_dir is None:
            project_dir = Path("gtm_projects") / domain
        
        plans_dir = project_dir / "plans"
        required_files = ["overview.md", "account.md", "persona.md", "email.md"]
        
        validation_results = {}
        
        for filename in required_files:
            file_path = plans_dir / filename
            validation_results[filename] = file_path.exists() and file_path.stat().st_size > 0
        
        return validation_results