from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- API Input ---
class SubmissionRequest(BaseModel):
    code: str = Field(..., description="The user's source code to be improved.")
    prompt: str = Field(..., description="Instructions for what to improve or change.")

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
