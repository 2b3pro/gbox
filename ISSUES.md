# Known Issues & Upstream Tracking

This file tracks known limitations, hardware-specific constraints, and upstream issues from the [LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) repository that affect `gbox`.

## Hardware Constraints

### Audio Backend (CPU Only)
- **Status:** Active Constraint
- **Description:** Currently, LiteRT-LM models (like Gemma-4) require the audio backend to be set to `cpu`. Attempting to use `gpu` for audio results in a `Runtime Error: Audio backend constraint mismatch`.
- **Workaround:** `gbox` defaults `audio-backend` to `cpu` automatically.

## Upstream Issues (LiteRT-LM)

### Excessive GPU Logging on macOS (#1999)
- **Reference:** [LiteRT-LM Issue #1999](https://github.com/google-ai-edge/LiteRT-LM/issues/1999)
- **Description:** Using the GPU backend on macOS via the Python API triggers excessive internal logging (lines starting with `I0000`).
- **Status:** **Confirmed** on Apple M2 Pro. Initialization logs from the WebGPU/Metal delegate are visible in every run.

### Metal Sampler CPU Fallback (#2073)
- **Reference:** [LiteRT-LM Issue #2073](https://github.com/google-ai-edge/LiteRT-LM/issues/2073)
- **Description:** Due to ABI export failures in macOS binaries, the sampler factory may fall back to CPU sampling even when the main engine is on GPU.
- **Impact:** Slight performance overhead during token selection.

### Binary Architecture Mismatch (#2072)
- **Reference:** [LiteRT-LM Issue #2072](https://github.com/google-ai-edge/LiteRT-LM/issues/2072)
- **Description:** Some prebuilt `.dylib` files may be incorrectly packaged as x86_64 instead of arm64.
- **Impact:** Potential load errors on Apple Silicon if certain sub-libraries are invoked.

### CPU Decode Crash on Gemma 4 (#2149)
- **Reference:** [LiteRT-LM Issue #2149](https://github.com/google-ai-edge/LiteRT-LM/issues/2149)
- **Description:** Reports of segfaults on E4B models and hangs on E2B models when using the CPU engine.
- **Impact:** High. Since `gbox` uses `E2B` by default and recommends `E4B` for high cognition tasks, this affects stability when using `--backend cpu`.

### Function Tool Quote Tokens Bug (#2172)
- **Reference:** [LiteRT-LM Issue #2172](https://github.com/google-ai-edge/LiteRT-LM/issues/2172)
- **Description:** Raw Gemma 4 quote tokens (`<|"|>`) are incorrectly passed as string arguments in tool calls.
- **Impact:** High. Causes tool arguments to be parsed incorrectly, particularly affecting complex tool strings (like AppleScript or bash commands).

### Sampler Params Ignored on GPU/NPU (#2080)
- **Reference:** [LiteRT-LM Issue #2080](https://github.com/google-ai-edge/LiteRT-LM/issues/2080)
- **Description:** Session-level parameters like `temperature`, `topK`, and `seed` are ignored by GPU/NPU executors.
- **Impact:** Medium. Model output might not respect custom sampling parameters on Apple Silicon/GPU backends.

### CPU-only Build for Python (#2224)
- **Reference:** [LiteRT-LM Issue #2224](https://github.com/google-ai-edge/LiteRT-LM/issues/2224)
- **Description:** Request for a Python package without GPU dependencies.
- **Impact:** Low. If implemented, could simplify CPU-only environment installations for `gbox`.

### Auto-conversion Path Failure (#2093)
- **Reference:** [LiteRT-LM Issue #2093](https://github.com/google-ai-edge/LiteRT-LM/issues/2093)
- **Description:** CLI fails with `NameError: convert is not defined` during automatic model conversion.
- **Impact:** Low. May affect users relying on automatic model conversions on first run.
