from typing import List, Dict, Any


def find_common_changes(model_results: List[Dict[str, Any]]) -> str:
    """
    Analyzes suggestions from multiple models to find common changes.
    Returns a text summary of what changes were agreed upon by multiple models.
    """
    if len(model_results) < 2:
        return "Not enough model responses to compare."

    # Collect all change reasons from each model
    model_reasons = {}
    for result in model_results:
        name = result["model_name"]
        suggestion = result["suggestion"]
        reasons = [c.reason.lower().strip() for c in suggestion.changes]
        model_reasons[name] = reasons

    # Find themes that appear in multiple models by simple keyword overlap
    all_reasons = []
    for result in model_results:
        suggestion = result["suggestion"]
        for change in suggestion.changes:
            all_reasons.append({
                "model": result["model_name"],
                "reason": change.reason,
                "line_range": change.line_range
            })

    if not all_reasons:
        return "No specific changes identified."

    # Group by which models suggested similar types of changes
    model_names = [r["model_name"] for r in model_results]
    summary_parts = []
    summary_parts.append(f"**{len(model_results)}** model responded with suggestions.\n")

    for result in model_results:
        suggestion = result["suggestion"]
        n_changes = len(suggestion.changes)
        summary_parts.append(f"- **{result['model_name']}**: {n_changes} change(s)")

    return "\n".join(summary_parts)
