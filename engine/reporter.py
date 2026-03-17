from typing import List, Dict, Any

def generate_markdown_report(
    task_id: str,
    prompt: str,
    model_results: List[Dict[str, Any]]
) -> str:
    """
    Generates a markdown report comparing suggestions from multiple AI models.
    """
    md = f"# AI Code Improvement Report (Task: {task_id})\n\n"

    md += "## Request\n"
    md += f"**Prompt:** {prompt}\n\n"
    md += "---\n\n"

    if not model_results:
        md += "## Status\n"
        md += "No models successfully produced a result. Please check API keys in your `.env` file.\n"
        return md

    for result in model_results:
        model = result.get("model_name", "Unknown")
        explanation = result.get("explanation", "No explanation provided.")
        diff_text = result.get("diff_text", "")
            
        # Normal markdown, we will style MarkdownH2 in cli.py CSS
        md += f"## {model.upper()} MODEL\n\n"
        md += f"**Explanation:** {explanation}\n\n"

        md += "### Full Diff\n"
        if diff_text.strip():
            md += f"```diff\n{diff_text}\n```\n\n"
        else:
            md += "*No changes detected.*\n\n"
        
        md += "---\n\n"

    return md
