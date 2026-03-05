import asyncio
import uuid
import os
from typing import Dict, Any, List
from core.config import settings
from engine.reviewers import run_llm_review
from engine.reporter import generate_markdown_report
from core.git_manager import (
    create_task_branch, 
    create_model_worktree, 
    commit_worktree_changes, 
    get_branch_diff, 
    cleanup_task_worktrees
)

async def _run_model_in_worktree(model_name: str, task_id: str, target_files: List[str], prompt: str) -> Dict[str, Any]:
    # 1. Create a worktree and isolated branch for this model
    wt_info = create_model_worktree(task_id, model_name)
    branch_name = wt_info["branch_name"]
    worktree_path = wt_info["worktree_path"]
    
    # 2. Ask LLM to edit files in that physical directory
    explanation = await run_llm_review(model_name, worktree_path, target_files, prompt)
    
    if not explanation:
        explanation = "Model failed to return a valid response."
        
    # 3. Commit the changes
    commit_worktree_changes(worktree_path, "AI Agent applied solution")
    
    return {
        "model_name": model_name,
        "branch_name": branch_name,
        "worktree_path": worktree_path,
        "explanation": explanation
    }

async def process_submission(target_files: List[str], prompt: str) -> Dict[str, Any]:
    """
    Main orchestration function.
    Creates Git worktrees, runs models in parallel, commits their changes,
    extracts diffs, and returns the models' states for the user to review.
    """
    task_id = str(uuid.uuid4())[:8]
    base_task_branch = create_task_branch(task_id)

    models = [settings.primary_model, settings.secondary_model, settings.tertiary_model]

    # 1. Run models concurrently in their own isolated Git worktrees
    tasks = [
        _run_model_in_worktree(m, task_id, target_files, prompt)
        for m in models
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)

    model_results = []
    for model, res in zip(models, results):
        if isinstance(res, Exception):
            print(f"Model {model} failed with exception: {res}")
        else:
            branch_name = res["branch_name"]
            
            # Since the model committed its changes to its branch, we diff against the base task branch
            diff_text = get_branch_diff(base_task_branch, branch_name)
            
            model_results.append({
                "model_name": res["model_name"],
                "branch_name": branch_name,
                "explanation": res["explanation"],
                "diff_text": diff_text,
            })

    # Optional: cleanup the physical worktree directories to save disk space
    # The branches containing the AI commits will remain in the repo
    cleanup_task_worktrees(task_id)

    # 3. Generate report
    report = generate_markdown_report(task_id, prompt, model_results)

    return {
        "task_id": task_id,
        "model_results": model_results,
        "report": report
    }
