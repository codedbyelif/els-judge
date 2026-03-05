import os
import subprocess
import shutil
import uuid
from typing import List, Optional

# We will use /tmp or a dedicated hidden folder for worktrees
WORKTREE_BASE_DIR = os.path.join(os.getcwd(), ".ai_worktrees")

def _run_git_command(args: List[str], cwd: str = None) -> str:
    """Run a git command and return its output."""
    if cwd is None:
        cwd = os.getcwd()
    
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {' '.join(args)}")
        print(f"Error output: {e.stderr}")
        raise

def ensure_base_branch(base_branch_name: str = "main"):
    """Ensure we are on a clean state or at least know our base branch."""
    # In a real tool, we might want to stash or warn on dirty working tree.
    pass

def setup_worktree_dir():
    """Ensure the base directory for worktrees exists."""
    if not os.path.exists(WORKTREE_BASE_DIR):
        os.makedirs(WORKTREE_BASE_DIR, exist_ok=True)
        # Add to gitignore if not there
        gitignore_path = os.path.join(os.getcwd(), ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                content = f.read()
            if ".ai_worktrees" not in content:
                with open(gitignore_path, "a") as f:
                    f.write("\n# AI Code Judge Worktrees\n.ai_worktrees/\n")

def create_task_branch(task_id: str, base_branch: str = "main") -> str:
    """Create a base branch for the entire task."""
    task_branch = f"task-{task_id}"
    # Create the branch based on the current HEAD or a specific base
    # For simplicity, we just branch off the current HEAD
    _run_git_command(["branch", task_branch])
    return task_branch

def create_model_worktree(task_id: str, model_name: str) -> dict:
    """
    Create a git worktree for a specific model to work in isolation.
    Returns the path to the worktree and the name of the branch.
    """
    setup_worktree_dir()
    
    # Clean up model name for branch branch
    clean_model_name = model_name.replace("/", "-").replace(":", "-")
    branch_name = f"task-{task_id}-{clean_model_name}"
    
    worktree_path = os.path.abspath(os.path.join(WORKTREE_BASE_DIR, branch_name))
    
    # Create the branch pointing to the current HEAD
    _run_git_command(["branch", branch_name])
    
    # Add the worktree
    _run_git_command(["worktree", "add", worktree_path, branch_name])
    
    return {
        "branch_name": branch_name,
        "worktree_path": worktree_path
    }

def commit_worktree_changes(worktree_path: str, commit_message: str):
    """Stage and commit all changes in the given worktree."""
    _run_git_command(["add", "."], cwd=worktree_path)
    
    # Only commit if there are changes
    try:
        _run_git_command(["commit", "-m", commit_message], cwd=worktree_path)
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stderr or "nothing to commit" in e.stdout:
            print(f"No changes made in {worktree_path}")
        else:
            raise

def get_branch_diff(base_branch: str, target_branch: str) -> str:
    """Get the diff between the base branch and the target model branch."""
    # We do this from the main repository
    return _run_git_command(["diff", f"{base_branch}..{target_branch}"])

def merge_model_branch(target_branch: str, base_branch: str = "main"):
    """Merge the selected model's branch back into the base directory/branch."""
    _run_git_command(["checkout", base_branch])
    _run_git_command(["merge", "--squash", target_branch])
    _run_git_command(["commit", "-m", f"Merged AI solution from {target_branch}"])

def cleanup_task_worktrees(task_id: str):
    """Remove all worktrees associated with a task_id."""
    # List all worktrees
    output = _run_git_command(["worktree", "list"])
    lines = output.split('\n')
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        wt_path = parts[0]
        
        # If this worktree belongs to our task
        if f"task-{task_id}" in wt_path and WORKTREE_BASE_DIR in wt_path:
            print(f"Removing worktree {wt_path}")
            _run_git_command(["worktree", "remove", "-f", wt_path])
            
            # Extract branch name and optionally delete it if we want full cleanup
            # We'll keep the branches for now so the user can inspect them if needed
            # branch_name = parts[2].strip("[]")
            # _run_git_command(["branch", "-D", branch_name])
