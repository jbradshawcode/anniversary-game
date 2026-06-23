# anniversary-game — Domain Language

Shared vocabulary for the tile-movement and scene systems. Seeded during an
architecture review; extend (or prune) as more seams get named.

## Spatial model

**TileMap**:
The authority on passability for a scene — which tiles are walkable and which
edges between adjacent tiles are walled. Built once from static geometry, then
refreshed with dynamic blockers.
_Avoid_: grid, collision map, navmesh

**Blocker**:
A tile made non-walkable by a movable object (via its `blocked_tiles()`), as
distinct from `static_blocked` scenery fixed at scene-build time.
_Avoid_: obstacle, collider

**Wall**:
An impassable edge *between* two adjacent walkable tiles (e.g. a net or fence):
you can stand beside it but not cross it. Directional.
_Avoid_: barrier, boundary

**Despawn**:
Remove objects from a scene and rebuild its TileMap in one step. Carries the
invariant that mutating a scene's object list requires a walkability rebuild.
_Avoid_: remove, delete, clear

## Movement gating

**Exit verdict**:
The single decision `StoryManager.gate_exit(scene, dir, dest)` returns when the
player steps toward an exit — `'pass'`, `'block'` (refused; any message shown by
Story itself), or `'end_week'`. SceneManager acts on the verdict; it does not
know the beat-level rules (barred door, locked edge, chapter-ending exit) behind
it.
_Avoid_: door block, locked exit (those are inputs to the verdict, not the seam)

## Seating

**Seated state**:
A humanoid is either standing, in transit (carrying a drink in hand), or seated
(drink resting on the table). The three transitions are owned by
`Humanoid.sit()` / `stand()` / `carry()` — the only sanctioned way to change
`sitting` / `holding` / `_drink_xy`, so the "drink in hand only in transit"
invariant can't be half-applied.
_Avoid_: poking holding/sitting directly

## Top-level flow

**Mode**:
The loop's active screen-state (title, overworld, results, phone, …). Exactly one
is active; the pause menu is a Game-level overlay on top, not a Mode.

**Mode transition**:
Every change of the active Mode goes through `Game.to(mode)` — the single seam
that swaps it and clears the pause overlay. The overworld-entry and
return-from-minigame sequences are the named operations `_resume_overworld()` and
`_return_to_gym_and_advance()`.
_Avoid_: assigning `self.active` directly

**Match verdict**:
The volleyball outcome, read as `VolleyCourt.player_won` — the score tuple is the
court's own implementation.
