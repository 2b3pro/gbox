#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GBOX="${GBOX_BIN:-$ROOT/gbox}"

echo "== version =="
"$GBOX" --version

echo "== modelinfo =="
"$GBOX" modelinfo gemma-4-12b | grep -E "^(Model|Resolved|Path|Modalities|MTP draft):"

echo "== json =="
json_output="$("$GBOX" --no-server --json "Say hello in Spanish. Return a short response." --max-tokens 512)"
printf '%s\n' "$json_output"
python3 -c 'import json, sys; json.load(sys.stdin)' <<<"$json_output"

echo "== tools =="
tools_output="$("$GBOX" --no-server --tools time --prompt "What is the current time? Answer briefly." --max-tokens 512)"
printf '%s\n' "$tools_output"

echo "== server config =="
if "$GBOX" --server config >/tmp/gbox-smoke-config.json 2>/dev/null; then
  python3 -m json.tool /tmp/gbox-smoke-config.json
else
  echo "No running gbox server on the default port; skipping server config check."
fi
rm -f /tmp/gbox-smoke-config.json

echo "smoke ok"
