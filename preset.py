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
    "sys": sys.tools,
    "media": media.tools,
    "dev": dev.tools,
    "utils": utils.tools,
    "mac": macos.tools,
    "all": tools,
    "vision": [media.ocr_image, macos.screenshot, macos.screenshot_selection, macos.capture_screen_text, media.image_metadata, media.media_convert],
    "audio": [media.record_audio, media.media_convert],
}
