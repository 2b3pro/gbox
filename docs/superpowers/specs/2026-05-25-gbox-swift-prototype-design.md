# gbox-swift Spike — Design

**Date:** 2026-05-25
**Status:** Approved for implementation planning
**Scope:** Smallest spike that validates the litert-lm Swift API as a credible substrate for a future Swift rewrite of gbox. Not a CLI replacement, not a port — a yes/no answer in ~1 day.

## Why

Current gbox is 1,147 lines of single-file Python wrapping `litert_lm` for on-device multimodal inference on Apple Silicon. Two structural costs of staying on Python:

1. **Tool ecosystem cost.** 7 tool modules (~733 lines) shell out heavily to `osascript`, `sips`, `screencapture`, `mdfind`, `launchctl`, `shortcuts`. Each shellout is a `fork`+`exec`+string-parse cycle that has a direct native equivalent on macOS (NSWorkspace, PDFKit, EventKit, AVFoundation, Vision, AppKit, UserNotifications).
2. **Inference plumbing cost.** FD-level `dup2` stderr suppression to silence Metal logs, manual `.venv` re-exec dance, hand-rolled SSE streaming shim, PyMuPDF dependency for PDF handling that PDFKit covers natively.

litert-lm publishes a Swift SDK (`https://github.com/google-ai-edge/LiteRT-LM` from `0.12.0`) with near-1:1 API parity for `Engine`, `Conversation`, `sendMessageStream`, `Tool`/`@ToolParam`, `SamplerConfig`, MTP, and the same `.litertlm` model format. The spike tests whether a Swift port is mechanically feasible and ergonomically better before committing to any larger migration.

## Goals (what success looks like)

After running the spike, we should have an unambiguous yes/no on each of:

1. **SPM resolution works.** `swift build` resolves `google-ai-edge/LiteRT-LM` at `0.12.0` without auth issues, missing artifacts, or platform gating.
2. **Engine loads existing `.litertlm` files.** The same `gemma-4-E2B-it.litertlm` used by Python loads under the Swift Engine without conversion.
3. **Streaming feels right.** `for try await chunk in conversation.sendMessageStream(...)` produces chunks in the same shape and cadence as the Python `send_message_async` SSE shim, with no terminal buffering.
4. **Tool authoring + invocation works end-to-end.** A `Tool`-conforming type with no `@ToolParam`s is discoverable to the model and invoked when the prompt asks about Finder selection — i.e. schema generation from Swift types produces something the model uses.
5. **Stderr cleanliness.** First empirical test of whether the Swift bindings silence Metal `I0000` logs by default, or whether the Python-side FD-level `dup2` hack still applies.

## Non-goals

Explicit out-of-scope so the spike doesn't grow:

