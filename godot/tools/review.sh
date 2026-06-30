#!/usr/bin/env bash
# Fixture-vs-bake review sheets: per scene, render the dimmed baked room with every
# Fixture flat-colour-highlighted, so the bake-vs-node split can be eyeballed. Writes
# godot/assets/review/<scene>.png + legend.txt. Needs a real GPU (not --headless).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
GODOT="${GODOT:-/opt/homebrew/bin/godot}"
"$GODOT" --path "$HERE" --quit-after 600 -- --review
echo "wrote review sheets into $HERE/assets/review/"
