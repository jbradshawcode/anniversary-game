"""Tree environment object"""
import pygame
from .base import GameObject

_TRUNK   = (101, 67, 33)
_LEAF    = (34, 139, 34)
_TRUNK_W = 10
_TRUNK_H = 30
_LEAF_R  = 20
_LEAF_OY = -10


class Tree(GameObject):
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, _TRUNK,
                         (self.x - _TRUNK_W // 2, self.y, _TRUNK_W, _TRUNK_H))
        pygame.draw.circle(screen, _LEAF, (self.x, self.y + _LEAF_OY), _LEAF_R)
