import json
import logging
import os
import re
from typing import Optional, List
from litellm import acompletion
from core.config import settings

logger = logging.getLogger("llm_consensus_engine.reviewers")

async def run_llm_review(model_name: str, worktree_path: str, target_files: List[str], prompt: str) -> Optional[str]:
    """
    Sends file contents from the worktree to an LLM, parses the edited files, 
    and writes them back to the worktree. Returns the explanation.
    """
    
    # 1. Read files
    files_context = ""
    for file_path in target_files:
        full_path = os.path.join(worktree_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            files_context += f"--- {file_path} ---\n{content}\n\n"
        else:
            files_context += f"--- {file_path} ---\n(File does not exist yet)\n\n"

    system_prompt = (
        "You are an expert software engineer acting as an autonomous agent. "
        "The user will provide you with the contents of several files and an instruction. "
        "You must improve or modify the code according to the instruction.\n\n"
        "OUTPUT FORMAT REQUIRED:\n"
        "For each file you modify, output the FULL new content wrapped in XML tags like this:\n"
        "```xml\n"
        '<file path="exact/path/from/input.py">\n'
        "// FULL NEW CODE HERE\n"
        "</file>\n"
        "```\n"
        "Do NOT output partial diffs. Output the entire file content.\n"
        "Outside the XML tags, you can write a brief explanation of what you changed."
    )

    user_prompt = f"Instruction: {prompt}\n\nFiles:\n{files_context}"

    # Build kwargs
    kwargs = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "timeout": 120
    }

    # Pass API key explicitly for Gemini
    if "gemini" in model_name:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            kwargs["api_key"] = gemini_key

    try:
        print(f"[REVIEWER] Calling {model_name}...")
        response = await acompletion(**kwargs)
        content = response.choices[0].message.content
        print(f"[REVIEWER] {model_name} responded ({len(content)} chars)")

        # 2. Parse the files and write them back
        file_pattern = re.compile(r'<file path="(.*?)">\n?(.*?)\n?</file>', re.DOTALL)
        matches = file_pattern.findall(content)
        
        files_modified = 0
        for path_attr, new_content in matches:
            # Security / sanity check: don't allow absolute paths or escaping worktree
            clean_path = path_attr.strip()
            if ".." in clean_path or clean_path.startswith("/"):
                logger.warning(f"Model {model_name} tried to write to {clean_path}, ignoring.")
                continue
                
            write_path = os.path.join(worktree_path, clean_path)
            os.makedirs(os.path.dirname(write_path), exist_ok=True)
            
            with open(write_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            files_modified += 1
            
        # Clean up the explanation by removing the XML blocks
        explanation = re.sub(r'<file path=".*?">.*?</file>', '', content, flags=re.DOTALL)
        explanation = re.sub(r'```xml\s*```', '', explanation).strip()
        
        if not explanation:
            explanation = f"Modified {files_modified} files."

        return explanation

    except Exception as e:
        print(f"[REVIEWER ERROR] {model_name}: {type(e).__name__}: {e}")
        logger.error(f"Error running review on {model_name}: {e}")
        return None
