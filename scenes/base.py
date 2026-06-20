"""Base scene class — shared by all scenes"""
import pygame
from config import (
    SCENE_CONFIGS, TILE_SIZE, MAP_COLS, MAP_ROWS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)
from systems.factory import ObjectFactory
from systems.tilemap import TileMap


class Scene:
    # Static, scene-defined geometry — subclasses override these instead of
    # carving the tile map by hand:
    #   static_blocked — tiles that are not walkable (walls, furniture, voids)
    #   walls          — blocked edges between two adjacent tiles (fences)
    static_blocked = ()
    walls = frozenset()

    def __init__(self, config_key: str):
        self._config_key = config_key
        config = SCENE_CONFIGS[config_key]
        self.scene_id  = config['id']
        self.exits         = config.get('exits', {})
        self.entry_points  = config.get('entry_points', {})

        self._map_cols = config.get('map_cols', MAP_COLS)

        # Tile bounds (inclusive)
        self.walkable_cols = config['walkable_cols']
        self.walkable_rows = config['walkable_rows']
        col0, col1 = self.walkable_cols
        row0, row1 = self.walkable_rows

        self.objects = ObjectFactory.create_scene_objects(config_key)
        self._extra_blocked = set()        # ad-hoc blockers (e.g. seated followers)
        self._tile_map = TileMap(
            self.walkable_cols, self.walkable_rows,
            self._map_cols, MAP_ROWS,
            self.static_blocked, self.walls,
        )
        self._refresh_blockers()

        self._world_surface = None

    def _refresh_blockers(self):
        """Re-derive the dynamic blocker layer from the current object list.
        Call after mutating self.objects (e.g. NPCs that joined the follower
        party) so vacated tiles become walkable again."""
        blocked = list(self._extra_blocked)
        for obj in self.objects:
            blocked.extend(obj.blocked_tiles())
        self._tile_map.set_blockers(blocked)

    def sync_blockers(self) -> None:
        """Re-derive blockers from objects' live tiles (NPCs that moved in a
        cutscene collide at their current position, not their spawn)."""
        self._refresh_blockers()

    def add_blockers(self, tiles) -> None:
        """Block extra tiles (e.g. seated followers) so the player can't walk
        through them. Cleared on scene entry so they don't leak across visits."""
        self._extra_blocked.update((int(x), int(y)) for x, y in tiles)
        self._refresh_blockers()

    def clear_extra_blockers(self) -> None:
        if self._extra_blocked:
            self._extra_blocked.clear()
            self._refresh_blockers()

    def repopulate(self) -> None:
        """Recreate this scene's objects from config — crew who left as followers in
        a previous chapter come back as NPCs for a fresh one. Resets ad-hoc blockers."""
        self.objects = ObjectFactory.create_scene_objects(self._config_key)
        self._extra_blocked.clear()
        self._refresh_blockers()

    def remove_named(self, names) -> None:
        """Drop objects whose display name is in `names` (e.g. crew absent a chapter)."""
        if not names:
            return
        self.objects = [o for o in self.objects if o.name not in names]
        self._refresh_blockers()

    def despawn(self, types) -> None:
        """Remove objects of the given type(s) and rebuild walkability. Owns the
        invariant that mutating the object list requires a tile-map rebuild, so
        callers never touch the grid directly."""
        self.objects = [o for o in self.objects if not isinstance(o, types)]
        self._refresh_blockers()

    @property
    def world_width(self) -> int:
        return self._map_cols * TILE_SIZE

    @property
    def scrolling(self) -> bool:
        return self._map_cols > MAP_COLS

    def get_world_surface(self) -> pygame.Surface:
        if self._world_surface is None:
            self._world_surface = pygame.Surface((self.world_width, SCREEN_HEIGHT))
        return self._world_surface

    def get_camera_x(self, player_x: float) -> int:
        max_cam = self.world_width - SCREEN_WIDTH
        if max_cam <= 0:
            return 0
        cam_x = int(player_x) - SCREEN_WIDTH // 2
        return max(0, min(cam_x, max_cam))

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        return self._tile_map.is_walkable(tile_x, tile_y)

    def has_wall(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        return self._tile_map.has_wall(from_x, from_y, to_x, to_y)

    def enter(self, player):
        """Hook called when this scene becomes active (no-op by default)."""
        pass

    def exit(self):
        """Hook called when leaving this scene (no-op by default)."""
        pass

    # Scenes that drive their own real-time input (e.g. the volleyball minigame)
    # set wants_raw_input = True; the main loop then routes discrete actions to
    # handle_action() and the held movement vector to handle_held(), and skips
    # the tile-movement path. Default scenes are unaffected.
    wants_raw_input = False

    def handle_action(self, action) -> bool:
        """One-shot action press; return True if consumed."""
        return False

    def handle_held(self, vec) -> None:
        """Per-frame held movement vector (dx, dy)."""
        pass

    def update(self, dt: float):
        for obj in self.objects:
            obj.update(dt)

    def _draw_objects(self, screen: pygame.Surface):
        for obj in self.objects:
            obj.draw(screen)

    def draw_overlay(self, screen: pygame.Surface):
        pass

    def draw(self, screen: pygame.Surface):
        # Default fallback; every concrete scene overrides this with its own art.
        screen.fill((0, 0, 0))
        self._draw_objects(screen)
