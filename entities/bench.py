"""Bench sprite — multi-tile wooden bench along a wall"""
import pygame
from .base import GameObject
from config import TILE_SIZE

_SEAT = (148, 108,  58)
_LITE = (168, 128,  72)
_EDGE = ( 88,  60,  32)


class Bench(GameObject):
    def __init__(self, tile_x: int, tile_y: int, height: int = 5):
        super().__init__(tile_x, tile_y)
        self._height = height
        # interaction handled in on_interact so "Yes" actually seats the player

    def on_interact(self, game) -> None:
        def chose(label):
            if label == "Yes":
                game.player.sit(self)
        game.dialogue.start(
            [{"text": "Sit on the bench?",
              "choices": {"Yes": ["You take a seat."], "No": []}}],
            on_choice=chose)

    def blocked_tiles(self) -> list:
        return [(self.tile_x, self.tile_y + i) for i in range(self._height)]

    def occupies(self, tx: int, ty: int) -> bool:
        return tx == self.tile_x and self.tile_y <= ty < self.tile_y + self._height

    def draw(self, screen: pygame.Surface):
        bx = self.tile_x * TILE_SIZE + 6
        by = self.tile_y * TILE_SIZE + 2
        bw = TILE_SIZE - 12
        bh = self._height * TILE_SIZE - 4

        pygame.draw.rect(screen, _SEAT, (bx, by, bw, bh))
        pygame.draw.rect(screen, _LITE, (bx, by, bw, max(bh // 6, 3)))

        for sy in range(by + TILE_SIZE, by + bh, TILE_SIZE):
            pygame.draw.line(screen, _EDGE, (bx + 1, sy), (bx + bw - 2, sy), 1)

        pygame.draw.rect(screen, _EDGE, (bx, by, bw, bh), 1)
