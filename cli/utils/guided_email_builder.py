"""
Guided Email Builder - Interactive email generation workflow
"""

import questionary
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


class GuidedEmailBuilder:
    """Interactive guided email builder with 4 steps"""
    
    def __init__(self, persona_data: Dict[str, Any], account_data: Dict[str, Any]):
        self.persona_data = persona_data
        self.account_data = account_data
        self.selections = {}
    
    def run_guided_flow(self) -> Dict[str, Any]:
        """Run the complete 4-step guided email building flow"""
        
        console.print()
        console.print(Panel.fit(
            "[bold blue]📧 Email Campaign Builder - Guided Mode[/bold blue]\n\n"
            "We'll walk you through 4 steps to create the perfect email:\n"
            "• [green]1/4[/green] What should your email emphasize?\n"
            "• [green]2/4[/green] Which specific pain point to focus on?\n" 
            "• [green]3/4[/green] How should we personalize this email?\n"
            "• [green]4/4[/green] What should the call-to-action be?",
            title="[bold]Guided Email Builder[/bold]",
            border_style="blue"
        ))
        
        # Step 1: Point of Emphasis
        emphasis = self._step_1_emphasis()
        
        # Step 2: Specific Pain Point (based on emphasis choice)
        pain_point = self._step_2_pain_point(emphasis)
        
        # Step 3: Personalization Angle
        personalization = self._step_3_personalization()
        
        # Step 4: Call-to-Action
        cta = self._step_4_call_to_action()
        
        # Return configuration for email generation
        return {
            "guided_mode": True,
            "emphasis": emphasis,
            "pain_point": pain_point,
            "personalization": personalization,
            "call_to_action": cta
        }
    
    def _step_1_emphasis(self) -> Dict[str, Any]:
        """Step 1: Select point of emphasis"""
        console.print()
        console.print("[bold]Step 1/4: What should your email emphasize?[/bold]")
        console.print()
        
        choices = [
            "1. Pain Point: Focus on challenges they're experiencing",
            "2. Capability: Focus on what your solution can do", 
            "3. Desired Outcome: Focus on the results they want"
        ]
        
        choice = questionary.select(
            "Select emphasis [1-3]:",
            choices=choices
        ).ask()
        
        # Map choice to value
        emphasis_type = choice.split(".")[0].strip()
        if emphasis_type == "1":
            emphasis_value = "pain_point"
        elif emphasis_type == "2":
            emphasis_value = "capability"
        else:
            emphasis_value = "outcome"
        
        console.print(f"✓ Focusing on {emphasis_value.replace('_', ' ')}")
        console.print()
        
        return {"type": emphasis_value}
    
    def _step_2_pain_point(self, emphasis: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Select specific pain point"""
        console.print("[bold]Step 2/4: Which pain point should we focus on?[/bold]")
        console.print()
        console.print("Based on your persona analysis, here are their key pain points:")
        console.print()
        
        # Extract pain points from persona data
        pain_points = self._extract_pain_points()
        
        choices = []
        for i, pain_point in enumerate(pain_points[:3], 1):
            choices.append(f"{i}. {pain_point['title']}\n   \"{pain_point['description']}\"")
        
        choices.append("4. Other (specify your own)")
        
        choice = questionary.select(
            "Select pain point [1-4]:",
            choices=choices
        ).ask()
        
        if choice.startswith("4."):
            custom_pain = questionary.text("Enter your custom pain point:").ask()
            selected_pain = {
                "title": "Custom Pain Point",
                "description": custom_pain,
                "custom": True
            }
        else:
            # Extract the number and get the corresponding pain point
            choice_num = int(choice.split(".")[0]) - 1
            selected_pain = pain_points[choice_num]
        
        console.print(f"✓ Selected: {selected_pain['title']}")
        console.print()
        
        return selected_pain
    
    def _step_3_personalization(self) -> Dict[str, Any]:
        """Step 3: Select personalization angle"""
        console.print("[bold]Step 3/4: How should we personalize this email?[/bold]")
        console.print()
        console.print("Based on your target account analysis:")
        console.print()
        
        # Extract personalization options from account data
        personalization_options = self._extract_personalization_options()
        
        choices = ["1. No personalization (generic approach)"]
        
        for i, option in enumerate(personalization_options, 2):
            choices.append(f"{i}. {option['name']}\n   \"{option['example']}\"")
        
        choices.append(f"{len(personalization_options) + 2}. Other (specify your own)")
        
        choice = questionary.select(
            "Select personalization [1-5]:",
            choices=choices
        ).ask()
        
        choice_num = int(choice.split(".")[0])
        
        if choice_num == 1:
            selected_personalization = {"type": "generic", "angle": "none"}
        elif choice_num == len(personalization_options) + 2:
            custom_angle = questionary.text("Enter your custom personalization angle:").ask()
            selected_personalization = {
                "type": "custom",
                "angle": custom_angle,
                "example": f"Custom approach: {custom_angle}"
            }
        else:
            selected_personalization = personalization_options[choice_num - 2]
        
        console.print(f"✓ Will use: {selected_personalization.get('name', selected_personalization.get('angle', 'custom approach'))}")
        console.print()
        
        return selected_personalization
    
    def _step_4_call_to_action(self) -> Dict[str, Any]:
        """Step 4: Select call-to-action"""
        console.print("[bold]Step 4/4: What should the call-to-action be?[/bold]")
        console.print()
        
        choices = [
            "1. Ask for a meeting\n   \"Worth a quick 15-min call next week?\"",
            "2. Ask if it's a priority\n   \"Is improving support efficiency a Q1 priority?\"", 
            "3. Ask for feedback\n   \"Curious if this resonates with your experience?\"",
            "4. Offer free help\n   \"Happy to share our scaling playbook - interested?\"",
            "5. Invite to resource\n   \"We have a guide on this - should I send it over?\""
        ]
        
        choice = questionary.select(
            "Select CTA [1-5]:",
            choices=choices
        ).ask()
        
        choice_num = int(choice.split(".")[0])
        
        cta_options = [
            {
                "type": "meeting",
                "text": "Worth a quick 15-min call next week?",
                "intent": "schedule_meeting"
            },
            {
                "type": "priority_check",
                "text": "Is improving support efficiency a Q1 priority?",
                "intent": "gauge_interest"
            },
            {
                "type": "feedback",
                "text": "Curious if this resonates with your experience?",
                "intent": "start_conversation"
            },
            {
                "type": "free_help",
                "text": "Happy to share our scaling playbook - interested?",
                "intent": "provide_value"
            },
            {
                "type": "resource",
                "text": "We have a guide on this - should I send it over?",
                "intent": "share_content"
            }
        ]
        
        selected_cta = cta_options[choice_num - 1]
        
        console.print(f"✓ Will {selected_cta['intent'].replace('_', ' ')}")
        console.print()
        
        return selected_cta
    
    def _extract_pain_points(self) -> List[Dict[str, Any]]:
        """Extract pain points from persona data"""
        default_pain_points = [
            {
                "title": "Maintaining support quality during rapid scaling",
                "description": "As teams grow from 10 to 50 agents, consistency drops"
            },
            {
                "title": "Long agent onboarding times",
                "description": "New agents take 6+ weeks to reach full productivity"
            },
            {
                "title": "Lack of visibility into knowledge gaps",
                "description": "No way to identify what agents don't know until customers complain"
            }
        ]
        
        # Try to extract from persona data if available
        persona_pain_points = []
        if self.persona_data:
            # Check various fields for pain points
            pain_fields = ["pain_points", "challenges", "biggest_challenges", "problems"]
            for field in pain_fields:
                if field in self.persona_data:
                    points = self.persona_data[field]
                    if isinstance(points, list):
                        for point in points:
                            if isinstance(point, dict):
                                persona_pain_points.append({
                                    "title": point.get("title", point.get("challenge", str(point))),
                                    "description": point.get("description", point.get("detail", ""))
                                })
                            else:
                                persona_pain_points.append({
                                    "title": str(point),
                                    "description": f"Challenge: {point}"
                                })
        
        # Return persona pain points if available, otherwise defaults
        return persona_pain_points[:3] if persona_pain_points else default_pain_points
    
    def _extract_personalization_options(self) -> List[Dict[str, Any]]:
        """Extract personalization options from account data"""
        default_options = [
            {
                "type": "funding",
                "name": "Reference recent Series B funding",
                "angle": "recent_funding",
                "example": "Congrats on the Series B - scaling challenges ahead?"
            },
            {
                "type": "hiring",
                "name": "Reference hiring spree",
                "angle": "hiring_growth", 
                "example": "Saw you're hiring 10+ support agents this quarter"
            },
            {
                "type": "growth",
                "name": "Reference company growth metrics",
                "angle": "company_growth",
                "example": "With 200% YoY growth, support must be challenging"
            }
        ]
        
        # Try to extract from account data if available
        account_options = []
        if self.account_data:
            # Check for buying signals that could be personalization angles
            buying_signals = self.account_data.get("buying_signals", [])
            for signal in buying_signals[:3]:
                if isinstance(signal, dict):
                    account_options.append({
                        "type": "buying_signal",
                        "name": f"Reference {signal.get('title', 'company activity')}",
                        "angle": signal.get('signal_type', 'activity'),
                        "example": signal.get('description', 'Recent company activity suggests opportunity')
                    })
        
        # Return account options if available, otherwise defaults
        return account_options if account_options else default_options