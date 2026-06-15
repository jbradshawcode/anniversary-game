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
