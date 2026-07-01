#!/usr/bin/env bash
# Agent/CI verify loop: run the project, screenshot one frame, quit.
# Writes godot/verify_shot.png. Needs a real GPU (not --headless, which renders blank).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/opt/homebrew/bin/godot}"
"$GODOT" --path "$HERE" --quit-after 4000 -- --shot
echo "wrote $HERE/verify_shot.png"
