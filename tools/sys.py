import os
import datetime
import subprocess
from .fs import _clean_path

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clipboard_read() -> str:
    """Returns the current macOS clipboard text via pbpaste."""
    try:
        r = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
    except FileNotFoundError:
        return "Error: pbpaste not available (macOS only)"
    return r.stdout

def clipboard_write(text: str) -> str:
    """Writes `text` to the macOS clipboard via pbcopy."""
    try:
        r = subprocess.run(["pbcopy"], input=text, text=True, timeout=5)
    except FileNotFoundError:
        return "Error: pbcopy not available (macOS only)"
    return "ok" if r.returncode == 0 else f"Error: pbcopy exit {r.returncode}"

def shell_execute(command: str) -> str:
    """Executes a shell command and returns output. USE WITH CAUTION."""
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        out = r.stdout + r.stderr
        return out if out else f"(Exit code: {r.returncode})"
    except Exception as e:
        return f"Error: {e}"

def applescript_execute(script: str, language: str = "AppleScript") -> str:
    """Executes AppleScript or JXA (Javascript for Automation).
    
    Args:
        script: The script code.
        language: 'AppleScript' or 'JavaScript'.
    """
    cmd = ["osascript"]
    if language.lower() in ("javascript", "jxa"):
        cmd.extend(["-l", "JavaScript"])
    
    try:
        r = subprocess.run(cmd, input=script, text=True, capture_output=True, timeout=20)
        return r.stdout if r.stdout else r.stderr
    except Exception as e:
        return f"Error: {e}"

tools = [get_current_time, clipboard_read, clipboard_write, shell_execute, applescript_execute]