- HTTP server, smart proxy, `/v1/chat/completions`, `/config`, `/models`.
- CLI flags beyond positional prompt. No `--model`, `--high`, `--system-file`, `--session`, `--tools`, `--mtp`, `--backend`, `--image`, `--audio`, `--max-tokens`, `--temperature`.
- Image/audio/PDF input wiring (engine declares the capability but the CLI doesn't expose it).
- System prompt loading (no `system.md` equivalent).
- Fabric resource resolution.
- Session windowing.
- Multi-token-prediction toggle (use Engine default).
- Tools other than `FinderSelectionTool`. The remaining 6 modules in `tools/` are untouched.
- XCTest target. Validation is manual side-by-side against Python gbox.
- Performance benchmarking. We're testing feasibility and ergonomics, not throughput.

## Architecture

### Layout

```
gbox-swift/
├── .gitignore              # /.build/, /.swiftpm/, *.xcodeproj
├── Package.swift           # SPM manifest
├── README.md               # how to build/run, what the spike proves
└── Sources/
    └── gbox-swift/
        ├── main.swift                  # CLI entry, Engine setup, stream loop
        └── FinderSelectionTool.swift   # Tool conformance + NSAppleScript bridge
```

### Package.swift

```swift
// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "gbox-swift",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(url: "https://github.com/google-ai-edge/LiteRT-LM", from: "0.12.0"),
    ],
    targets: [
        .executableTarget(
            name: "gbox-swift",
            dependencies: [
                .product(name: "LiteRT-LM", package: "LiteRT-LM"),
            ]
        ),
    ]
)
```

**Platform choice:** macOS 14 (Sonoma). Covers full async/await Foundation. Ian's machine is on macOS 26, so this is conservative.

**Note:** the exact product name from the LiteRT-LM Swift package may differ from `"LiteRT-LM"`. First implementation step verifies this against the package's actual `Package.swift`.

### Model resolution

Hardcoded path: `~/.litert-lm/models/gemma-4-E2B-it.litertlm`.

- Matches Python gbox's third search path (`get_available_models` in `gbox`).
- If the file doesn't exist, fail before constructing `Engine` with: `"Error: model not found at <path>. Run gbox --models to see available models."`
- No env-var override, no fallback list. The spike is hardcoded; the future port handles full resolution.

## Components

### main.swift (~100 lines)

Pseudocode:

```swift
import Foundation
import LiteRT_LM

@main
struct GboxSwift {
    static func main() async throws {
        // 1. Argument parsing
        let args = CommandLine.arguments
        guard args.count >= 2 else {
            FileHandle.standardError.write(Data("Usage: gbox-swift \"<prompt>\"\n".utf8))
            exit(2)
        }
        let prompt = args.dropFirst().joined(separator: " ")

        // 2. Model resolution
        let modelURL = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".litert-lm/models/gemma-4-E2B-it.litertlm")
        guard FileManager.default.fileExists(atPath: modelURL.path) else {
            FileHandle.standardError.write(Data("Error: model not found at \(modelURL.path)\n".utf8))
            exit(1)
        }

        // 3. Engine
        let engineConfig = EngineConfig(modelPath: modelURL.path)
        let engine = Engine(engineConfig: engineConfig)
        try await engine.initialize()

        // 4. Conversation
        let convConfig = ConversationConfig(
            tools: [FinderSelectionTool()],
            sampler: SamplerConfig(topK: 40, topP: 0.95, temperature: 0.7, maxNumTokens: 2048)
        )
        let conversation = try await engine.createConversation(config: convConfig)

        // 5. Stream
        let start = Date()
        var chunkCount = 0
        for try await chunk in conversation.sendMessageStream(Message(prompt)) {
            FileHandle.standardOutput.write(Data(chunk.text.utf8))
            chunkCount += 1
        }
        FileHandle.standardOutput.write(Data("\n".utf8))

        // 6. Stats
        let elapsed = Int(Date().timeIntervalSince(start) * 1000)
        FileHandle.standardError.write(Data("[\(chunkCount) chunks, \(elapsed)ms]\n".utf8))
    }
}
```

**Notes for implementation:**
- Exact API names (`EngineConfig`, `ConversationConfig`, `SamplerConfig`, `Message`, `chunk.text`) are taken from the documentation we fetched. Verify against the installed SDK headers in step 1 of execution and correct if they differ.
- `EngineConfig` may take additional modality flags or backend hints. Use defaults; we are not exercising image/audio inputs in the spike.
- `Message(prompt)` is the text-only constructor. If the SDK requires `Message(Content.text(prompt))` or similar, adjust.

### FinderSelectionTool.swift (~50 lines)

Pseudocode:

```swift
import Foundation
import LiteRT_LM

struct FinderSelectionTool: Tool {
    static let toolName = "get_finder_selection"
    static let toolDescription = """
        Get the POSIX paths of the items currently selected in Finder. \
        Returns one path per line, or an empty string if nothing is selected. \
        Use this when the user asks about their current Finder selection.
        """

    func run() async -> String {
        let source = """
            tell application "Finder"
                set theItems to selection
                set thePaths to {}
                repeat with anItem in theItems
                    set end of thePaths to POSIX path of (anItem as alias)
                end repeat
                return thePaths
            end tell
            """

        guard let script = NSAppleScript(source: source) else {
            return "Error: failed to compile AppleScript"
        }

        var errorInfo: NSDictionary?
        let result = script.executeAndReturnError(&errorInfo)

        if let errorInfo {
            let msg = errorInfo[NSAppleScript.errorMessage] as? String ?? "unknown"
            return "Error: \(msg)"
        }

        // Walk the list descriptor
        var paths: [String] = []
        for i in 1...result.numberOfItems {
            if let path = result.atIndex(i)?.stringValue {
                paths.append(path)
            }
        }
        return paths.joined(separator: "\n")
    }
}
```

**Notes for implementation:**
- Exact `Tool` protocol shape (associated types, async signature, how name/description are surfaced, whether `static` or instance properties) is taken from the documentation. Verify against SDK and adjust.
- `NSAppleScript` is chosen over `Process` → `/usr/bin/osascript` for the native-API thesis: no subprocess fork/exec, structured `NSAppleEventDescriptor` return instead of stdout string parsing, inline error info in `NSDictionary`.
- The AppleScript itself matches what `tools/macos.py`'s `get_finder_selection` shells to, for behavior parity.
- Description text matches the Python tool's docstring conventionally so we're testing Swift schema generation, not prompt engineering.

## Data flow

```
CLI arg
  ↓
Engine.initialize(model.litertlm)
  ↓
Conversation w/ FinderSelectionTool registered
  ↓
sendMessageStream(prompt) ──[model invokes tool]──→ FinderSelectionTool.run()
  ↓                                                       ↓
AsyncSequence chunks → stdout                         NSAppleScript → [paths]
                                                          ↓
                                                      String → engine resumes
```

## Error handling

| Failure | Handling |
|---|---|
| Missing prompt arg | Stderr usage line, exit 2 |
| Model file missing | Explicit error before `Engine` construction, exit 1 |
| Engine init throws | Stderr message, exit 1 |
| Stream throws mid-response | Print what we have, stderr error, exit 1 |
| Tool AppleScript compile error | Return `"Error: failed to compile AppleScript"` (string, not throw) |
| Tool AppleScript runtime error | Return `"Error: <NSDictionary errorMessage>"` (string, not throw) |

The tool-error convention (`"Error: ..."` string return rather than throw) matches Python gbox's tool convention so the model can reason about the failure and retry. This is enforced because LiteRT-LM surfaces tool returns to the model verbatim.

**No FD-level stderr suppression in the spike.** First empirical question: do the Swift bindings already silence Metal `I0000` logs? If they do, the Python `suppress_stderr` hack is unnecessary on the Swift side and we delete that complexity in the future port. If they don't, we know to add equivalent suppression in phase 2.

## Validation

Manual side-by-side. Select 2-3 files in Finder, then:

```bash
# Swift spike
cd gbox-swift
swift build
swift run gbox-swift "list my finder selection in a markdown table"

# Python equivalent for comparison
cd ..
./gbox --tools mac "list my finder selection in a markdown table"
```

### Success criteria checklist

- [ ] `swift build` succeeds, SPM resolves the litert-lm Swift package
- [ ] `swift run gbox-swift "hello"` (no tool path) produces streamed text output
- [ ] `swift run gbox-swift "what is in my finder selection?"` causes the model to invoke `get_finder_selection`
- [ ] Tool returns the selected file paths, formatted into the model's response
- [ ] Stream chunks appear progressively in the terminal (no whole-response buffering)
- [ ] Final output is qualitatively comparable to the Python `gbox --tools mac` invocation

### No-go signals

- SPM cannot resolve `google-ai-edge/LiteRT-LM` (package not actually published despite docs).
- Engine init throws on the existing `.litertlm` (Swift binding incompatibility).
- Tool schema generation produces something the model never invokes (the description matches Python's, so this would mean Swift's `Tool` protocol isn't surfacing what we expect).

## What this spike does NOT decide

Even on a clean "yes" across all success criteria, this spike does not commit to:

- Porting the remaining 6 tool modules.
- Building the HTTP server in Swift.
- Replacing Python gbox.
- A specific Swift-side architecture for the eventual full port (single-file CLI vs library + executable split).

Those are separate decisions made after the spike's evidence lands.

## Open questions to resolve during implementation

1. **Exact SDK API surface.** Documentation gave us approximate names (`EngineConfig`, `ConversationConfig`, `SamplerConfig`, `Message`, `Tool`, `@ToolParam`). The first implementation step verifies these against the installed package and corrects the spike code if they differ.
2. **`Tool` protocol shape.** Whether name/description are static properties, instance properties, computed, or set via a function builder. Documentation showed `@ToolParam` for parameters; for a zero-parameter tool the registration shape needs SDK confirmation.
3. **Message content constructor.** Whether `Message("prompt")` works directly or requires `Message(Content.text("prompt"))`.
4. **Chunk type from `sendMessageStream`.** Whether iterating yields a `Chunk` with `.text` accessor, or a raw `String`, or a richer structure with deltas.
5. **MTP default in Swift bindings.** Documentation said "universally recommended for GPU/Metal" — but `ISSUES.md` in Python gbox found MTP slower on Apple Silicon Metal. The spike runs with whatever the Swift default is and notes it. (Resolving the contradiction is out of scope for the spike.)
