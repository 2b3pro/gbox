# gbox (gb) - LiteRT-LM Inference Tool

![gbox Banner](assets/banner.png)

A powerful, multimodal CLI wrapper for the LiteRT-LM Python API. This tool allows for quick inference with support for text, images, audio, PDFs, structured JSON output, and modular tool calling.

## Features

- **Multimodal Support**: Seamlessly handle text, images, and **audio** in a single prompt.
- **PDF Intelligence**: Automatically detects piped PDFs, extracting text and rendering the first page for the vision backend.
- **Structured Output**: Enforce strict JSON responses using the `--schema` flag.
- **Real-Time Streaming**: Use the `--stream` flag to see the model's response as it generates.
- **System Instructions**: Inject system-level instructions or named Fabric patterns using the `--system-file` flag.
- **Modular Tooling**: Enable specific tools or predefined tool sets from a modular `tools/` package.
- **Context Awareness**: Inject conversation history via JSONL or raw text context via Markdown using the `--context` flag.
- **Smart Recommendations**: Suggests using the `--high` (4B) model when complex tools (like AppleScript, SQLite, or macOS system automation) are requested.
- **Unix-Friendly**: Designed for piping and shell automation.

## Installation

Ensure you have the `litert_lm` package installed. For full features, install these dependencies:

```bash
# Required for PDF support
uv pip install pymupdf

# Recommended for specific tools
brew install poppler exiftool sox ffmpeg imagemagick
```

## Usage

### Basic Inference
You can provide the prompt via the `--prompt` flag or as a positional argument.

```bash
# Positional (concise)
./gb "What is the capital of France?"

# Using the flag
./gb --prompt "Hi there!"

# Using a file as a prompt
./gb --prompt instructions.txt

# With real-time streaming
./gb --stream "Write a long poem"
```

### Multimodal (Image & Audio)
If no prompt is provided with an image or audio, a default one like "Describe this image" is used.

```bash
# Implicit prompt
./gb --image photo.jpg

# Explicit prompt
./gb --audio clip.wav --prompt "Transcribe this audio"
```

### macOS Power Features
The `mac` tool set allows deep integration with macOS.

```bash
# Analyze a selection of your screen (triggers crosshair)
./gb --tools mac "Analyze the part of my screen I'm about to select"

# Finder integration
./gb --tools mac "Summarize the files I have currently selected in Finder"

# Web Browser context
./gb --tools mac "What is the URL of the site I'm looking at?"

# System control
./gb --tools mac "Switch to dark mode and say 'Good evening'"
```

### Model Selection
The tool defaults to `gemma-4-E2B-it`.
```bash
# Use the 4B model (Higher reasoning)
./gb --high --prompt "Explain quantum decoherence."

# Explicitly use the 2B model
./gb --default --prompt "Who are you?"
```

### Selective Tools
Enable only the tools required for the task. The tool will suggest `--high` if complex tools are enabled.

```bash
# Enable specific tools and sets
./gb --presets preset.py --tools "calculator,fs" --prompt "Find data.csv and calculate the mean"
```

### Context and History
Inject prior context or full conversation history.

```bash
# Use a Markdown file as prior context
./gb --context context.md --prompt "Explain based on above"

# Use a JSONL file for full message history
./gb --context history.jsonl --prompt "Continue our chat"
```

**Available Sets in `preset.py`:**
- `fs`: File system (read, write, list, find, grep)
- `web`: Web (fetching, DuckDuckGo search)
- `sys`: System (time, clipboard, shell, AppleScript/JXA)
- `media`: Media (OCR, conversion, metadata)
- `audio`: Recording and conversion
- `dev`: Git workflow (status, diff)
- `utils`: Math and SQLite queries
- `mac`: macOS Power Features (Shortcuts, Finder selection, Spotlight search, TTS, Browser info, System Appearance, Screenshots/OCR, Launchd LCRUD)

See [CONTRIBUTING.md](CONTRIBUTING.md) for a guide on adding your own tools.

### Structured JSON Output
```bash
# schema.json: {"type":"object", "properties": {"sentiment": {"type":"string"}}}
echo "I love this tool!" | ./gb --schema schema.json --json
```

## Options

| Flag | Description |
|------|-------------|
| `--prompt` | The user text prompt (or path to a prompt file). |
| `--image` | Path to an image file. |
| `--audio` | Path to an audio file. |
| `--system-file` | Named Fabric pattern or system file (system prompt). |
| `--schema` | Path to a JSON schema file. |
| `--context` | Path to JSONL (history) or Markdown (text) file. |
| `--json` | Output strict JSON (cleans markdown filler). |
| `--stream` | Stream the response in real-time. |
| `--tools` | Comma-separated list of tools or sets. |
| `--presets` | Path to your `preset.py` file. |
| `--default` | Force `gemma-4-E2B-it`. |
| `--high` | Force `gemma-4-E4B-it`. |
| `--backend` | Engine backend (`cpu` or `gpu`). Defaults to `gpu` on Apple Silicon. |
| `--vision-backend` | Vision backend (`cpu` or `gpu`). Defaults to `gpu` on Apple Silicon. |
| `--audio-backend` | Audio backend (`cpu` or `gpu`). Defaults to `cpu`. |
| `--max-tokens` | KV cache size (default: 4096). |
