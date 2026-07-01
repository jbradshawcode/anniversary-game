#!/usr/bin/env bash
# Asset-bake: render the procedural _draw() art to PNG textures under assets/baked/.
# Needs a real GPU (not --headless, which renders blank). Mirrors verify.sh.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/opt/homebrew/bin/godot}"
"$GODOT" --path "$HERE" --quit-after 600 -- --bake
echo "baked into $HERE/assets/baked/"
