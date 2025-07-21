"""
Guided Email Builder - Interactive email generation workflow
"""

import questionary
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from cli.utils.console import ensure_breathing_room, clear_console

console = Console()

# Custom style for text inputs to use cyan color
TEXT_INPUT_STYLE = questionary.Style([
    ('question', 'bold #01A0E4'),           # Question text - brand blue
    ('text', '#00BFFF'),                    # Text input - cyan
    ('answer', '#00BFFF')                   # Answer display - cyan
])


class GuidedEmailBuilder:
    """Interactive guided email builder with 5 steps matching PRD specifications"""
    
    def __init__(self, persona_data: Dict[str, Any], account_data: Dict[str, Any]):
        self.persona_data = persona_data
        self.account_data = account_data
        self.selections = {}
        # Extract structured data from persona
        self.use_cases = persona_data.get('use_cases', [])
        self.buying_signals = persona_data.get('buying_signals', [])
        # Track completed steps for display with full Q&A context
        self.completed_steps = []
        self.qa_history = []  # Store question-answer pairs for full context
    
    def run_guided_flow(self) -> Dict[str, Any]:
        """Run the complete 5-step guided email building flow"""
        
        console.print()
        console.print(Panel.fit(
            "[bold #01A0E4]📧 Email Campaign Builder - Guided Mode[/bold #01A0E4]\n\n"
            "We'll walk you through 5 steps to create the perfect email:\n"
            "• 1 What should your email emphasize?\n"
            "• 2 Which specific content to focus on?\n" 
            "• 3 Add social proof (optional)\n"
            "• 4 How should we personalize this email?\n"
            "• 5 What should the call-to-action be?",
            title="[bold #01A0E4]Guided Email Builder[/bold #01A0E4]",
            border_style="#01A0E4"
        ))
        
        # Step 1: Point of Emphasis
        emphasis = self._step_1_emphasis()
        
        # Step 2: Specific Content (based on emphasis choice)
        selected_content = self._step_2_content_selection(emphasis)
        
        # Step 3: Social Proof Collection
        social_proof = self._step_3_social_proof()
        
        # Step 4: Personalization Angle  
        personalization = self._step_4_personalization()
        
        # Step 5: Call-to-Action
        cta = self._step_5_call_to_action()
        
        # Return configuration for email generation
        return {
            "guided_mode": True,
            "emphasis": emphasis["type"],
            "selected_content": selected_content,
            "social_proof": social_proof,
            "personalization": personalization,
            "call_to_action": cta,
            "qa_history": self.qa_history  # Include Q&A history for display
        }
    
    def _step_1_emphasis(self) -> Dict[str, Any]:
        """Step 1: Select point of emphasis"""
        console.print()
        console.print("[bold]Step 1: What should your email emphasize?[/bold]")
        console.print()
        
        choices = [
            "1. Use Case: Focus on specific workflows your solution impacts",
            "2. Pain Point: Focus on challenges they're experiencing",
            "3. Capability: Focus on what your solution can do", 
            "4. Desired Outcome: Focus on the results they want"
        ]
        
        from cli.utils.menu_utils import show_menu_with_numbers
        choice = show_menu_with_numbers(
            "💡 What should be the main focus of your email? (This shapes the entire message):",
            choices=[
                "General Introduction - Company/product overview",
                "Value Proposition - Focus on specific benefits",
                "Pain Point - Address specific challenges",
                "Product Feature - Highlight specific capabilities",
                "Customer Success - Share proof/testimonials",
                "Educational Content - Share insights/resources",
                "Request/Ask - Meeting, demo, or trial"
            ],
            add_separator=False
        )
        
        # Map choice to value
        emphasis_type = choice.split(".")[0].strip()
        if emphasis_type == "1":
            emphasis_value = "use_case"
        elif emphasis_type == "2":
            emphasis_value = "pain_point"
        elif emphasis_type == "3":
            emphasis_value = "capability"
        else:
            emphasis_value = "desired_outcome"
        
        console.print(f"✓ Focusing on {emphasis_value.replace('_', ' ')}")
        console.print()
        
        # Track completed step with Q&A
        self.completed_steps.append(f"Step 1: Focusing on {emphasis_value.replace('_', ' ')}")
        self.qa_history.append({
            "question": "Step 1: What should your email emphasize?",
            "answer": choice
        })
        
        return {"type": emphasis_value}
    
    def _step_2_content_selection(self, emphasis: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Select specific content based on emphasis choice"""
        emphasis_type = emphasis["type"]
        
        # Clear screen and show previous steps
        clear_console()
        self._show_previous_steps()
        
        console.print(f"[bold]Step 2: Which {emphasis_type.replace('_', ' ')} should we focus on?[/bold]")
        console.print()
        console.print(f"Based on your persona analysis, here are their key {emphasis_type.replace('_', ' ')}s:")
        console.print()
        
        # Extract content options based on emphasis type
        content_options = self._extract_content_by_type(emphasis_type)
        
        choices = []
        for option in content_options:
            # For step 2: show only the text after the colon (if there is one)
            display_text = option['value']
            if ':' in display_text:
                display_text = display_text.split(':', 1)[1].strip()
            choices.append(display_text)
        
        # Add "Other" option
        choices.append("Other (specify custom instructions to the LLM)")
        
        from cli.utils.menu_utils import show_menu_with_numbers
        choice = show_menu_with_numbers(
            f"Select {emphasis_type.replace('_', ' ')}:",
            choices=choices,
            add_separator=False
        )
        
        # Find which option was selected
        choice_idx = choices.index(choice) if choice in choices else len(choices) - 1
        
        if choice_idx == len(content_options):  # "Other" option selected
            custom_instructions = questionary.text(
                "🎯 Describe what you want the AI to focus on:",
                placeholder="e.g., Emphasize cost savings, mention recent industry trends, focus on security benefits",
                style=TEXT_INPUT_STYLE
            ).ask()
            ensure_breathing_room(console)
            selected_content = {
                "type": emphasis_type,
                "value": "Custom",
                "description": custom_instructions,
                "custom_instructions": custom_instructions,
                "custom": True
            }
        else:
            selected_content = content_options[choice_idx]
            selected_content["custom"] = False
        
        console.print(f"✓ Selected: {selected_content['value']}")
        console.print()
        
        # Track completed step with Q&A
        self.completed_steps.append(f"Step 2: Selected {selected_content['value']}")
        self.qa_history.append({
            "question": f"Step 2: Which {emphasis_type.replace('_', ' ')} should we focus on?",
            "answer": choice
        })
        
        return selected_content
    
    def _step_3_social_proof(self) -> Optional[str]:
        """Step 3: Collect social proof (optional)"""
        # Clear screen and show previous steps
        clear_console()
        self._show_previous_steps()
        
        console.print("[bold]Step 3: Add Social Proof (Optional)[/bold]")
        console.print()
        console.print("💪 Social proof adds credibility to your outreach")
        console.print("Examples: client wins, case studies, impressive metrics, or notable partnerships")
        console.print()
        
        social_proof = questionary.text(
            "Add social proof (optional):",
            placeholder="e.g., We helped 50+ companies reduce churn by 25% | Recently worked with Stripe on scaling | Featured in TechCrunch",
            style=TEXT_INPUT_STYLE
        ).ask()
        
        ensure_breathing_room(console)
        
        if social_proof and social_proof.strip():
            console.print("✓ Social proof added")
            console.print()
            
            # Track completed step with Q&A
            self.completed_steps.append("Step 3: Social proof added")
            self.qa_history.append({
                "question": "Step 3: Add Social Proof (Optional)",
                "answer": f"Added: {social_proof.strip()}"
            })
            
            return social_proof.strip()
        else:
            console.print("✓ Skipping social proof")
            console.print()
            
            # Track completed step with Q&A
            self.completed_steps.append("Step 3: Skipping social proof")
            self.qa_history.append({
                "question": "Step 3: Add Social Proof (Optional)",
                "answer": "Skipped - no social proof added"
            })
            
            return None
    
    def _step_4_personalization(self) -> Dict[str, Any]:
        """Step 4: Select personalization angle"""
        # Clear screen and show previous steps
        clear_console()
        self._show_previous_steps()
        
        console.print("[bold]Step 4: How should we personalize this email?[/bold]")
        console.print()
        console.print("Based on your target account analysis:")
        console.print()
        
        # Extract personalization options from buying signals
        personalization_options = self._extract_buying_signals_for_personalization()
        
        choices = []
        # Add "No Personalization" first
        choices.append("No Personalization (generic outreach)")
        
        for option in personalization_options:
            # For step 3: show only the text before the colon (if there is one)
            display_text = option['title']
            if ':' in display_text:
                display_text = display_text.split(':', 1)[0].strip()
            choices.append(display_text)
        
        # Add "Other" option
        choices.append("Other (specify custom instructions to the LLM)")
        
        from cli.utils.menu_utils import show_menu_with_numbers
        choice = show_menu_with_numbers(
            f"Select personalization:",
            choices=choices,
            add_separator=False
        )
        
        # Find which option was selected
        choice_idx = choices.index(choice) if choice in choices else len(choices) - 1
        
        if choice_idx == 0:  # "No Personalization" option selected
            selected_personalization = {
                "type": "not-personalized",
                "value": "No Personalization",
                "title": "No Personalization",
                "custom": False
            }
        elif choice_idx == len(choices) - 1:  # "Other" option selected
            custom_instructions = questionary.text(
                "Enter custom personalization instructions for the LLM:",
                placeholder="e.g., Reference their recent product launch...",
                style=TEXT_INPUT_STYLE
            ).ask()
            ensure_breathing_room(console)
            
            # Pass custom instructions to the LLM - it will handle uncertainty detection
            selected_personalization = {
                "type": "custom",
                "value": "Custom personalization",
                "custom_instructions": custom_instructions,
                "custom": True
            }
        else:
            selected_personalization = personalization_options[choice_idx - 1]  # -1 because "No Personalization" is first
            selected_personalization["custom"] = False
        
        console.print(f"✓ Will reference: {selected_personalization.get('title', 'custom approach')}")
        console.print()
        
        # Track completed step with Q&A
        self.completed_steps.append(f"Step 4: Will reference {selected_personalization.get('title', 'custom approach')}")
        self.qa_history.append({
            "question": "Step 4: How should we personalize this email?",
            "answer": choice
        })
        
        return selected_personalization
    
    def _step_5_call_to_action(self) -> Dict[str, Any]:
        """Step 5: Select call-to-action"""
        # Clear screen and show previous steps
        clear_console()
        self._show_previous_steps()
        
        console.print("[bold]Step 5: What should the call-to-action be?[/bold]")
        console.print()
        
        cta_options = [
            {
                "type": "meeting",
                "text": "Worth a quick 15-min call next week?",
                "intent": "schedule_meeting",
                "label": "Ask for a meeting"
            },
            {
                "type": "priority_check",
                "text": "Is improving support efficiency a Q1 priority?",
                "intent": "gauge_interest",
                "label": "Ask if it's a priority"
            },
            {
                "type": "feedback",
                "text": "Curious if this resonates with your experience?",
                "intent": "start_conversation",
                "label": "Ask for feedback"
            },
            {
                "type": "free_help",
                "text": "Happy to share our scaling playbook - interested?",
                "intent": "provide_value",
                "label": "Offer free help"
            },
            {
                "type": "resource",
                "text": "We have a guide on this - should I send it over?",
                "intent": "share_content",
                "label": "Invite to resource"
            }
        ]
        
        choices = []
        for option in cta_options:
            choices.append(f"{option['label']} (e.g. {option['text']})")
        
        # Add "Other" option
        choices.append("Other (write your own custom CTA)")
        
        from cli.utils.menu_utils import show_menu_with_numbers
        choice = show_menu_with_numbers(
            f"Select CTA:",
            choices=choices,
            add_separator=False
        )
        
        # Find which option was selected
        choice_idx = choices.index(choice) if choice in choices else len(choices) - 1
        
        if choice_idx == len(cta_options):  # "Other" option selected
            custom_cta = questionary.text(
                "Enter your custom call-to-action:",
                placeholder="e.g., Would you like to see how this works in action?",
                style=TEXT_INPUT_STYLE
            ).ask()
            ensure_breathing_room(console)
            selected_cta = {
                "type": "custom",
                "text": custom_cta,
                "intent": "custom_action",
                "custom": True
            }
        else:
            selected_cta = cta_options[choice_idx]
            selected_cta["custom"] = False
        
        console.print(f"✓ Will {selected_cta['intent'].replace('_', ' ')}")
        console.print()
        
        # Track completed step with Q&A
        self.completed_steps.append(f"Step 5: Will {selected_cta['intent'].replace('_', ' ')}")
        self.qa_history.append({
            "question": "Step 5: What should the call-to-action be?",
            "answer": choice
        })
        
        return selected_cta
    
    def _show_previous_steps(self) -> None:
        """Show all completed steps with full Q&A context at the top of the screen"""
        if self.qa_history:
            console.print("✓ Previous steps:")
            for qa in self.qa_history:
                console.print(f"  [bold]{qa['question']}[/bold]")
                console.print(f"  → {qa['answer']}")
                console.print()
            console.print()
    
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
    
    def _extract_content_by_type(self, emphasis_type: str) -> List[Dict[str, Any]]:
        """Extract content options based on emphasis type from use_cases array"""
        content_options = []
        
        for use_case in self.use_cases:
            if isinstance(use_case, dict):
                if emphasis_type == "use_case":
                    content_options.append({
                        "type": "use_case",
                        "value": use_case.get("use_case", "Unknown use case"),
                        "description": use_case.get("use_case", "Unknown use case")
                    })
                elif emphasis_type == "pain_point":
                    content_options.append({
                        "type": "pain_point", 
                        "value": use_case.get("pain_points", "Unknown pain point"),
                        "description": use_case.get("pain_points", "Unknown pain point")
                    })
                elif emphasis_type == "capability":
                    content_options.append({
                        "type": "capability",
                        "value": use_case.get("capability", "Unknown capability"),
                        "description": use_case.get("capability", "Unknown capability")
                    })
                elif emphasis_type == "desired_outcome":
                    content_options.append({
                        "type": "desired_outcome",
                        "value": use_case.get("desired_outcome", "Unknown outcome"),
                        "description": use_case.get("desired_outcome", "Unknown outcome")
                    })
        
        # Return first 3 unique options or defaults if none found
        unique_options = []
        seen_values = set()
        for option in content_options:
            if option["value"] not in seen_values:
                unique_options.append(option)
                seen_values.add(option["value"])
                if len(unique_options) >= 3:
                    break
        
        # Fallback defaults if no content found
        if not unique_options:
            if emphasis_type == "pain_point":
                unique_options = [
                    {"type": "pain_point", "value": "Scaling challenges", "description": "Maintaining quality during rapid growth"},
                    {"type": "pain_point", "value": "Long onboarding times", "description": "New team members take too long to be productive"},
                    {"type": "pain_point", "value": "Lack of visibility", "description": "No insight into performance gaps"}
                ]
            elif emphasis_type == "capability":
                unique_options = [
                    {"type": "capability", "value": "Real-time analysis", "description": "Analyze performance in real-time"},
                    {"type": "capability", "value": "Automated coaching", "description": "Provide automated guidance and suggestions"},
                    {"type": "capability", "value": "Knowledge gap detection", "description": "Identify areas needing improvement"}
                ]
            elif emphasis_type == "use_case":
                unique_options = [
                    {"type": "use_case", "value": "Quality assurance", "description": "Ensure consistent service quality"},
                    {"type": "use_case", "value": "Team training", "description": "Accelerate team onboarding and training"},
                    {"type": "use_case", "value": "Performance monitoring", "description": "Monitor and improve team performance"}
                ]
            else:  # desired_outcome
                unique_options = [
                    {"type": "desired_outcome", "value": "Improved efficiency", "description": "Faster resolution times and better productivity"},
                    {"type": "desired_outcome", "value": "Higher quality", "description": "More consistent and accurate service delivery"},
                    {"type": "desired_outcome", "value": "Reduced costs", "description": "Lower training costs and improved ROI"}
                ]
        
        return unique_options
    
    def _extract_buying_signals_for_personalization(self) -> List[Dict[str, Any]]:
        """Extract buying signals that can be used for personalization"""
        personalization_options = []
        
        for signal in self.buying_signals:
            if isinstance(signal, dict):
                personalization_options.append({
                    "type": "buying_signal",
                    "title": signal.get("title", "Company activity"),
                    "description": signal.get("description", "Recent company activity"),
                    "example": f"Reference {signal.get('title', 'recent activity')}: \"{signal.get('description', 'activity suggests opportunity')}\""
                })
        
        # Return first 4 options or defaults if none found
        if personalization_options:
            return personalization_options[:4]
        
        # Fallback defaults if no buying signals found
        return [
            {
                "type": "funding",
                "title": "Recent funding round",
                "description": "Recent Series B funding",
                "example": "Congrats on the Series B - scaling challenges ahead?"
            },
            {
                "type": "hiring",
                "title": "Hiring activity",
                "description": "Active hiring in support team",
                "example": "Saw you're hiring 10+ support agents this quarter"
            },
            {
                "type": "growth",
                "title": "Company growth",
                "description": "Rapid company growth metrics",
                "example": "With 200% YoY growth, support must be challenging"
            },
            {
                "type": "tech_stack",
                "title": "Technology adoption",
                "description": "Recent technology adoption",
                "example": "Notice you recently adopted Zendesk - scaling pains?"
            }
        ]