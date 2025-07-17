"""
Configuration management for evaluation system.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EvalConfig:
    """Configuration for a single prompt evaluation."""
    
    name: str
    prompt_name: str
    service_module: str
    service_function: str
    schema_path: Optional[str] = None
    deterministic_checks: Optional[List[str]] = None
    llm_judges: Optional[List[str]] = None
    default_model: str = "OpenAI/gpt-4.1-nano"
    fallback_model: str = "Gemini/models/gemini-1.5-flash"
    
    @classmethod
    def load_prompt_config(cls, prompt_name: str) -> Optional['EvalConfig']:
        """Load configuration for a specific prompt."""
        config_path = Path(f"evals/prompts/{prompt_name}/config.yaml")
        
        if not config_path.exists():
            return None
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            return cls(
                name=config_data.get("name", f"{prompt_name} Evaluation"),
                prompt_name=prompt_name,
                service_module=config_data.get("service", {}).get("module", ""),
                service_function=config_data.get("service", {}).get("function", ""),
                schema_path=config_data.get("schema"),
                deterministic_checks=config_data.get("judges", {}).get("deterministic"),
                llm_judges=config_data.get("judges", {}).get("llm"),
                default_model=config_data.get("models", {}).get("default", "OpenAI/gpt-4.1-nano"),
                fallback_model=config_data.get(
                    "models", {}
                ).get("fallback", "Gemini/models/gemini-1.5-flash")
            )
            
        except Exception as e:
            print(f"Error loading config for {prompt_name}: {e}")
            return None
    
    @classmethod
    def list_available_prompts(cls) -> List[str]:
        """List all available prompt configurations."""
        prompts_dir = Path("evals/prompts")
        if not prompts_dir.exists():
            return []
        
        available_prompts = []
        for prompt_dir in prompts_dir.iterdir():
            if prompt_dir.is_dir() and (prompt_dir / "config.yaml").exists():
                available_prompts.append(prompt_dir.name)
        
        return sorted(available_prompts)
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        if not self.name:
            errors.append("Name is required")
        
        if not self.prompt_name:
            errors.append("Prompt name is required")
        
        if not self.service_module:
            errors.append("Service module is required")
        
        if not self.service_function:
            errors.append("Service function is required")
        
        # Check if schema file exists if specified
        if self.schema_path:
            schema_path = Path(f"evals/prompts/{self.prompt_name}/{self.schema_path}")
            if not schema_path.exists():
                errors.append(f"Schema file not found: {schema_path}")
        
        return errors