# Investigation: `enable_thinking` / a `--think` flag

**Date:** 2026-05-11
**Tested against:** `litert-lm` 0.10.1, `gemma-4-E2B-it.litertlm`, GPU backend, Apple M2 Pro
**Question:** Should `gbox` expose a `--think` flag? Does LiteRT-LM's chat-template
thinking mode offer measurable value today?

## TL;DR

- **The knob already works.** Passing `extra_context={"enable_thinking": True}` to
  `Engine.create_conversation(...)` is honored by the Gemma 4 chat template *right now*
  on litert-lm 0.10.1 — no SDK upgrade needed.
- **It currently buys nothing measurable** on `gemma-4-E2B-it`: zero correctness lift in
  testing, 1.5×–3.5× slower decode, and the thinking trace is **swallowed by the SDK**
  (never returned in the response `content`, so it can't even be displayed).
- **Decision: do not add `--think` yet.** It would be a strictly-worse `--high`. Revisit
  if (a) litert-lm starts returning the thinking trace as a distinct content block, or
  (b) a sweep on `gemma-4-E4B-it` against a real reasoning benchmark shows a delta worth
  the latency tax.

## What the SDK exposes (litert-lm 0.10.1)

`Engine(...)` accepts: `model_path`, `backend`, `max_num_tokens`, `cache_dir`,
`vision_backend`, `audio_backend`, `input_prompt_as_hint`, `enable_speculative_decoding`.
There is **no `enable_thinking` Engine parameter** — passing one raises `TypeError`.

`Engine.create_conversation(...)` accepts an `extra_context` mapping, documented as
*"Extra context for the chat template."* That is the channel the thinking toggle flows
through. The Gemma 4 data processor (`Gemma4DataProcessor`) reads `enable_thinking` from
it.

## Evidence it is honored

The runtime's prefill logs (`session_basic.cc:301`) show the templated prompt. With the
toggle off vs. on:

```
# baseline / enable_thinking=False / wrong key (e.g. "thinking": True)
<|turn>user
<prompt>...<turn|>
<|turn>model

# extra_context={"enable_thinking": True}
<|turn>system
<|think|><turn|>          <-- injected directive
<|turn>user
<prompt>...<turn|>
<|turn>model
```

Only the exact key `enable_thinking` with value `True` triggers the `<|think|>` system
turn. `False` and misspelled keys produce the baseline template.

## Behavioural / quality results

**Multi-step word problems, full 4096-token budget, `gemma-4-E2B-it`:**

| Problem | Baseline | `enable_thinking=True` |
|---|---|---|
| Bat & ball ($0.05) | ✅ correct, 6.9s | ✅ correct, 12.7s |
| 5 machines / 100 widgets (5 min) | ✅ correct, 5.1s | ✅ correct, 17.5s |
| Egg cartons, multi-step (2 cartons, 0 left) | ✅ correct, 3.6s | ✅ correct, 5.3s |
| Apple/sheep trick questions | ❌ wrong | ❌ still wrong, ~32× slower |

- **No correctness change** observed in either direction.
- **Latency cost:** consistently 1.5×–3.5× slower; on one short prompt the decode went
  from 0.2s → 6.5s while the *visible* output stayed ~3 chars — i.e. the model spent
  ~6s generating thinking tokens that were then discarded.
- **Thinking trace is hidden:** the response always came back as a single
  `{"type": "text", ...}` block. No separate `thinking`/`reasoning` block, no inline
  `<think>…</think>` or `<|think|>…<|/think|>` markers. With the current SDK there is
  nothing for `gbox` to surface even if it wanted a `--show-thinking` option.

Caveats: `n=1` per prompt; only the small (E2B) model tested. A lift on E4B or on
harder problems is not ruled out — just unproven.

## If `--think` is added later

Minimal, ~10 lines:

1. `parser.add_argument("--think", action=argparse.BooleanOptionalAction, default=None)`
   near the other backend flags (`gbox` ~line 560). Tri-state: `None` = model default.
2. Thread it into the two `create_conversation(...)` call sites (`gbox` ~344 and ~834):
   `extra_context={"enable_thinking": args.think}` only when `args.think is not None`.
3. Probe defensively — wrap in try/except or gate on `litert_lm` version; an unsupported
   model/template should fall back silently rather than error (cf. how
   `enable_speculative_decoding` "throws if the model does not support it").
4. Warn on stderr when `--think` is combined with a low `--max-tokens` — thinking tokens
   eat into the 4096 KV ceiling.
5. Reconcile with `--high`: both express "I want better reasoning." `--high` swaps to
   `gemma-4-E4B-it` (a real capability jump); `--think` toggles a mode on the same model.
   Keep them separate, but consider having `--high` imply `--think` once thinking
   demonstrates value.
6. If the SDK later returns the thinking trace as a distinct content block, add a
   `--show-thinking` / `--hide-thinking` pair and update the text-extraction logic
   (`gbox` ~354/387/855) which currently keeps only `type == "text"` blocks.

## Re-running the experiment

Build a throwaway script that constructs an `Engine` the same way `gbox` does
(`suppress_stderr()` around construction, `backend=GPU`, `max_num_tokens=4096`,
`cache_dir=os.path.dirname(model_path)`), then compare
`engine.create_conversation(messages=[])` vs.
`engine.create_conversation(messages=[], extra_context={"enable_thinking": True})` on a
batch of multi-step problems. Check (a) decode wall-time, (b) whether the final answer is
correct, (c) the `type` of every returned content block, (d) the prefill template echoed
on stderr to confirm the `<|think|>` turn is present.
