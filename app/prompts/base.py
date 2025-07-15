"""
base.py - Core template engine logic for prompt rendering and validation.
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Optional, Tuple

TEMPLATE_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["jinja2"])
)


def render_template(template_name: str, variables: dict) -> Tuple[Optional[str], str]:
    """
    Render a Jinja2 template with the given variables.
    Returns a tuple of (system_prompt, user_prompt).
    """
    template = env.get_template(f"{template_name}.jinja2")
    rendered = template.render(**variables)

    # Split on {# User Prompt #} to separate system and user prompts
    parts = rendered.split("{# User Prompt #}")
    if len(parts) == 2:
        system_prompt = parts[0].strip()
        user_prompt = parts[1].strip()
    else:
        # For backward compatibility, treat the whole template as user prompt
        system_prompt = None
        user_prompt = rendered.strip()

    return system_prompt, user_prompt
