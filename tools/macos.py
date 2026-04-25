import subprocess
import os
import datetime
import tempfile
from .fs import _clean_path
from .media import ocr_image

def run_shortcut(name: str, input_text: str = "") -> str:
    """Runs a macOS Shortcut by name.
    
    Args:
        name: The exact name of the shortcut in the Shortcuts app.
        input_text: Optional text to pass as input to the shortcut.
    """
    cmd = ["shortcuts", "run", name]
    if input_text:
        cmd.extend(["--input-text", input_text])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.stdout if r.stdout else "Shortcut executed successfully."
    except Exception as e:
        return f"Error: {e}"

def get_finder_selection() -> str:
    """Returns the POSIX paths of all files currently selected in Finder."""
    script = '''
    tell application "Finder"
        set theSelection to selection
        if theSelection is {} then return "No files selected."
        set out to ""
        repeat with i from 1 to count of theSelection
            set out to out & POSIX path of (item i of theSelection as text) & "\n"
        end repeat
        return out
    end tell
    '''
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def spotlight_search(query: str) -> str:
    """Uses macOS Spotlight (mdfind) to find files matching a query.
    
    Args:
        query: The search query (e.g., "kind:pdf LiteRT").
    """
    try:
        r = subprocess.run(["mdfind", query], capture_output=True, text=True, timeout=20)
        output = r.stdout.strip()
        if not output:
            return "No matches found."
        lines = output.split("\n")
        res = "\n".join(lines[:50])
        if len(lines) > 50:
            res += f"\n... ({len(lines) - 50} more matches)"
        return res
    except Exception as e:
        return f"Error: {e}"

def speak_text(text: str) -> str:
    """Makes the Mac speak the provided text using the system voice.
    
    Args:
        text: The text to be spoken aloud.
    """
    try:
        subprocess.Popen(["say", text])
        return "Speaking aloud..."
    except Exception as e:
        return f"Error: {e}"

