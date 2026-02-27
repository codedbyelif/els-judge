import difflib

def generate_unified_diff(original: str, suggested: str) -> list[str]:
    """Generates a list of unified diff strings using Python's difflib."""
    return list(difflib.unified_diff(
        original.splitlines(),
        suggested.splitlines(),
        fromfile='original',
        tofile='suggested',
        n=3,
        lineterm=''
    ))

def analyze_diff(original_code: str, suggested_code: str) -> list[dict]:
    """
    Analyzes the diff and chunks it into simplified node structures or statistics.
    For this implementation, we return basic diff text parts.
    """
    raw_diff = generate_unified_diff(original_code, suggested_code)
    
    # We can store the full text diff or parse chunks.
    # Here we just return a simplified unified view in one piece.
    diff_text = "\n".join(raw_diff)
    
    return [{"change_type": "unified", "original_chunk": None, "suggested_chunk": diff_text}]
