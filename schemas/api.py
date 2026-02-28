from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# --- API Input ---
class SubmissionRequest(BaseModel):
    code: str = Field(..., description="The user's source code to be improved.", min_length=1)
    prompt: str = Field(..., description="Instructions for what to improve or change.", min_length=1, max_length=2000)

    @field_validator("code")
    def code_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Code must not be empty or whitespace only.")
        return v

    @field_validator("prompt")
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Prompt must not be empty or whitespace only.")
        return v

# --- LLM Suggestion Output ---
class CodeChange(BaseModel):
    line_range: str = Field(..., description="e.g. 'Line 3-5' or 'Line 7'")
    original: str = Field(..., description="The original code snippet that was changed.")
    improved: str = Field(..., description="The improved version of that snippet.")
    reason: str = Field(..., description="Why this change was made.")

class LLMSuggestion(BaseModel):
    improved_code: str = Field(..., description="The full improved version of the code.")
    explanation: str = Field(..., description="Brief summary of what was changed and why.")
    changes: List[CodeChange] = Field(default_factory=list, description="List of specific changes made.")

# --- API Response ---
class ModelResult(BaseModel):
    model_name: str
    improved_code: str
    explanation: str
    changes: List[CodeChange]
    diff_text: str

class FinalVerdictResponse(BaseModel):
    submission_id: int
    model_results: List[ModelResult]
    common_changes: str
    markdown_report: str
