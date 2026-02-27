import json
import logging
from typing import Optional
from litellm import acompletion
from schemas.api import LLMReviewOutput
from core.config import settings

logger = logging.getLogger("llm_consensus_engine.reviewers")

# Define the expected JSON format strictly
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["security", "logic", "performance", "style", "functional"]},
                    "description": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "line_number": {"type": ["integer", "null"]}
                },
                "required": ["category", "description", "severity"]
            }
        },
        "overall_risk_score": {"type": "number"},
        "summary": {"type": "string"}
    },
    "required": ["issues", "overall_risk_score", "summary"]
}

async def run_llm_review(model_name: str, original_code: str, suggested_code: str) -> Optional[LLMReviewOutput]:
    """
    Sends the code to a specific LLM model and requests a structured JSON response.
    """
    system_prompt = (
        "You are an expert software engineer reviewing code changes. "
        "Analyze the provided Original and Suggested code for security, logic, performance, stylisitc, and functional changes. "
        "You MUST return your analysis strictly as a JSON object matching this schema: "
        f"{json.dumps(JSON_SCHEMA)}"
    )
    
    user_prompt = f"Original Code:\n```\n{original_code}\n```\n\nSuggested Code:\n```\n{suggested_code}\n```"
    
    try:
        response = await acompletion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if "gpt" in model_name or "claude" in model_name else None,
            timeout=30
        )
        
        # Extract response text
        content = response.choices[0].message.content
        
        # Clean markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        # Parse and validate with Pydantic
        return LLMReviewOutput.model_validate_json(content)
        
    except Exception as e:
        logger.error(f"Error running review on {model_name}: {e}")
        return None
