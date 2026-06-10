# Gemma 4 Dense Model Specs

**Date captured:** 2026-06-04
**Status:** Reference (transcribed from Gemma model documentation)
**Relevance to gbox:** These are the dense bundles gbox runs on-device. `E2B` is the default (`gbox --default` → `gemma-4-E2B-it`), `E4B` is the high-cognition model (`gbox --high` → `gemma-4-E4B-it`), and `12B Unified` is exposed as `gemma-4-12b` with compatibility aliases for `gemma4-12b` and `gemma-4-12B-it` installs. Missing built-in Gemma bundles are imported on first use via `litert-lm import`. Use `gbox modelinfo <model>` to confirm a local bundle's modalities and MTP draft head.

## Dense Models

| Property | E2B | E4B | 12B Unified |
|---|---|---|---|
| **Total Parameters** | 2.3B effective (5.1B with embeddings) | 4.5B effective (8B with embeddings) | 11.95B |
| **Layers** | 35 | 42 | 48 |
| **Sliding Window** | 512 tokens | 512 tokens | 1024 tokens |
| **Context Length** | 128K tokens | 128K tokens | 256K tokens |
| **Vocabulary Size** | 262K | 262K | 262K |
| **Supported Modalities** | Text, Image, Audio | Text, Image, Audio | Text, Image, Audio |
| **Vision Encoder Parameters** | ~150M | ~150M | — |
| **Audio Encoder Parameters** | ~300M | ~300M | — |

## Notes

- **"Effective" vs "with embeddings" parameter counts** — the E2B/E4B "effective" figure excludes the (large, 262K-vocab) embedding tables; the parenthetical is the full count. gbox defaults `--max-tokens` to 4096 for local memory safety, but the flag can be raised for larger KV caches when the hardware can hold them; this remains separate from the model's native context length (128K–256K above).
- **12B Unified shows full Text/Image/Audio modalities but `—` for the separate vision/audio encoder params** — the "Unified" variant integrates the encoders rather than bundling them as the discrete ~150M vision / ~300M audio add-ons used by E2B/E4B. gbox's capability detection (`detect_model_capabilities`) keys off the `tf_lite_vision_encoder` / `tf_lite_audio_encoder_hw` sections present in the `.litertlm`, so verify per-bundle with `modelinfo` rather than assuming from this table.
- **Local KV-cache reality** — regardless of the 128K/256K native context, usable context is bounded by the `--max-tokens` KV-cache size you start gbox with. Larger values increase memory use; persistent sessions summarize overflow via `manage_session_window`.
