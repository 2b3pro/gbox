# MTP Benchmark: Apple M2 Pro GPU

**Date:** 2026-06-09  
**Host:** Apple M2 Pro, 32 GB RAM, macOS 26.5.1  
**Runtime:** gbox 0.7.0, litert-lm 0.13.1  
**Method:** `litert-lm benchmark --backend gpu --prefill-tokens 512 --decode-tokens 256 --max-num-tokens 1024`, three cold-process runs per model/config.

## Summary

MTP on Apple Silicon Metal is model-specific. It is not a universal win or loss.

| Model | MTP OFF decode | MTP ON decode | Delta | Recommendation |
|---|---:|---:|---:|---|
| E2B | 64.30 tok/s | 63.71 tok/s | -0.9% | Default off |
| E4B | 37.50 tok/s | 39.38 tok/s | +5.0% | Default on |
| 12B | 15.20 tok/s | 14.53 tok/s | -4.5% | Legacy standalone bundle; retest registry `gemma4-12b` before defaulting on |

## Full Averages

| Model | MTP | Prefill tok/s | Decode tok/s | Init s | TTFT s | Wall s |
|---|---|---:|---:|---:|---:|---:|
| E2B | off | 1321.04 | 64.30 | 2.60 | 0.41 | 5.94 |
| E2B | on | 1444.04 | 63.71 | 2.52 | 0.37 | 5.89 |
| E4B | off | 381.29 | 37.50 | 7.72 | 1.37 | 12.39 |
| E4B | on | 410.88 | 39.38 | 4.64 | 1.27 | 10.39 |
| 12B | off | 72.61 | 15.20 | 31.24 | 7.14 | 40.05 |
| 12B | on | 63.63 | 14.53 | 26.43 | 8.28 | 39.53 |

## Notes

- The graphical report lives at [`mtp-metal-gpu-2026-06-09.html`](mtp-metal-gpu-2026-06-09.html).
- Earlier 2026-05-24 prompt-level tests showed MTP slower across E2B/E4B on litert-lm 0.12.0. The 2026-06-09 retest on litert-lm 0.13.1 changed the E4B conclusion.
- The 12B rows were captured against a legacy standalone `gemma-4-12B-it.litertlm` bundle. Current gbox-friendly 12B resolution prefers the registry `gemma4-12b/model.litertlm` bundle, which should be benchmarked separately before changing its MTP default.
- Treat these numbers as local to Apple M2 Pro Metal. CUDA/WebGPU backends may behave differently.
