# app/prompts/runner.py
from openai import OpenAI
from .registry import TEMPLATE_REGISTRY, render_template

client = OpenAI()

def run_prompt(template_name: str, variables: BaseModel):
    entry = TEMPLATE_REGISTRY[template_name]

    # Jinja render
    sys_prompt, user_prompt = render_template(entry["template"], variables.model_dump())

    # Call LLM (adjust as needed)
    raw_json = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sys_prompt} if sys_prompt else {},
            {"role": "user", "content": user_prompt},
        ],
    ).choices[0].message.content

    # Validate with the output model
    return entry["response_model"].model_validate_json(raw_json)
