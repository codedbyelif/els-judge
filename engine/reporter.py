from typing import Dict, Any, List

def generate_markdown_report(consensus_data: Dict[str, Any], diff_stats: List[Dict[str, Any]]) -> str:
    """
    Converts the output of the consensus engine into a readable markdown report.
    """
    md = "# AI Consensus Code Review Report\n\n"
    
    md += "## Executive Summary\n"
    md += f"- **Aggregated Risk Score:** `{consensus_data['aggregated_risk_score']} / 10`\n"
    md += f"- **Severity Level:** **{consensus_data['severity_level']}**\n"
    md += f"- **Model Disagreement Rate:** `{consensus_data['disagreement_rate']*100:.1f}%`\n\n"
    
    md += "## Identified Issues\n"
    issues = consensus_data.get("consensus_issues", [])
    if not issues:
        md += "No critical issues identified by any model.\n\n"
    else:
        for idx, issue in enumerate(issues, start=1):
            sev = issue['severity'].upper()
            line = f"Line {issue['line_number']}" if issue.get("line_number") else "General"
            md += f"### {idx}. {issue['category'].title()} ({sev})\n"
            md += f"- **Description:** {issue['description']}\n"
            md += f"- **Location:** {line}\n"
            md += f"- **Detected By:** `{issue['found_by']}`\n\n"
            
    md += "## Diff Statistics\n"
    # Basic summary of diff structure
    for diff in diff_stats:
        md += "```diff\n"
        if diff.get("suggested_chunk"):
            md += diff["suggested_chunk"] + "\n"
        md += "```\n\n"

    return md
