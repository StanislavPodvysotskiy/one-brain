#!/usr/bin/env bash
# Saves a web chat's session summary (text in the clipboard) into the project.
# Usage:
#   scripts/save-session.sh "Project" kimi "session topic"   — clipboard → sessions/YYYY-MM-DD_kimi_session-topic.md
#   scripts/save-session.sh "Project" decisions              — clipboard → new entries on top of DECISIONS.md
#   scripts/save-session.sh "Project" status                 — clipboard → STATUS.md (the old version stays in Git)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/clipboard.sh"
NAME="${1:?Specify the project}"
MODEL="${2:?Specify the model (claude, kimi, qwen…), decisions or status}"
TEXT="$(clip_paste)"
[[ -n "$(printf '%s' "$TEXT" | tr -d '[:space:]')" ]] || { echo "The clipboard is empty" >&2; exit 1; }
if [[ "$MODEL" == "status" ]]; then
  printf '%s\n' "$TEXT" | python3 "$DIR/brain.py" save-status "$NAME"
  exit 0
fi
if [[ "$MODEL" == "decisions" ]]; then
  printf '%s\n' "$TEXT" | python3 "$DIR/brain.py" save-decisions "$NAME"
  echo "Now copy the new STATUS.md from the chat and run"
  echo "  scripts/save-session.sh \"$NAME\" status"
  exit 0
fi
printf '%s\n' "$TEXT" | python3 "$DIR/brain.py" save-session "$NAME" "$MODEL" "${3:?Specify the session topic}"
echo "Next, copy from the chat and run:"
echo "  the new decisions, if the chat made any:  scripts/save-session.sh \"$NAME\" decisions"
echo "  the new STATUS.md:                        scripts/save-session.sh \"$NAME\" status"
