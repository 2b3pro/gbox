import os
import datetime
import subprocess
from .fs import _clean_path

def ocr_image(filepath: str) -> str:
    """Extracts text from an image or PDF file using Apple Vision via `ocr-file`.

    Works on images (png/jpg/heic/tiff/...) and PDFs. Returns the recognized text,
    or an error string prefixed with "Error:" on failure.
    """
    path = os.path.expanduser(_clean_path(filepath))
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    try:
        result = subprocess.run(
            ["ocr-file", path],
            capture_output=True, text=True, timeout=300,
        )
    except FileNotFoundError:
        return "Error: ocr-file not installed at /usr/local/bin/ocr-file"
    except subprocess.TimeoutExpired:
        return "Error: ocr-file timed out"
    if result.returncode != 0:
        return f"Error: ocr-file failed: {result.stderr.strip()}"
    return result.stdout

def record_audio(seconds: int = 5, output_path: str = "") -> str:
    """Records audio from the microphone to a file. Requires `sox` or `ffmpeg`.
    
    Returns the path to the recorded file.
    """
    if not output_path:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = f"/tmp/record-{ts}.wav"
    else:
        output_path = os.path.expanduser(_clean_path(output_path))
        
    try:
        if os.path.exists("/opt/homebrew/bin/sox") or os.path.exists("/usr/local/bin/sox"):
            subprocess.run(["sox", "-d", output_path, "trim", "0", str(seconds)], timeout=seconds+5)
        else:
            subprocess.run(["ffmpeg", "-f", "avfoundation", "-i", ":0", "-t", str(seconds), output_path, "-y"], timeout=seconds+5)
        return output_path
    except Exception as e:
        return f"Error recording: {e}"

def media_convert(input_path: str, output_path: str, options: str = "") -> str:
    """Converts media files using sips (images), ffmpeg (video/audio), or magick.
    
    Args:
        input_path: Path to source file.
        output_path: Path to destination.
        options: Extra CLI flags for the converter.
    """
    inp = os.path.expanduser(_clean_path(input_path))
    out = os.path.expanduser(_clean_path(output_path))
    ext = os.path.splitext(inp)[1].lower()
    
    try:
        if ext in (".png", ".jpg", ".jpeg", ".heic", ".tiff", ".webp"):
            if "resize" in options or "format" in options:
                subprocess.run(["sips"] + options.split() + [inp, "--out", out], check=True)
            else:
                subprocess.run(["magick", inp] + options.split() + [out], check=True)
        else:
            subprocess.run(["ffmpeg", "-i", inp] + options.split() + [out, "-y"], check=True)
        return f"Converted to {out}"
    except Exception as e:
        return f"Error: {e}"

def image_metadata(filepath: str) -> str:
    """Extracts detailed metadata (EXIF, etc.) using `exiftool` or `sips`.
    
    Args:
        filepath: Path to the image file.
    """
    path = os.path.expanduser(_clean_path(filepath))
    try:
        if os.path.exists("/opt/homebrew/bin/exiftool"):
            r = subprocess.run(["exiftool", path], capture_output=True, text=True, timeout=10)
        else:
            r = subprocess.run(["sips", "-g", "all", path], capture_output=True, text=True, timeout=10)
        return r.stdout
    except Exception as e:
        return f"Error: {e}"

tools = [ocr_image, record_audio, media_convert, image_metadata]
