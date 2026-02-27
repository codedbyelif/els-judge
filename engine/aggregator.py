from typing import Dict, Any
from schemas.api import LLMReviewOutput

def calculate_consensus(reviews: Dict[str, LLMReviewOutput]) -> Dict[str, Any]:
    """
    Analyzes multiple LLM reviews to calculate a final consensus risk score,
    detect disagreements, and pool identified issues.
    """
    if not reviews:
        return {
            "aggregated_risk_score": 0.0,
            "severity_level": "None",
            "disagreement_rate": 0.0,
            "consensus_issues": []
        }
        
    scores = [r.overall_risk_score for r in reviews.values() if r is not None]
    if not scores:
         return {
            "aggregated_risk_score": 0.0,
            "severity_level": "None",
            "disagreement_rate": 0.0,
            "consensus_issues": []
        }
        
    avg_score = sum(scores) / len(scores)
    
    # Simple disagreement rate based on max difference in scores among models
    max_diff = max(scores) - min(scores)
    # Normalize disagreement to a 0-1 scale (since scores range 0-10)
    disagreement_rate = min(max_diff / 10.0, 1.0)
    
    if avg_score >= 8: severity = "Critical"
    elif avg_score >= 5: severity = "High"
    elif avg_score >= 3: severity = "Medium"
    else: severity = "Low"
    
    # Aggregate and group issues
    all_issues = []
    for model, rev in reviews.items():
        if rev and rev.issues:
            for issue in rev.issues:
                issue_dict = issue.model_dump()
                issue_dict["found_by"] = model
                all_issues.append(issue_dict)
                
    # In a full production system, we could group similar issues by semantic similarity.
    # Here we return a pooled list.
    
    return {
        "aggregated_risk_score": round(avg_score, 2),
        "severity_level": severity,
        "disagreement_rate": round(disagreement_rate, 2),
        "consensus_issues": all_issues
    }
