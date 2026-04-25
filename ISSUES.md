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
