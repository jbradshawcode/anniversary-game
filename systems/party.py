"""Follower party — the gym crew trailing the player in a conga line.

Followers chase a breadcrumb trail of the player's recent tile centres, so they
trace the actual path (no corner-cutting) and settle one tile apart when the
player stops. They are never added to any scene's tile map, so they can't jam
the player. Presence is derived from the story beat, so nothing here is saved.
"""
import pygame
from typing import List, Optional, Tuple, TYPE_CHECKING
from config import TILE_SIZE, TILE_MOVE_SPEED
from entities import James, Dan, Matt, Nat, Leonard

if TYPE_CHECKING:
    from entities.characters.player import Player

# The Saturday gym cast, in conga order behind the player.
WEEK1_CREW = [James, Dan, Matt, Nat, Leonard]

_Pt = Tuple[float, float]


def _tile_center(tile_x: int, tile_y: int) -> _Pt:
    return (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2)


class Party:
    def __init__(self) -> None:
        self.followers: List = []
        self._trail: List[_Pt] = []
        self._last_tile: Optional[Tuple[int, int]] = None
        self._following = False

    @property
    def active(self) -> bool:
        return bool(self.followers)

    def clear(self) -> None:
        self.followers = []
        self._trail = []
        self._last_tile = None
        self._following = False

    def form(self, player: 'Player', scene_manager) -> None:
        """Spawn the crew stacked on the player and stop drawing them as scenery."""
        self.followers = [cls(player.tile_x, player.tile_y) for cls in WEEK1_CREW]
        for f in self.followers:
            f.blocking = False
            f.x, f.y = float(player.x), float(player.y)
        if scene_manager is not None and scene_manager.current is not None:
            crew_types = tuple(WEEK1_CREW)
            scene = scene_manager.current
            scene.objects = [
                o for o in scene.objects if not isinstance(o, crew_types)]
            # The crew's old tiles were baked in as blocked at scene build time;
            # rebuild so the player can walk through the space they vacated.
            scene._build_tile_map()
        self._seed(player)
        self._following = True

    def settle(self, scene_id: int, tiles) -> None:
        """Park the followers on the given tiles and stop following."""
        for f, tile in zip(self.followers, tiles):
            f.tile_x, f.tile_y = tile
            f.x, f.y = _tile_center(tile[0], tile[1])
            f.walking = False
        self._following = False

    def stop_following(self) -> None:
        """Freeze followers where they stand (e.g. after a seating cutscene)."""
        for f in self.followers:
            f.walking = False
        self._following = False

    def on_scene_change(self, player: 'Player') -> None:
        if not self.followers:
            return
        for f in self.followers:
            f.x, f.y = float(player.x), float(player.y)
        self._seed(player)
        self._following = True

    def _seed(self, player: 'Player') -> None:
        self._trail = [_tile_center(player.tile_x, player.tile_y)]
        self._last_tile = (player.tile_x, player.tile_y)

    def update(self, dt: float, player: 'Player') -> None:
        if not self._following or not self.followers:
            return
        cur = (player.tile_x, player.tile_y)
        if cur != self._last_tile:
            self._trail.append(_tile_center(cur[0], cur[1]))
            self._last_tile = cur
            cap = len(self.followers) + 3
            if len(self._trail) > cap:
                self._trail = self._trail[-cap:]
        for i, f in enumerate(self.followers):
            idx = len(self._trail) - 2 - i
            if idx < 0:
                idx = 0
            self._step(f, self._trail[idx], dt)

    @staticmethod
    def _step(f, target: _Pt, dt: float) -> None:
        dx = target[0] - f.x
        dy = target[1] - f.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 0.5:
            f.walking = False
            return
        if abs(dx) >= abs(dy):                # face the way we're walking
            f.facing = 'right' if dx > 0 else 'left'
        else:
            f.facing = 'down' if dy > 0 else 'up'
        step = TILE_MOVE_SPEED * dt
        if step >= dist:
            moved = dist
            f.x, f.y = target
        else:
            moved = step
            f.x += dx / dist * step
            f.y += dy / dist * step
        f.walking = True
        f.walk_phase += moved * 0.2       # ~one bob cadence per tile

    def draw(self, surface: pygame.Surface) -> None:
        for f in self.followers:
            f.draw(surface)
