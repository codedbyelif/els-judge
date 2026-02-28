import json
import logging
from typing import Optional
from litellm import acompletion
from schemas.api import LLMSuggestion
from core.config import settings

logger = logging.getLogger("llm_consensus_engine.reviewers")

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "improved_code": {"type": "string"},
        "explanation": {"type": "string"},
        "changes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line_range": {"type": "string"},
                    "original": {"type": "string"},
                    "improved": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["line_range", "original", "improved", "reason"]
            }
        }
    },
    "required": ["improved_code", "explanation", "changes"]
}

async def run_llm_review(model_name: str, code: str, prompt: str) -> Optional[LLMSuggestion]:
    """
    Sends user's code and prompt to an LLM model.
    The model returns an improved version of the code with explanations.
    """
    system_prompt = (
        "You are an expert software engineer. The user will give you their code and an instruction. "
        "You must improve/modify the code according to the instruction. "
        "Return your response strictly as a JSON object matching this schema: "
        f"{json.dumps(JSON_SCHEMA)}\n\n"
        "Rules:\n"
        "- 'improved_code' must contain the FULL improved version of the code.\n"
        "- 'explanation' is a brief summary of what you changed and why.\n"
        "- 'changes' is a list of specific modifications you made, each with the original snippet, improved snippet, the line range, and reason.\n"
        "- If no changes are needed, return the original code with an empty changes array."
    )

    user_prompt = f"My Code:\n```\n{code}\n```\n\nInstruction: {prompt}"

    try:
        response = await acompletion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if "gpt" in model_name or "claude" in model_name else None,
            timeout=45
        )

        content = response.choices[0].message.content

        # Clean markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()

        return LLMSuggestion.model_validate_json(content)

    except Exception as e:
        logger.error(f"Error running review on {model_name}: {e}")
        return None