def get_active_browser_info() -> str:
    """Returns the URL and Title of the active tab in Safari or Google Chrome."""
    script = '''
    if application "Safari" is running then
        tell application "Safari"
            if (count of windows) > 0 then
                set theUrl to URL of front document
                set theTitle to name of front document
                return "Safari: " & theTitle & " (" & theUrl & ")"
            end if
        end tell
    end if
    if application "Google Chrome" is running then
        tell application "Google Chrome"
            if (count of windows) > 0 then
                set theUrl to URL of active tab of front window
                set theTitle to title of active tab of front window
                return "Chrome: " & theTitle & " (" & theUrl & ")"
            end if
        end tell
    end if
    return "No active browser window found."
    '''
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def set_system_appearance(mode: str) -> str:
    """Sets macOS system appearance to Dark or Light mode.
    
    Args:
        mode: 'dark' or 'light'.
    """
    is_dark = "true" if mode.lower() == "dark" else "false"
    script = f'''
    tell application "System Events"
        tell appearance preferences
            set dark mode to {is_dark}
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        return f"System set to {mode} mode."
    except Exception as e:
        return f"Error: {e}"

def screenshot(filepath: str = "") -> str:
    """Captures the screen to a PNG. If filepath is empty, writes to /tmp with timestamp.

    Returns the saved path. Pair with `ocr_image` to extract on-screen text.
    """
    if filepath:
        path = os.path.expanduser(_clean_path(filepath))
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = f"/tmp/screenshot-{ts}.png"
    try:
        r = subprocess.run(["screencapture", "-x", path], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return f"Error: screencapture failed: {r.stderr.strip()}"
        return path
    except Exception as e:
        return f"Error: {e}"

def screenshot_selection() -> str:
    """Allows the user to interactively select a portion of the screen with a crosshair.
    
    Returns the path to the captured selection image.
    """
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = f"/tmp/selection-{ts}.png"
    try:
        # -i triggers interactive mode
        r = subprocess.run(["screencapture", "-i", path], capture_output=True, text=True, timeout=30)
        if not os.path.exists(path):
            return "Selection cancelled or failed."
        return path
    except Exception as e:
        return f"Error: {e}"

def capture_screen_text() -> str:
    """Captures the entire screen and extracts all text using OCR.
    
    Returns the recognized text on the screen.
    """
    path = screenshot()
    if path.startswith("Error:"):
        return path
    try:
        text = ocr_image(path)
        # Cleanup temp file
        if "/tmp/screenshot-" in path:
            os.remove(path)
        return text
    except Exception as e:
        return f"Error running OCR on screen: {e}"

def launchd_list() -> str:
    """Lists all user Launch Agents (~/Library/LaunchAgents)."""
    path = os.path.expanduser("~/Library/LaunchAgents")
    if not os.path.exists(path):
        return "No user LaunchAgents directory found."
    try:
        files = [f for f in os.listdir(path) if f.endswith(".plist")]
        return "\n".join(files) if files else "No custom plists found."
    except Exception as e:
        return f"Error: {e}"

def launchd_read(label: str) -> str:
    """Reads the content of a launchd plist file by its label or filename.
    
    Args:
        label: The label of the job (e.g., 'com.user.task') or the filename.
    """
    if not label.endswith(".plist"):
        label += ".plist"
    path = os.path.expanduser(f"~/Library/LaunchAgents/{label}")
    if not os.path.exists(path):
        return f"Error: Job file not found: {path}"
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def launchd_create(label: str, program_arguments: list[str], run_at_load: bool = True, start_interval: int = 0) -> str:
    """Creates and loads a new launchd agent.
    
    Args:
        label: Unique identifier for the job (e.g., 'com.me.daily_backup').
        program_arguments: List of command and arguments to run.
        run_at_load: Whether to run the job immediately when loaded.
        start_interval: Frequency in seconds (0 to disable).
    """
    import plistlib
    path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    
    plist_data = {
        "Label": label,
        "ProgramArguments": program_arguments,
        "RunAtLoad": run_at_load,
    }
    if start_interval > 0:
        plist_data["StartInterval"] = start_interval

    try:
        with open(path, "wb") as f:
            plistlib.dump(plist_data, f)
        
        # Load the new job
        subprocess.run(["launchctl", "load", path], check=True)
        return f"Job '{label}' created and loaded at {path}"
    except Exception as e:
        return f"Error: {e}"

def launchd_delete(label: str) -> str:
    """Unloads and deletes a launchd agent.
    
    Args:
        label: The label of the job.
    """
    if not label.endswith(".plist"):
        filename = label + ".plist"
    else:
        filename = label
        label = label.replace(".plist", "")

    path = os.path.expanduser(f"~/Library/LaunchAgents/{filename}")
    try:
        # Unload first
        subprocess.run(["launchctl", "unload", path], capture_output=True)
        if os.path.exists(path):
            os.remove(path)
            return f"Job '{label}' deleted."
        return f"Job '{label}' was not found on disk, but unload was attempted."
    except Exception as e:
        return f"Error: {e}"

def launchd_service_control(label: str, action: str) -> str:
    """Controls a launchd service (start, stop, load, unload).
    
    Args:
        label: The label of the job.
        action: 'start', 'stop', 'load', or 'unload'.
    """
    path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    try:
        if action in ("load", "unload"):
            subprocess.run(["launchctl", action, path], check=True)
        else:
            # start/stop use the label
            subprocess.run(["launchctl", action, label], check=True)
        return f"Action '{action}' performed on '{label}'."
    except Exception as e:
        return f"Error: {e}"

tools = [
    run_shortcut, 
    get_finder_selection, 
    spotlight_search, 
    speak_text, 
    get_active_browser_info, 
    set_system_appearance,
    screenshot,
    screenshot_selection,
    capture_screen_text,
    launchd_list,
    launchd_read,
    launchd_create,
    launchd_delete,
    launchd_service_control
]
