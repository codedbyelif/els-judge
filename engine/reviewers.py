import json
import logging
import os
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
        "- If no changes are needed, return the original code with an empty changes array.\n"
        "- Return ONLY the JSON object, no markdown formatting, no code blocks."
    )

    user_prompt = f"My Code:\n```\n{code}\n```\n\nInstruction: {prompt}"

    # Build kwargs
    kwargs = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "timeout": 60
    }

    # Only set response_format for OpenAI models (not Claude, not Gemini)
    if "gpt" in model_name:
        kwargs["response_format"] = {"type": "json_object"}

    # Pass API key explicitly for Gemini
    if "gemini" in model_name:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            kwargs["api_key"] = gemini_key

    try:
        print(f"[REVIEWER] Calling {model_name}...")
        response = await acompletion(**kwargs)
        content = response.choices[0].message.content
        print(f"[REVIEWER] {model_name} responded ({len(content)} chars)")

        # Clean markdown code blocks if present
        if "```json" in content:
            start = content.index("```json") + 7
            end = content.rindex("```")
            content = content[start:end].strip()
        elif "```" in content:
            start = content.index("```") + 3
            end = content.rindex("```")
            content = content[start:end].strip()

        return LLMSuggestion.model_validate_json(content)

    except Exception as e:
        print(f"[REVIEWER ERROR] {model_name}: {type(e).__name__}: {e}")
        logger.error(f"Error running review on {model_name}: {e}")
        return None
