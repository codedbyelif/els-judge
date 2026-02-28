from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.domain import Submission, ModelSuggestion
from schemas.api import SubmissionRequest, FinalVerdictResponse, ModelResult, CodeChange
from engine.dispatcher import process_submission
import logging

logger = logging.getLogger("llm_consensus_engine.api")
router = APIRouter()

@router.post("/submit-code", response_model=FinalVerdictResponse)
async def submit_code(request: SubmissionRequest, db: Session = Depends(get_db)):
    """
    Submits user's code and prompt to the AI improvement pipeline.
    Sends to multiple LLMs, collects improved versions, and returns comparison.
    """
    # 1. Create Submission Record
    submission = Submission(
        code=request.code,
        prompt=request.prompt
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    try:
        # 2. Run Pipeline
        results = await process_submission(request.code, request.prompt)

        # 3. Store per-model suggestions
        for mr in results.get("model_results", []):
            suggestion = mr["suggestion"]
            db_suggestion = ModelSuggestion(
                submission_id=submission.id,
                model_name=mr["model_name"],
                improved_code=suggestion.improved_code,
                explanation=suggestion.explanation,
                changes=[c.model_dump() for c in suggestion.changes],
                diff_text=mr["diff_text"]
            )
            db.add(db_suggestion)

        db.commit()

        # 4. Build response
        model_results = []
        for mr in results.get("model_results", []):
            suggestion = mr["suggestion"]
            model_results.append(ModelResult(
                model_name=mr["model_name"],
                improved_code=suggestion.improved_code,
                explanation=suggestion.explanation,
                changes=suggestion.changes,
                diff_text=mr["diff_text"]
            ))

        return FinalVerdictResponse(
            submission_id=submission.id,
            model_results=model_results,
            common_changes=results.get("common_changes", ""),
            markdown_report=results.get("report", "")
        )

    except Exception as e:
        logger.error(f"Pipeline error for submission {submission.id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
