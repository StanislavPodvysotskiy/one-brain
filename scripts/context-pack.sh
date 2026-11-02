#!/usr/bin/env bash
# Packs a project's context for a web chat without file access: prints it and copies it to the clipboard.
# Usage: scripts/context-pack.sh "Project name" [number of latest sessions, default 3]
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/clipboard.sh"
NAME="${1:?Usage: scripts/context-pack.sh \"Project name\" [N]}"
OUT="$(python3 "$DIR/brain.py" context "$NAME" -n "${2:-3}" --web)"
printf '%s\n' "$OUT"
printf '%s\n' "$OUT" | clip_copy
echo "--- Copied to the clipboard ($(printf '%s' "$OUT" | wc -c | tr -d ' ') bytes) ---" >&2
