"""
Constants and enums for CLI menus and choices
"""
from enum import Enum
from typing import Dict


class EmailGenerationMode(Enum):
    """Email generation mode choices"""
    GUIDED = "guided"
    AUTOMATIC = "automatic"


class MenuChoices:
    """Menu choice constants to avoid brittle string matching"""
    
    # Email generation mode choices
    EMAIL_MODE_GUIDED = "🎯 Guided Builder (5-step interactive process ~2 min)"
    EMAIL_MODE_AUTOMATIC = "⚡ Automatic (AI generates based on your analysis ~30 sec)"
    
    # Starting point choices
    START_FRESH = "🔄 Start from beginning (all steps)"
    START_FROM_COMPANY = "📊 Start from Company Overview"
    START_FROM_ACCOUNT = "🏢 Start from Target Account Profile"
    START_FROM_PERSONA = "👤 Start from Buyer Persona"
    START_FROM_EMAIL = "📧 Start from Email Campaign"
    START_FROM_PLAN = "🎯 Start from GTM Strategic Plan"
    CANCEL = "❌ Cancel (view existing results)"
    
    @classmethod
    def get_email_mode(cls, choice: str) -> EmailGenerationMode:
        """Get email generation mode from menu choice"""
        if choice == cls.EMAIL_MODE_GUIDED:
            return EmailGenerationMode.GUIDED
        elif choice == cls.EMAIL_MODE_AUTOMATIC:
            return EmailGenerationMode.AUTOMATIC
        else:
            raise ValueError(f"Unknown email mode choice: {choice}")
    
    @classmethod
    def get_starting_step(cls, choice: str) -> str:
        """Get starting step from menu choice"""
        mapping = {
            cls.START_FRESH: "overview",
            cls.START_FROM_COMPANY: "overview",
            cls.START_FROM_ACCOUNT: "account",
            cls.START_FROM_PERSONA: "persona",
            cls.START_FROM_EMAIL: "email",
            cls.START_FROM_PLAN: "plan",
        }
        return mapping.get(choice, "")