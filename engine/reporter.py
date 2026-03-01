from typing import List, Dict, Any


def generate_markdown_report(
    original_code: str,
    prompt: str,
    model_results: List[Dict[str, Any]],
    common_changes: str
) -> str:
    """
    Generates a markdown report comparing suggestions from multiple AI models.
    """
    md = "# AI Code Improvement Report\n\n"

    md += "## Request\n"
    md += f"**Prompt:** {prompt}\n\n"
    md += "**Original Code:**\n"
    md += f"```\n{original_code}\n```\n\n"

    md += "---\n\n"
    md += "## Summary\n"
    md += f"{common_changes}\n\n"

    md += "---\n\n"

    for result in model_results:
        model = result["model_name"]
        suggestion = result["suggestion"]
        diff_text = result["diff_text"]
            
        # Normal markdown, we will style MarkdownH2 in cli.py CSS
        md += f"## {model.upper()} MODEL\n\n"
        md += f"**Explanation:** {suggestion.explanation}\n\n"

        if suggestion.changes:
            md += "### Changes Made\n\n"
            for i, change in enumerate(suggestion.changes, 1):
                md += f"**{i}. {change.line_range}** — {change.reason}\n\n"
                md += f"Before:\n```python\n{change.original}\n```\n"
                md += f"After:\n```python\n{change.improved}\n```\n\n"

        md += "### Full Diff\n"
        md += f"```diff\n{diff_text}\n```\n\n"

        md += "### Improved Code\n"
        md += f"```python\n{suggestion.improved_code}\n```\n\n"
        
        md += "---\n\n"

    return md
