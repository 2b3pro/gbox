import subprocess
from .fs import _clean_path

def git_status() -> str:
    """Returns the current git status of the repository."""
    try:
        r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=10)
        return r.stdout if r.stdout else "Clean or not a git repo."
    except Exception as e:
        return f"Error: {e}"

def git_diff(filepath: str = "") -> str:
    """Returns the git diff for a specific file or the whole repo if filepath is empty."""
    cmd = ["git", "diff"]
    if filepath:
        cmd.append(_clean_path(filepath))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return r.stdout[:10000] if r.stdout else "No diff."
    except Exception as e:
        return f"Error: {e}"

tools = [git_status, git_diff]
