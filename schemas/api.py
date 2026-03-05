import uuid
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# --- API Input ---
class SubmissionRequest(BaseModel):
    target_files: List[str] = Field(..., description="List of file paths to modify (relative to working directory).", min_items=1)
    prompt: str = Field(..., description="Instructions for what to improve or change.", min_length=1)

    @field_validator("prompt")
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Prompt must not be empty or whitespace only.")
        return v

# --- API Response ---
class ModelResult(BaseModel):
    model_name: str
    branch_name: str
    explanation: str
    diff_text: str

class FinalVerdictResponse(BaseModel):
    task_id: str
    model_results: List[ModelResult]
    markdown_report: str
