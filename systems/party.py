"""Follower party — the gym crew trailing the player in a conga line.

Followers retrace the real tiles the player walked, two abreast where there's
room: one column on the trail itself, a second flanking onto the adjacent walkable
tile and falling into single file whenever that tile is blocked (a turn, a wall, a
doorway). Targets are always real tiles, so nothing straddles a wall edge; their
logical tile tracks their pixel position, and a move-then-resolve pass is a safety
net that shoves anyone out of a solid tile. They are never added to any scene's
tile map, so they can't jam the player. Presence is derived from the story beat,
so nothing here is saved.
"""
import pygame
from typing import List, Optional, Tuple, TYPE_CHECKING
from config import TILE_SIZE, TILE_MOVE_SPEED
from entities import James, Dan, Matt, Nat, Bailey, Mayu, Wallace

if TYPE_CHECKING:
    from entities.characters.player import Player

# The gym cast that heads to the pub, in conga order behind the player. Leonard
# leaves after the Ch1 gym, so he never joins the pub.
WEEK1_CREW = [James, Dan, Matt, Nat, Bailey, Mayu, Wallace]

_Pt = Tuple[float, float]


def _tile_center(tile_x: int, tile_y: int) -> _Pt:
    return (tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2)


class Party:
    def __init__(self) -> None:
        self.followers: List = []
        self._trail: List[_Pt] = []
        self._last_tile: Optional[Tuple[int, int]] = None
        self._following = False
        self._scenes = None              # to honour the same walkability the player obeys

    @property
    def active(self) -> bool:
        return bool(self.followers)

    def clear(self) -> None:
        self.followers = []
        self._trail = []
        self._last_tile = None
        self._following = False

    def form(self, player: 'Player', scene_manager, exclude=()) -> None:
        """Spawn the crew stacked on the player and stop drawing them as scenery.
        `exclude` (names) stay behind as scenery and don't join the party."""
        self._scenes = scene_manager
        roster = [cls for cls in WEEK1_CREW if cls.name not in exclude]
        self.followers = [cls(player.tile_x, player.tile_y) for cls in roster]
        for f in self.followers:
            f.blocking = False
            f.x, f.y = float(player.x), float(player.y)
        if scene_manager is not None and scene_manager.current is not None:
            # Drop only the joining crew from the scene; despawn owns the tile-map
            # rebuild so the space they vacated turns walkable. Excluded crew stay.
            scene_manager.current.despawn(tuple(roster))
        self._seed(player)
        self._following = True

    def settle(self, scene_id: int, tiles) -> None:
        """Park the followers on the given tiles and stop following."""
        for f, tile in zip(self.followers, tiles):
            f.tile_x, f.tile_y = tile
            f.x, f.y = _tile_center(tile[0], tile[1])
            f.walking = False
            # settled crew sit at the pub table, facing it (row 10 sits between the rows);
            # sit() rests any drink they're holding on the table
            f.sit('up' if tile[1] >= 10 else 'down')
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
        self._trail = [(player.tile_x, player.tile_y)]      # trail of real tiles
        self._last_tile = (player.tile_x, player.tile_y)

    def update(self, dt: float, player: 'Player') -> None:
        if not self._following or not self.followers:
            return
        cur = (player.tile_x, player.tile_y)
        if cur != self._last_tile:
            self._trail.append(cur)                       # trail of real tiles the player walked
            self._last_tile = cur
            ranks = (len(self.followers) - 1) // 2 + 1
            cap = ranks + 3
            if len(self._trail) > cap:
                self._trail = self._trail[-cap:]
        for i, f in enumerate(self.followers):
            rank, member = i // 2, i % 2                  # two abreast: a trail column + a flank
            idx = len(self._trail) - 2 - rank
            if idx < 0:
                idx = 0
            target = self._trail[idx]
            if member == 1:                              # the flanking column...
                perp = self._perp_tile(idx)
                cand = (target[0] + perp[0], target[1] + perp[1])
                if self._walkable_tile(cand):
                    target = cand
                else:                                    # ...falls into line when there's no room
                    target = self._trail[max(0, idx - 1)]
            self._step(f, _tile_center(*target), dt)
        self._resolve_collisions()           # move-then-resolve: shove anyone out of a solid tile

    def _perp_tile(self, idx: int) -> Tuple[int, int]:
        """A side direction (in tiles) perpendicular to the trail's heading at idx."""
        a = self._trail[idx]
        b = self._trail[idx - 1] if idx > 0 else (self._trail[idx + 1]
                                                  if idx + 1 < len(self._trail) else a)
        dx, dy = a[0] - b[0], a[1] - b[1]
        if dx and not dy:
            return (0, 1)                    # heading horizontally -> flank vertically
        if dy and not dx:
            return (1, 0)                    # heading vertically -> flank horizontally
        return (0, 1)

    def _walkable_tile(self, tile: Tuple[int, int]) -> bool:
        sc = self._scenes.current if self._scenes is not None else None
        return sc is None or sc.is_walkable(tile[0], tile[1])

    def _walkable_px(self, px: float, py: float) -> bool:
        sc = self._scenes.current if self._scenes is not None else None
        if sc is None:
            return True
        return sc.is_walkable(int(px // TILE_SIZE), int(py // TILE_SIZE))

    def _resolve_collisions(self) -> None:
        """Move-then-resolve: after everyone has stepped, shove any follower whose body
        overlaps a solid tile back out of it (minimum-penetration push, a few passes for
        corners). The rule is simply: a follower never overlaps a solid sprite."""
        sc = self._scenes.current if self._scenes is not None else None
        if sc is None:
            return
        r = 8                                       # follower half-extent in px
        for f in self.followers:
            for _ in range(8):
                moved = False
                lo_x, hi_x = int((f.x - r) // TILE_SIZE), int((f.x + r) // TILE_SIZE)
                lo_y, hi_y = int((f.y - r) // TILE_SIZE), int((f.y + r) // TILE_SIZE)
                for tx in range(lo_x, hi_x + 1):
                    for ty in range(lo_y, hi_y + 1):
                        if sc.is_walkable(tx, ty):
                            continue
                        left, right = tx * TILE_SIZE, (tx + 1) * TILE_SIZE
                        top, bot = ty * TILE_SIZE, (ty + 1) * TILE_SIZE
                        pens = ((f.x + r) - left, right - (f.x - r),
                                (f.y + r) - top, bot - (f.y - r))
                        m = min(pens)
                        if m <= 0:
                            continue
                        if m == pens[0]:
                            f.x -= m
                        elif m == pens[1]:
                            f.x += m
                        elif m == pens[2]:
                            f.y -= m
                        else:
                            f.y += m
                        moved = True
                if not moved:
                    break

    def _step(self, f, target: _Pt, dt: float) -> None:
        dx = target[0] - f.x
        dy = target[1] - f.y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 0.5:                        # arrived -> rest exactly on the tile
            f.x, f.y = target
            f.tile_x, f.tile_y = int(f.x // TILE_SIZE), int(f.y // TILE_SIZE)
            f.walking = False
            return
        if abs(dx) >= abs(dy):                # face the way we're walking
            f.facing = 'right' if dx > 0 else 'left'
        else:
            f.facing = 'down' if dy > 0 else 'up'
        # double-time when lagging (e.g. after waiting at a crossing) to catch up
        speed = TILE_MOVE_SPEED * (1.7 if dist > TILE_SIZE * 2.2 else 1.0)
        step = speed * dt
        if step >= dist:
            nx, ny, moved = target[0], target[1], dist
        else:
            nx, ny, moved = f.x + dx / dist * step, f.y + dy / dist * step, step
        # Collision: a follower must obey the same solid tiles the player does — never
        # step from valid ground into a blocked sprite; slide along the free axis instead.
        # (If it's somehow already inside a blocked tile, let it move out unimpeded.)
        if not self._walkable_px(nx, ny) and self._walkable_px(f.x, f.y):
            if self._walkable_px(nx, f.y):
                ny = f.y
            elif self._walkable_px(f.x, ny):
                nx = f.x
            else:
                nx, ny, moved = f.x, f.y, 0.0
        f.x, f.y = nx, ny
        f.tile_x, f.tile_y = int(f.x // TILE_SIZE), int(f.y // TILE_SIZE)  # logical tile = where we are
        f.walking = moved > 0
        f.walk_phase += moved * 0.2       # ~one bob cadence per tile

    def draw(self, surface: pygame.Surface) -> None:
        for f in self.followers:
            f.draw(surface)
