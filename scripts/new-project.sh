#!/usr/bin/env bash
# Creates a project folder from the templates and adds a row to 00_Home.md.
# Usage: scripts/new-project.sh "Project name" [code folder(s), comma-separated]
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="${1:?Usage: scripts/new-project.sh \"Project name\" [~/code/folder]}"
if [[ -n "${2:-}" ]]; then
  exec python3 "$DIR/brain.py" new-project "$NAME" --repo "$2"
fi
exec python3 "$DIR/brain.py" new-project "$NAME"
