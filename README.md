# gbox — Local, Free, Multimodal AI on Your Mac

![gbox Banner](assets/banner.png)

**100% local. 100% free. No API keys, no usage caps, no telemetry, no cloud round-trips.**

`gbox` is a command-line wrapper around Google's [LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) runtime and Google's open [Gemma 4](https://ai.google.dev/gemma) models, optimized for Apple Silicon. It gives you a multimodal AI assistant — text, image, audio, PDF — that runs entirely on your own hardware, with first-class shell ergonomics and a real tool-calling system.

## Why gbox?

- 🆓 **Free forever** — no subscription, no token billing. Built-in Gemma models are open-weight and downloaded once on first use.
- 🏠 **Fully local & private** — every byte of your prompts, files, screenshots, and audio stays on your machine. Nothing leaves the box.
- ⚡ **Fast on Apple Silicon** — backed by Google's LiteRT-LM with Metal GPU acceleration, plus an optional warm-server mode that eliminates the model-load penalty.
- 🧰 **Real tool calling** — the model can read your filesystem, run AppleScript, query SQLite, OCR images, control macOS, search the web, and more — gated by an explicit `--tools` allowlist.
- 🔌 **OpenAI-compatible API** — drop-in `/v1/chat/completions` endpoint so existing OpenAI client code works unchanged against your local model.
- 🐚 **Unix-native** — pipes, stdin, exit codes, streaming. Composes with the rest of your shell.

### Built on Google's open AI stack

- **[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM)** — Google AI Edge's on-device LLM runtime ([overview](https://ai.google.dev/edge/litert)).
- **[Gemma 4](https://ai.google.dev/gemma)** — Google's multimodal open models designed for edge devices. `gbox` defaults to `gemma-4-E2B-it`, switches to `gemma-4-E4B-it` with `--high`, and can run the larger `gemma-4-12b` model with `--model`.
  - [Gemma 4 Model Card Comparison](https://ai.google.dev/gemma/docs/core/model_card_4)

## Features

- **Multimodal Support**: Seamlessly handle text, images, and **audio** in a single prompt.
- **PDF Intelligence**: Automatically detects piped PDFs, extracting text and rendering the first page for the vision backend.
- **Structured Output**: Enforce strict JSON responses using the `--schema` flag.
- **Real-Time Streaming**: Use the `--stream` flag to see the model's response as it generates.
- **Clipboard Output**: Pass `-c` / `--clipboard` to copy the final result straight to the macOS clipboard.
- **System Instructions**: Inject system-level instructions or named Fabric patterns using the `--system-file` flag.
- **Modular Tooling**: Enable specific tools or predefined tool sets from a modular `tools/` package.
- **Context Awareness**: Inject conversation history via JSONL or raw text context via Markdown using the `--context` flag.
- **Smart Recommendations**: Suggests using the `--high` (4B) model when complex tools (like AppleScript, SQLite, or macOS system automation) are requested.
- **Flexible Model Selection**: Use the default 2B model, `--high` for 4B, `--model gemma-4-12b` for the larger Gemma 4 12B model, or reference any model imported via `litert-lm import` by its shorthand ID (e.g. `--model qwen3-4b`). Missing built-in Gemma models are imported automatically on first use. gbox auto-detects each bundle's modalities (text/vision/audio) and MTP draft head, so text-only models like Qwen3 just work — no manual backend flags. Inspect any model with `gbox modelinfo <model>`.
- **Multi-Token Prediction (MTP)**: `--mtp` / `--no-mtp` toggle for LiteRT-LM speculative decoding. Defaults are model-aware on Apple Silicon Metal (**on for `gemma-4-E4B-it`, off otherwise**), **on for non-Darwin GPU** per [upstream guidance](https://ai.google.dev/edge/litert-lm/python#mtp), off for CPU.
- **Unix-Friendly**: Designed for piping and shell automation.

## Installation

Ensure you have the `litert_lm` package installed. For full features, install these dependencies:

```bash
# Required for PDF support
uv pip install pymupdf

# Recommended for specific tools
brew install poppler exiftool sox ffmpeg imagemagick
```

Built-in Gemma models (`gemma-4-E2B-it`, `gemma-4-E4B-it`, and `gemma-4-12b`) are downloaded automatically the first time you run them. `gbox` delegates the import to `litert-lm import` so the files land in LiteRT-LM's normal model registry.

## Usage

### Basic Inference
You can provide the prompt via the `--prompt` flag or as a positional argument.

```bash
# Positional (concise)
gbox "What is the capital of France?"

# Using the flag
gbox --prompt "Hi there!"

# Using a file as a prompt
gbox --prompt instructions.txt

# With real-time streaming
gbox --stream "Write a long poem"

# Copy the result to the clipboard (also works with --json / --stream)
gbox -c "Draft a tweet about on-device inference"
```

### Multimodal (Image & Audio)
If no prompt is provided with an image or audio, a default one like "Describe this image" is used.

```bash
# Implicit prompt
gbox --image photo.jpg

# Explicit prompt
gbox --audio clip.wav --prompt "Transcribe this audio"
```

### macOS Power Features
The `mac` tool set allows deep integration with macOS.

```bash
# Analyze a selection of your screen (triggers crosshair)
gbox --tools mac "Analyze the part of my screen I'm about to select"

# Finder integration
gbox --tools mac "Summarize the files I have currently selected in Finder"

# Web Browser context
gbox --tools mac "What is the URL of the site I'm looking at?"

# System control
gbox --tools mac "Switch to dark mode and say 'Good evening'"
```

### Model Selection
The tool defaults to `gemma-4-E2B-it`. Use `--high` for the 4B model, or `--model` when you want a specific model such as Gemma 4 12B.
```bash
# Use the 4B model (Higher reasoning)
gbox --high --prompt "Explain quantum decoherence."

# Use the 12B model (largest bundled Gemma option)
gbox --model gemma-4-12b --prompt "Design a robust migration plan."

# Explicitly use the 2B model
gbox --default --prompt "Who are you?"

# Fail instead of downloading a missing built-in model
gbox --no-download --model gemma-4-12b --prompt "Hello"
```

#### Using imported / custom models
Models imported with the LiteRT-LM CLI (`litert-lm import <source> <model-id>`) are stored as `~/.litert-lm/models/<model-id>/model.litertlm`. Reference them by their shorthand ID — gbox resolves the registry layout for you. Built-in friendly names resolve to registry IDs when present (`gemma-4-E2B-it` → `gemma4-e2b`, `gemma-4-E4B-it` → `gemma4-e4b`, `gemma-4-12b` → `gemma4-12b`):
```bash
# Shorthand ID from `litert-lm import` (resolves <id>/model.litertlm)
gbox --model qwen3-4b "What is gravitronics?"

# Or any .litertlm file by path
gbox --model ~/.litert-lm/models/my-custom.litertlm "Prompt..."
```
gbox inspects each bundle before loading and only wires up the encoders it actually contains, so a **text-only** model (e.g. Qwen3) runs without you having to disable the vision/audio backends. Models lacking an MTP draft head also auto-disable speculative decoding.

#### Inspecting a model
Use `modelinfo` to see a model's modalities, format, size, and MTP support without loading it:
```bash
gbox modelinfo qwen3-4b
# Model:      qwen3-4b
# Path:       /Users/you/.litert-lm/models/qwen3-4b/model.litertlm
# Size:       5.3 GB
# Format:     LiteRT-LM 1.5.0
# Modalities: text
# MTP draft:  no
```

### Selective Tools
Enable only the tools required for the task. The tool will suggest `--high` if complex tools are enabled.

```bash
# Enable specific tools and sets (bundled preset.py is auto-resolved when --tools is given)
gbox --tools "calculator,fs" --prompt "Find data.csv and calculate the mean"

# Point at your own preset module instead
gbox --presets ~/my-preset.py --tools "mac,my_custom_tool" --prompt "..."
```

### Context and History
Inject prior context or full conversation history.

```bash
# Use a Markdown file as prior context
gbox --context context.md --prompt "Explain based on above"

# Use a JSONL file for full message history
gbox --context history.jsonl --prompt "Continue our chat"
```

**Available Sets in `preset.py`:**
- `fs`: File system (read, write, list, find, grep)
- `web`: Web (fetching, DuckDuckGo search)
- `sys`: System (time, clipboard, shell, AppleScript/JXA)
- `media`: Media (OCR, conversion, metadata)
- `audio`: Recording and conversion
- `dev`: Git workflow (status, diff)
- `utils`: Math and SQLite queries
- `mac`: macOS Power Features (Shortcuts, Keyboard Maestro macros, Finder selection, Spotlight search, TTS, Browser info, System Appearance, Screenshots/OCR, Launchd LCRUD)

See [CONTRIBUTING.md](CONTRIBUTING.md) for a guide on adding your own tools.

### Structured JSON Output
```bash
# schema.json: {"type":"object", "properties": {"sentiment": {"type":"string"}}}
echo "I love this tool!" | gbox --schema schema.json --json
```

## Server Mode

gbox can run as a background service to keep the model "warm," significantly reducing the latency of subsequent requests by avoiding repeated model loading.

### Automatic Server Diversion (Smart Proxy)
When you run a standard `gbox` command, it will automatically check if a compatible server is already running. If the server's model and loaded tools satisfy your request, `gbox` will transparently divert the inference to the server. 

**Benefits:**
- **Near-Zero Latency:** Avoids the 3-10 second model loading penalty.
- **Resource Safety:** Prevents multiple model instances from overloading your system's VRAM/RAM.

If the server is incompatible (e.g., you requested `--high` but the server is running the default model), `gbox` will fall back to local execution. Use the `--no-server` flag to force local execution regardless of server status.

Server model, backend, and KV-cache size are startup settings. Do **not** pack them into the API `model` field. Start or restart the server with the desired runtime config:

```bash
gbox --server restart --model gemma-4-12b --backend gpu --max-tokens 32768
```

Then send normal OpenAI-style requests with just the model ID, e.g. `"model": "gemma-4-12b"`. The request `model` value is echoed in responses; it does not hot-swap the already-loaded engine. Larger `--max-tokens` values allocate larger KV caches and can substantially increase memory use and startup latency.

### Control Subcommands
- **Start**: `gbox --server start` (or simply `gbox --server`) — Daemonizes the process. Refuses to start if another gbox is already on the port (idempotent) or if a non-gbox process holds the port (safety).
- **Stop**: `gbox --server stop` — Terminates the background process. Falls back to `lsof` port discovery if the pid file is stale or missing.
- **Restart**: `gbox --server restart` — Stop, wait for the port to free, then start. Useful after code or config changes.
- **Status**: `gbox --server status` — Reports whether a gbox server is alive on the port; flags inconsistent pid-file/port states explicitly instead of guessing.
- **Logs**: `gbox --server logs` — Prints `~/.gbox/server.log`.
- **Config**: `gbox --server config` — Prints the running server's active model, MTP state, backends, tools, and limits (proxies `GET /config`).
- **Models**: `gbox --server models` — Lists models the running server can load (proxies `GET /models`).

### API Usage
The server listens on port **8955** by default and provides OpenAI-compatible endpoints:
- `POST /v1/chat/completions`
- `POST /infer`
- `GET /config` (returns active model, tools, and limits)
- `GET /models` (OpenAI-shaped list of available models)

#### Sample JSON Request (Non-Streaming)
```bash
curl http://localhost:8955/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-4-E2B-it",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain gravity in one sentence."}
    ],
    "stream": false
  }'
```

#### Sample JSON Request (Streaming)
```bash
curl http://localhost:8955/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Count to 5 slowly."}],
    "stream": true
  }'
```

## Options

| Flag | Description |
|------|-------------|
| `--model` | Model ID or path: a `--high`/`--default` name, `gemma-4-12b`, a `litert-lm import` shorthand (e.g. `qwen3-4b`), or any `.litertlm` file. Also usable positionally (`gbox <model> "prompt"`). |
| `--no-download` | Disable first-run auto-download for missing built-in Gemma models. |
| `--prompt` | The user text prompt (or path to a prompt file). |
| `--image` | Path to an image file. |
| `--audio` | Path to an audio file. |
| `--system-file` | Named Fabric pattern or system file (system prompt). |
| `--schema` | Path to a JSON schema file. |
| `--context` | Path to JSONL (history) or Markdown (text) file. |
| `--json` | Output strict JSON (cleans markdown filler). |
| `--stream` | Stream the response in real-time. |
| `-c`, `--clipboard` | Copy the final result to the macOS clipboard (via `pbcopy`). |
| `--no-server` | Disable automatic server diversion. |
| `--server` | Server control: `start`, `stop`, `status`, `logs`, `config`, `models`. |
| `--port` | Port for the inference server (default: 8955). |
| `--tools` | Comma-separated tools or sets to filter the preset down to (e.g. `time`, `clip`, `exec`, `mac`, `fs,web`, `all`). If `--presets` is omitted, the bundled `preset.py` next to `gbox` is auto-loaded. |
| `--presets` | Path to a `preset.py` module. Optional when `--tools` is given (bundled preset is used). |
| `--default` | Force `gemma-4-E2B-it`. |
| `--high` | Force `gemma-4-E4B-it`. |
| `--backend` | Engine backend (`cpu` or `gpu`). Defaults to `gpu` on Apple Silicon. |
| `--vision-backend` | Vision backend (`cpu` or `gpu`). Defaults to `gpu` on Apple Silicon. |
| `--audio-backend` | Audio backend (`cpu` or `gpu`). Defaults to `cpu`. |
| `--max-tokens` | LiteRT-LM KV cache size / maximum context window in tokens (default: 4096; larger values use more memory). |
| `--mtp` / `--no-mtp` | Toggle Multi-Token Prediction (speculative decoding). Defaults: model-aware on Apple Silicon Metal (**on for `gemma-4-E4B-it`, off otherwise**), **on for non-Darwin GPU**, off for CPU. See [ISSUES.md](ISSUES.md) for benchmark data. |

---

## Smoke Test

Run a quick local regression check after changing `gbox`:

```bash
scripts/smoke.sh
```

## Demos

The [`demo/`](demo/) directory ships a set of single-file bash utilities built on `gbox` — `cmd` (natural language → shell command), `oneliner` (pipe chains from English), `wtd` ("what is this directory?"), `explain`, `naming`, `port`, `gitsum`, and `mac-narrator`. Inspired by [apfel](https://github.com/Arthur-Ficial/apfel)'s demo set, ported to use on-device LiteRT-LM via `gbox` instead of Apple Intelligence.

```bash
cd demo
./cmd "find all .log files modified today"
./gitsum 20
./wtd ~/some/project
```

System prompts live in [`demo/systems/`](demo/systems/) so you can tune tone or output format without touching bash. See [`demo/README.md`](demo/README.md) for the full list, examples, and global-install instructions.

> **Speed tip:** run `gbox --server start` once. Every demo call then auto-proxies through the warm server instead of cold-starting the model.

---

## Support

If this project helps you keep your AI workflows local and free, consider buying me a coffee! It helps keep the updates coming.

<a href="https://paypal.me/2b3/5">
  <img src="https://img.shields.io/badge/Donate-PayPal-blue.svg" alt="Donate with PayPal" />
</a>

**[https://paypal.me/2b3/5](https://paypal.me/2b3/5)**

---

## License

MIT License - Created by [Ian Shen](https://github.com/2b3pro).
