"""Walkability grid for a scene — pure tile logic, no pygame.

Owns which tiles are walkable and which edges between adjacent tiles are walled.
Built once from a scene's static geometry (walkable bounds, static_blocked
scenery, walls), then refreshed with the dynamic blockers contributed by movable
objects. Kept free of pygame/entities so it can be tested without a display.
"""
from typing import FrozenSet, Iterable, List, Sequence, Tuple

_Tile = Tuple[int, int]
_Edge = Tuple[_Tile, _Tile]


class TileMap:
    def __init__(self, walkable_cols: Sequence[int], walkable_rows: Sequence[int],
                 map_cols: int, map_rows: int,
                 static_blocked: Iterable[_Tile],
                 walls: Iterable[_Edge]) -> None:
        self._map_cols = map_cols
        self._map_rows = map_rows
        self._walls: FrozenSet[_Edge] = frozenset(walls)

        # Static layer: 1 inside the walkable rectangle, minus statically blocked
        # scenery. Every rebuild starts from a copy of this and layers the
        # dynamic blockers on top, so static geometry survives a refresh.
        col0, col1 = walkable_cols
        row0, row1 = walkable_rows
        self._base: List[List[int]] = [[0] * map_cols for _ in range(map_rows)]
        for row in range(row0, row1 + 1):
            for col in range(col0, col1 + 1):
                self._base[row][col] = 1
        for tx, ty in static_blocked:
            if 0 <= ty < map_rows and 0 <= tx < map_cols:
                self._base[ty][tx] = 0

        self._grid: List[List[int]] = [row[:] for row in self._base]

    def set_blockers(self, tiles: Iterable[_Tile]) -> None:
        """Replace the dynamic blocker layer (movable objects) and rebuild."""
        self._grid = [row[:] for row in self._base]
        for tx, ty in tiles:
            if 0 <= ty < self._map_rows and 0 <= tx < self._map_cols:
                self._grid[ty][tx] = 0

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        if tile_x < 0 or tile_x >= self._map_cols or tile_y < 0 or tile_y >= self._map_rows:
            return False
        return self._grid[tile_y][tile_x] == 1

    def has_wall(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        return ((from_x, from_y), (to_x, to_y)) in self._walls
