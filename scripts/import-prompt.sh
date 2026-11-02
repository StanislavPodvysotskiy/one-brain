#!/usr/bin/env bash
# Prompt for a model's web chat: export its projects from the chat history into One Brain without
# duplicates. Prints it and copies it to the clipboard. Save the model's answer into 00_Inbox/ and ask
# a model with file access to distribute it (the one-brain skill, section 4).
# Usage: scripts/import-prompt.sh kimi
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/clipboard.sh"
OUT="$(python3 "$DIR/brain.py" import-prompt --model "${1:?Usage: scripts/import-prompt.sh kimi}")"
printf '%s\n' "$OUT"
printf '%s\n' "$OUT" | clip_copy
echo "--- Copied to the clipboard ($(printf '%s' "$OUT" | wc -c | tr -d ' ') bytes) ---" >&2
