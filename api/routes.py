from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.domain import Submission, Review, DiffNode, FinalVerdict
from schemas.api import SubmissionRequest, FinalVerdictResponse
from engine.dispatcher import process_submission
import logging

logger = logging.getLogger("llm_consensus_engine.api")
router = APIRouter()

@router.post("/submit-code", response_model=FinalVerdictResponse)
async def submit_code(request: SubmissionRequest, db: Session = Depends(get_db)):
    """
    Submits original and suggested code to the consensus pipeline.
    The pipeline runs diff analysis, multiple LLM reviews concurrently,
    aggregates the risk scores, calculates consensus, and stores everything in the DB.
    """
    # 1. Create Submission Record
    submission = Submission(
        original_code=request.original_code, 
        suggested_code=request.suggested_code
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    try:
        # 2. Run Pipeline
        results = await process_submission(request.original_code, request.suggested_code)
        
        # 3. Store Diffs
        for diff in results.get("diffs", []):
            db_diff = DiffNode(
                submission_id=submission.id,
                change_type=diff.get("change_type", "unknown"),
                original_chunk=diff.get("original_chunk"),
                suggested_chunk=diff.get("suggested_chunk")
            )
            db.add(db_diff)
            
        # 4. Store Reviews
        for model_name, review_data in results.get("reviews", {}).items():
            db_review = Review(
                submission_id=submission.id,
                model_name=model_name,
                structured_data=review_data.model_dump(),
                risk_score=review_data.overall_risk_score
            )
            db.add(db_review)
            
        # 5. Store Final Verdict
        consensus = results.get("consensus", {})
        db_verdict = FinalVerdict(
            submission_id=submission.id,
            aggregated_risk_score=consensus.get("aggregated_risk_score", 0.0),
            severity_level=consensus.get("severity_level", "Unknown"),
            disagreement_rate=consensus.get("disagreement_rate", 0.0),
            consensus_issues=consensus.get("consensus_issues", []),
            markdown_report=results.get("report", "")
        )
        db.add(db_verdict)
        db.commit()
        db.refresh(db_verdict)
        
        # 6. Return standard response
        return FinalVerdictResponse(
            submission_id=submission.id,
            aggregated_risk_score=db_verdict.aggregated_risk_score,
            severity_level=db_verdict.severity_level,
            disagreement_rate=db_verdict.disagreement_rate,
            markdown_report=db_verdict.markdown_report
        )
        
    except Exception as e:
        logger.error(f"Pipeline error for submission {submission.id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
