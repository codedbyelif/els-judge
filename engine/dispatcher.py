import asyncio
from typing import Dict, Any, List
from core.config import settings
from engine.reviewers import run_llm_review
from engine.diff_analyzer import analyze_diff
from engine.aggregator import find_common_changes
from engine.reporter import generate_markdown_report

async def process_submission(code: str, prompt: str) -> Dict[str, Any]:
    """
    Main orchestration function.
    Sends user's code + prompt to multiple LLMs, collects improved versions,
    runs diff analysis, and generates a comparison report.
    """
    models = [settings.primary_model, settings.secondary_model, settings.tertiary_model]

    # 1. Run LLM reviews concurrently
    tasks = [run_llm_review(m, code, prompt) for m in models]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    model_results = []
    for model, res in zip(models, results):
        if isinstance(res, Exception):
            print(f"Model {model} failed with exception: {res}")
        elif res is not None:
            # Run diff between original and this model's suggestion
            diff_text = analyze_diff(code, res.improved_code)
            model_results.append({
                "model_name": model,
                "suggestion": res,
                "diff_text": diff_text
            })

    # 2. Find common changes across models
    common_changes = find_common_changes(model_results)

    # 3. Generate report
    report = generate_markdown_report(code, prompt, model_results, common_changes)

    return {
        "model_results": model_results,
        "common_changes": common_changes,
        "report": report
    }
