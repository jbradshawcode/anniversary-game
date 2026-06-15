"""Rock environment object"""
import pygame
from .base import GameObject

_COLOR = (128, 128, 128)
_W     = 20
_H     = 15
_OX    = -10
_OY    = 0


class Rock(GameObject):
    def draw(self, screen: pygame.Surface):
        pygame.draw.ellipse(screen, _COLOR, (self.x + _OX, self.y + _OY, _W, _H))
