import asyncio
from typing import Dict, Any
from core.config import settings
from engine.reviewers import run_llm_review
from engine.diff_analyzer import analyze_diff
from engine.aggregator import calculate_consensus
from engine.reporter import generate_markdown_report

async def process_submission(original_code: str, suggested_code: str) -> Dict[str, Any]:
    """
    Main orchestration function.
    Runs diff analysis, dispatches concurrent LLM reviews, aggregates them, and generates a report.
    """
    models = [settings.primary_model, settings.secondary_model, settings.tertiary_model]
    
    # 1. Diff Analysis (synchronous)
    diff_stats = analyze_diff(original_code, suggested_code)
    
    # 2. Run LLM reviews concurrently
    tasks = [run_llm_review(m, original_code, suggested_code) for m in models]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    valid_reviews = {}
    for model, res in zip(models, results):
        if isinstance(res, Exception):
            # Log exception and skip
            print(f"Model {model} failed with exception: {res}")
        elif res is not None:
             valid_reviews[model] = res
             
    # 3. Aggregate data
    consensus = calculate_consensus(valid_reviews)
    
    # 4. Generate report
    report = generate_markdown_report(consensus, diff_stats)
    
    return {
        "diffs": diff_stats,
        "reviews": valid_reviews,  # These are currently LLMReviewOutput pydantic objects
        "consensus": consensus,
        "report": report
    }
