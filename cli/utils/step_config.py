"""
Step configuration for GTM generation pipeline
Centralized configuration to eliminate hardcoded values and improve scalability
"""

from typing import Dict, List, NamedTuple, Optional
from dataclasses import dataclass

@dataclass
class StepConfig:
    """Configuration for a single GTM generation step"""
    key: str
    name: str
    explanation: str
    icon: str
    preview_title: str
    file_name: str
    
    def get_step_panel_title(self, step_number: int, total_steps: int) -> str:
        """Get the panel title for this step"""
        return f"[bold #0066CC][{step_number}/{total_steps}] {self.name}[/bold #0066CC]"

# GTM Pipeline Configuration
GTM_STEPS = [
    StepConfig(
        key="overview",
        name="Company Overview",
        explanation="Analyzing your website to understand your business, products, and value proposition",
        icon="📋",
        preview_title="COMPANY OVERVIEW - Preview",
        file_name="overview.json"
    ),
    StepConfig(
        key="account",
        name="Target Account Profile", 
        explanation="Identifying your ideal customer companies based on your business analysis",
        icon="🎯",
        preview_title="TARGET ACCOUNT - Preview",
        file_name="account.json"
    ),
    StepConfig(
        key="persona",
        name="Buyer Persona",
        explanation="Creating detailed profiles of decision-makers at your target companies",
        icon="👤",
        preview_title="BUYER PERSONA - Preview", 
        file_name="persona.json"
    ),
    StepConfig(
        key="email",
        name="Email Campaign",
        explanation="Crafting personalized outreach emails based on your analysis",
        icon="📧",
        preview_title="EMAIL CAMPAIGN - Preview",
        file_name="email.json"
    ),
    StepConfig(
        key="strategy",
        name="GTM Strategic Plan",
        explanation="Creating comprehensive go-to-market execution plan with scoring frameworks and tool recommendations",
        icon="🎯",
        preview_title="STRATEGIC PLAN - Preview",
        file_name="strategy.json"
    )
]

class StepManager:
    """Centralized step management for GTM pipeline"""
    
    def __init__(self):
        self.steps = GTM_STEPS
        self.step_by_key = {step.key: step for step in self.steps}
        self.total_steps = len(self.steps)
    
    def get_step(self, key: str) -> Optional[StepConfig]:
        """Get step configuration by key"""
        return self.step_by_key.get(key)
    
    def get_step_number(self, key: str) -> int:
        """Get step number (1-indexed) by key"""
        for i, step in enumerate(self.steps):
            if step.key == key:
                return i + 1
        return 0
    
    def get_total_steps(self) -> int:
        """Get total number of steps"""
        return self.total_steps
    
    def get_step_keys(self) -> List[str]:
        """Get all step keys in order"""
        return [step.key for step in self.steps]
    
    def get_steps_from_key(self, start_key: str) -> List[StepConfig]:
        """Get all steps starting from a given key"""
        try:
            start_index = self.get_step_keys().index(start_key)
            return self.steps[start_index:]
        except ValueError:
            return []
    
    def get_step_by_number(self, number: int) -> Optional[StepConfig]:
        """Get step by number (1-indexed)"""
        if 1 <= number <= self.total_steps:
            return self.steps[number - 1]
        return None
    
    def is_last_step(self, key: str) -> bool:
        """Check if a step is the last step in the pipeline"""
        return key == self.steps[-1].key if self.steps else False
    
    def get_next_step(self, key: str) -> Optional[StepConfig]:
        """Get the next step after the given key"""
        try:
            current_index = self.get_step_keys().index(key)
            if current_index + 1 < len(self.steps):
                return self.steps[current_index + 1]
            return None
        except ValueError:
            return None
    
    def get_next_step_name(self, key: str) -> str:
        """Get the display name for the next step"""
        next_step = self.get_next_step(key)
        if next_step:
            # Map to user-friendly names
            name_mapping = {
                "overview": "Target Accounts",
                "account": "Target Personas", 
                "persona": "Email Campaign",
                "email": "Create GTM plan",
                "advisor": ""
            }
            return name_mapping.get(key, next_step.name)
        return ""

# Global step manager instance
step_manager = StepManager()