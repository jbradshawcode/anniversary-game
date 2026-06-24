# Claude Rules — anniversary-game (Godot port)

In-progress migration of the pygame game (one level up) to **Godot 4.7**. The
pygame source is the reference; port faithfully, then use Godot's renderer for the
graphics upgrade that motivated the move.

## Environment
- Godot 4.7 stable, **GDScript** (not C#). Renderer: GL Compatibility.
- Binary: `/opt/homebrew/bin/godot`. Python 3.9 source game is in the parent dir.

## The one rule that makes agentic work possible: text-first + self-verify
- **Author everything as text** — `.gd` scripts and `.tscn` (hand-written). Build the
  node tree in code (`Main.gd`), don't rely on editor clicking. Agents can't drive the GUI.
- **Verify by screenshot every visual change**: `bash tools/verify.sh` runs the project,
  grabs one frame to `verify_shot.png`, and quits. Read that PNG to see your own output
  and iterate. Do NOT use `--headless` for screenshots — its dummy renderer outputs blank.
- After adding/renaming a `class_name`, run `godot --path . --headless --import` once so the
  global class cache picks it up, then run normally.
- **The verify shot must exercise every code path, not just the visible one.** A screenshot
  only renders one branch — drive the others too (e.g. a normal move AND a scene transition)
  and `assert(...)` their post-conditions in `Main._shot()`. A try_move signature regression
  once passed the shot because the shot only took the exit branch; interactive play caught it.
- **Call `RenderingServer.force_draw()` before `get_viewport().get_texture().get_image()`.**
  The OS stops rendering an unfocused window, so a bare read-back returns a stale frame —
  three different scenes once saved byte-identical screenshots until force_draw was added.

## Architecture mapping (pygame → Godot)
- `config.py`            → `globals/Config.gd` (autoload singleton, consts).
- `systems/tilemap.py`   → `systems/TileGrid.gd` (RefCounted; walkable rect + walled edges).
- `entities/.../player`  → `entities/Player.gd` (Node2D; `try_move`/`update` ported 1:1).
- `scenes/sceneN.py`     → `scenes/SceneN.gd` (Node2D; `draw_structures` → `_draw()`).
- Scene owns its `TileGrid` and exposes `is_walkable(tx,ty)` / `has_wall(fx,fy,tx,ty)`.

## Porting art: `pygame.draw.*` → `_draw()`
The original's art is procedural and maps almost line-for-line. Same coords (Y is down
in both), tile math unchanged (`TILE_SIZE=32`):
- `pygame.draw.rect(s, c, (x,y,w,h))`      → `draw_rect(Rect2(x,y,w,h), c)`
- `...rect(s, c, rect, width)` (outline)   → `draw_rect(rect, c, false, width)`
- `pygame.draw.line(s, c, a, b, w)`        → `draw_line(Vector2(a), Vector2(b), c, w)`
- `pygame.draw.circle` outline             → `draw_arc(center, r, 0, TAU, 24, c, w)`
- `pygame.draw.ellipse`                    → `draw_circle` under a scaled `draw_set_transform`
- Colors: `(r,g,b)` 0–255 → `Color8(r,g,b)`.

## Graphics upgrade (the point of the migration)
Use real engine features, don't re-fake the pygame approximations:
- Lighting: `CanvasModulate` (ambient) + `PointLight2D` pools (texture via `systems/LightTex.gd`,
  generated in code — no image assets). Lights on movers (e.g. the player glow) are dynamic.
- Tune lighting by screenshot; `energy`/ambient color are sensitive — iterate, don't guess.
