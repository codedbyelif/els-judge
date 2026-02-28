import difflib


def generate_unified_diff(original: str, suggested: str) -> str:
    """Generates a unified diff string."""
    diff_lines = list(difflib.unified_diff(
        original.splitlines(),
        suggested.splitlines(),
        fromfile='original',
        tofile='improved',
        n=3,
        lineterm=''
    ))
    return "\n".join(diff_lines) if diff_lines else "(No changes)"


def analyze_diff(original_code: str, suggested_code: str) -> str:
    """
    Returns a unified diff text between original and suggested code.
    """
    return generate_unified_diff(original_code, suggested_code)
