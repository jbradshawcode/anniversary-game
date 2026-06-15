"""Base class for all game objects"""
import pygame
from typing import List, Optional
from config import TILE_SIZE


class GameObject:
    name: Optional[str] = None       # character display name (None for scenery)

    def __init__(self, tile_x: int, tile_y: int, blocking: bool = True):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.x = tile_x * TILE_SIZE + TILE_SIZE // 2
        self.y = tile_y * TILE_SIZE + TILE_SIZE // 2
        self.blocking = blocking
        self.interaction_text: Optional[List[str]] = None

    def blocked_tiles(self) -> list:
        if self.blocking:
            return [(self.tile_x, self.tile_y)]
        return []

    def occupies(self, tx: int, ty: int) -> bool:
        return tx == self.tile_x and ty == self.tile_y

    def update(self, dt: float):
        pass

    def draw(self, screen: pygame.Surface):
        pass
