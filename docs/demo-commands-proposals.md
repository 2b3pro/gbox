# Proposal: additional `demo/` commands

**Date:** 2026-05-24
**Status:** Drafted, not built. Pick from this list before implementing.
**Context:** The first batch of demos (`cmd`, `oneliner`, `wtd`, `explain`, `naming`, `port`, `gitsum`, `mac-narrator`) was ported from [`apfel/demo`](https://github.com/Arthur-Ficial/apfel/tree/main/demo) and only exercises text-in/text-out. gbox has more capabilities — multimodal (image/audio/PDF), `--schema` for strict JSON, smart-proxy speed when the server is warm — and those should drive the next round.

## Design constraints (carry over from the first batch)

- Each command is a single bash script in [`demo/`](../demo/), with a sibling `systems/<name>.md` system prompt.
- Symlink-safe `SCRIPT_DIR` resolution at the top so `gbox-<name>` global install works.
- Default 4096-token KV cache — keep demo inputs trimmed (`head`, truncation, summarize-before-pass when needed), or raise `--max-tokens` for models/hardware that can hold a larger cache.
- Default to E2B; only call `gbox --high ...` when reasoning genuinely benefits (Tier-2 candidates flagged below).
- Stay opinionated. If a command needs more than ~120 lines of bash it probably belongs as a real Python script, not a demo.

## Tier 1 — high-fit, simple to build

These each replace something Ian does multiple times a day and cover four distinct gbox capabilities.

| Command | What it does | gbox feature exercised | Notes |
|---|---|---|---|
| **`commit`** | `git diff --staged` → conventional-commit message | stdin piping | Mirrors `gitsum` shape; output starts with `feat:`/`fix:`/`docs:`/etc. |
| **`pr`** | Branch commits vs `main` → PR title + body (Summary + Test plan) | stdin + multi-section output | Pair with `gh pr create --body-file -` |
| **`tasks`** | Any text (email, meeting notes, transcript) → OmniFocus-pasteable action items | structured text out | One action per line, prefixed `- `, due-dates inline when stated |
| **`cap`** | Clipboard/selection → Roam-ready block: title, tags, 2-line summary, wikilink candidates | matches DevonThink/Roam capture flow | Could later write directly via `roam-research-mcp` |
| **`tx`** | Audio file → clean transcript (drops um/uh, paragraph breaks) | `--audio` (multimodal) | First demo that proves gbox audio works end-to-end |
| **`pdfsum`** | Pipe a PDF → 3-bullet summary + open questions | native PDF auto-handling | Just `cat foo.pdf \| gbox --system-file ...` — gbox does the rest |
| **`whatscreen`** | `screencapture -x /tmp/s.png && gbox --image ...` → "what am I looking at" in 2 sentences | `--image` (vision) | Useful for "where was I 20 min ago" recovery |
| **`reply`** | Quoted email + one-line intent → drafted reply matching the original tone | `--system-file` tone presets | Variants via flags: `-w` warm, `-d` direct, `-s` short |

## Tier 2 — niche but useful

- **`gtd`** — brain-dump → sorted into Projects / Next Actions / Someday / Reference (probably wants `--high`)
- **`rephrase`** — tone dial: `-d` direct, `-w` warmer, `-s` shorter, `-p` plain-language (strip jargon)
- **`chart`** — image of a chart/table → numbers extracted as a markdown table (vision)
- **`quote`** — long text → 3-5 pullable quotes (one per line)
- **`today`** — paste OF today list → reorder by energy curve + dependency (probably wants `--high`)
- **`pick`** — options + criteria → choice with one-paragraph rationale (advisorium-lite)
- **`meeting`** — meeting transcript/notes → Decisions / Open Questions / Action Items (3 sections)
- **`voicememo`** — audio file → speaker-tagged bullets (limited by single-channel input but useful for Audio Hijack captures)

## Tier 3 — requires `--schema`, the real differentiator

These are where gbox stops being "apfel with bigger models" and starts being its own thing. They emit strict JSON that pipes into other tooling.

- **`tasks --json`** → `[{action, project, due, estimate}]` → AppleScript ingester for OmniFocus
- **`chart --json`** → `{headers: [...], rows: [[...]]}` → `jq` or `xlsx` skill
- **`gtd --json`** → `{projects: [...], next_actions: [...], someday: [...], reference: [...]}` → fan-out to multiple sinks
- **`cap --json`** → `{title, tags: [...], summary, wikilinks: [...]}` → direct Roam block via MCP
- **`pr --json`** → `{title, summary, test_plan: [...], risks: [...]}` → `gh pr create` with structured fields

A separate doc — *"adding a `--schemas/` convention to `demo/`"* — should probably land before this tier so the JSON shapes live next to their consumers.

## Recommended first batch

If only five get built, pick **`commit`, `tasks`, `tx`, `pdfsum`, `whatscreen`**. Reasons:

1. Covers four distinct gbox capabilities (text, audio, PDF, vision) in one round — proves the multimodal surface end-to-end.
2. Each one replaces a manual step Ian does daily.
3. None of them need `--high` or `--schema`, so they ship without further infra.
4. `tx` and `whatscreen` are the demos a future visitor will *show their friends*. The first batch is missing that "oh wow" moment.

## Open design questions

- **Where do tone/format variants live?** `reply -w` could either (a) swap `systems/reply.md` for `systems/reply-warm.md` via a case statement, or (b) inject an extra clause into the prompt. Option (a) is more Fabric-pattern-native; option (b) is one fewer file. Pick a convention before building `reply`/`rephrase`.
- **`whatscreen` permissions.** `screencapture` needs Screen Recording permission for the invoking process. First run will prompt; document this in the script header.
- **Audio model availability.** `tx` assumes a model with audio support is loaded (`gemma-4-E4B-it` does; E2B may not). Should the script auto-`--high` when `--audio` is used? Or fail-fast with a clear message? (gbox already has logic around this — verify before building.)
- **JSON convention for Tier 3.** Schemas as JSON Schema files in `demo/schemas/`, or inline-in-script heredocs? JSON Schema files are cleaner and reusable across demos.

## Out of scope for `demo/`

These belong as real CLI tools or PAI skills, not demos:

- Anything that maintains state across calls (a true daemon, a watcher).
- Anything that talks to a remote API (defeats the "on-device" pitch).
- Anything that needs an OAuth flow.

If a demo grows past ~150 lines or starts needing config files, it's outgrown the demo dir.
