from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- API Input --- 
class SubmissionRequest(BaseModel):
    original_code: str = Field(..., description="The original source code snippet.")
    suggested_code: str = Field(..., description="The LLM-generated or suggested updated code.")

# --- LLM Review Outputs --- 
class ChangeIssue(BaseModel):
    category: Literal["security", "logic", "performance", "style", "functional"]
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    line_number: Optional[int] = None

class LLMReviewOutput(BaseModel):
    issues: List[ChangeIssue]
    overall_risk_score: float = Field(..., ge=0, le=10, description="Risk score from 0 (safe) to 10 (critical).")
    summary: str = Field(..., description="Brief summary of the review.")

# --- API Response ---
class FinalVerdictResponse(BaseModel):
    submission_id: int
    aggregated_risk_score: float
    severity_level: str
    disagreement_rate: float
    markdown_report: str
