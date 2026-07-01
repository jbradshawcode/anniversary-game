#!/usr/bin/env bash
# Agent/CI verify loop: run the project through the _shot() screenshot suite, then quit.
# Shots are written to a temp dir (ANNIV_SHOT_DIR) so they don't clog the project dir.
# Needs a real GPU (not --headless, which renders blank).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/opt/homebrew/bin/godot}"
SHOT_DIR="${ANNIV_SHOT_DIR:-${TMPDIR:-/tmp}/anniv-verify}"
mkdir -p "$SHOT_DIR"
ANNIV_SHOT_DIR="$SHOT_DIR" "$GODOT" --path "$HERE" --quit-after 8000 -- --shot
echo "wrote $(ls "$SHOT_DIR"/verify_*.png 2>/dev/null | wc -l | tr -d ' ') shots to $SHOT_DIR"
