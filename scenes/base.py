"""Base scene class — shared by all scenes"""
import pygame
from config import (
    SCENE_CONFIGS, TILE_SIZE, MAP_COLS, MAP_ROWS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
)
from systems.factory import ObjectFactory


class Scene:
    # Static, scene-defined geometry — subclasses override these instead of
    # carving the tile map by hand:
    #   static_blocked — tiles that are not walkable (walls, furniture, voids)
    #   walls          — blocked edges between two adjacent tiles (fences)
    static_blocked = ()
    walls = frozenset()

    def __init__(self, config_key: str):
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
        self._build_tile_map()

        self._world_surface = None

    def _build_tile_map(self):
        """(Re)derive the walkability grid from bounds, static scenery and the
        current object list. Call after mutating self.objects so vacated tiles
        (e.g. NPCs that joined the follower party) become walkable again."""
        col0, col1 = self.walkable_cols
        row0, row1 = self.walkable_rows
        self._tile_map = [[0] * self._map_cols for _ in range(MAP_ROWS)]
        for row in range(row0, row1 + 1):
            for col in range(col0, col1 + 1):
                self._tile_map[row][col] = 1

        # Static scenery that isn't walkable (declared by the subclass)
        for tx, ty in self.static_blocked:
            if 0 <= ty < MAP_ROWS and 0 <= tx < self._map_cols:
                self._tile_map[ty][tx] = 0

        for obj in self.objects:
            for tx, ty in obj.blocked_tiles():
                if 0 <= ty < MAP_ROWS and 0 <= tx < self._map_cols:
                    self._tile_map[ty][tx] = 0

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
        if tile_x < 0 or tile_x >= self._map_cols or tile_y < 0 or tile_y >= MAP_ROWS:
            return False
        return self._tile_map[tile_y][tile_x] == 1

    def has_wall(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        return ((from_x, from_y), (to_x, to_y)) in self.walls

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
