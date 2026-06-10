import os
from tools import fs, web, sys, media, dev, utils, macos

_system_md = os.path.join(os.path.dirname(__file__), "system.md")
if os.path.exists(_system_md):
    with open(_system_md, "r", encoding="utf-8") as _f:
        system_instruction = _f.read().strip()
else:
    system_instruction = "You are a helpful assistant with access to tools."

# Aggregate all tools
tools = (
    fs.tools + 
    web.tools + 
    sys.tools + 
    media.tools + 
    dev.tools + 
    utils.tools +
    macos.tools
)

# Predefined tool sets
tool_sets = {
    "fs": fs.tools,
    "web": web.tools,
    "sys": [sys.get_current_time, sys.clipboard_read, sys.clipboard_write],
    "media": media.tools,
    "dev": dev.tools,
    "utils": utils.tools,
    "mac": macos.tools,
    "all": tools,
    "time": [sys.get_current_time],
    "clip": [sys.clipboard_read, sys.clipboard_write],
    "clipboard": [sys.clipboard_read, sys.clipboard_write],
    "exec": [sys.shell_execute, sys.applescript_execute],
    "screen": [macos.screenshot, macos.screenshot_selection, macos.capture_screen_text],
    "browser": [macos.get_active_browser_info],
    "finder": [macos.get_finder_selection],
    "safe": [
        fs.read_file_text,
        fs.list_dir,
        fs.find_files,
        fs.grep_text,
        web.fetch_url,
        sys.get_current_time,
        sys.clipboard_read,
        media.ocr_image,
        media.image_metadata,
        dev.git_status,
        dev.git_diff,
        utils.calculator,
        macos.get_finder_selection,
        macos.spotlight_search,
        macos.get_active_browser_info,
        macos.screenshot,
        macos.screenshot_selection,
        macos.capture_screen_text,
        macos.launchd_list,
        macos.launchd_read,
    ],
    "vision": [media.ocr_image, macos.screenshot, macos.screenshot_selection, macos.capture_screen_text, media.image_metadata, media.media_convert],
    "audio": [media.record_audio, media.media_convert],
}
