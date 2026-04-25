import os
import re
import subprocess
import glob as _glob

def _clean_path(filepath: str) -> str:
    """Strip tokenizer artifacts (<|"|>, <|...|>) and surrounding quotes from a path."""
    s = filepath.strip()
    s = re.sub(r'<\|[^|]*\|>', '', s)
    s = s.strip().strip('\'"`')
    return s

def read_file_text(filepath: str) -> str:
    """Reads a file and returns its text content.

    Supports plain text (.txt, .md) read directly, and PDFs via `pdftotext`.
    Returns an error string prefixed with "Error:" on failure.
    """
    path = os.path.expanduser(_clean_path(filepath))
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"

    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", path, "-"],
                capture_output=True, text=True, timeout=120,
            )
        except FileNotFoundError:
            return "Error: pdftotext not installed (brew install poppler)"
        except subprocess.TimeoutExpired:
            return "Error: pdftotext timed out"
        if result.returncode != 0:
            return f"Error: pdftotext failed: {result.stderr.strip()}"
        return result.stdout

    if ext in (".txt", ".md", ".markdown", ".rst", ".log", ".csv", ".json", ".yaml", ".yml", ""):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError as e:
            return f"Error: {e}"

    return f"Error: unsupported extension '{ext}'"

def list_dir(path: str = ".") -> str:
    """Lists entries in a directory. Directories get a trailing '/'. Max 500 entries."""
    p = os.path.expanduser(_clean_path(path))
    if not os.path.isdir(p):
        return f"Error: not a directory: {p}"
    try:
        entries = sorted(os.listdir(p))
    except OSError as e:
        return f"Error: {e}"
    lines = []
    for name in entries[:500]:
        full = os.path.join(p, name)
        lines.append(name + ("/" if os.path.isdir(full) else ""))
    suffix = f"\n... ({len(entries) - 500} more)" if len(entries) > 500 else ""
    return "\n".join(lines) + suffix

def find_files(pattern: str, root: str = ".") -> str:
    """Finds files matching a glob pattern under `root` (recursive via '**'). Max 200 hits."""
    r = os.path.expanduser(_clean_path(root))
    if not os.path.isdir(r):
        return f"Error: root not a directory: {r}"
    pat = os.path.join(r, pattern)
    try:
        hits = _glob.glob(pat, recursive=True)
    except OSError as e:
        return f"Error: {e}"
    if not hits:
        return f"(no matches for {pattern} under {r})"
    truncated = hits[:200]
    suffix = f"\n... ({len(hits) - 200} more)" if len(hits) > 200 else ""
    return "\n".join(truncated) + suffix

def write_file(filepath: str, content: str) -> str:
    """Writes `content` to `filepath` (UTF-8, overwrites). Returns bytes written or error."""
    path = os.path.expanduser(_clean_path(filepath))
    parent = os.path.dirname(path) or "."
    if not os.path.isdir(parent):
        return f"Error: parent directory does not exist: {parent}"
    try:
        with open(path, "w", encoding="utf-8") as f:
            n = f.write(content)
    except OSError as e:
        return f"Error: {e}"
    return f"Wrote {n} chars to {path}"

def grep_text(pattern: str, filepath: str, max_matches: int = 100) -> str:
    """Searches `filepath` for regex `pattern`, returning matching lines with line numbers."""
    path = os.path.expanduser(_clean_path(filepath))
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return f"Error: bad regex: {e}"
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if rx.search(line):
                    out.append(f"{i}: {line.rstrip()}")
                    if len(out) >= max_matches:
                        out.append(f"... (stopped at {max_matches})")
                        break
    except OSError as e:
        return f"Error: {e}"
    return "\n".join(out) if out else "(no matches)"

tools = [read_file_text, list_dir, find_files, write_file, grep_text]
