"""Mayu — chin-length brown bob with a fringe, fair skin, olive hoodie."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (236, 206, 182)
_SKIN_SH  = (214, 182, 158)
_HAIR     = ( 70,  48,  35)
_HAIR_LT  = (102,  74,  54)
_HAIR_DK  = ( 48,  32,  22)
_TEE      = ( 96,  99,  72)
_TEE_SH   = ( 72,  76,  54)
_EYE      = ( 60,  42,  30)
_LASH     = ( 30,  18,   8)
_LIP      = (205, 120, 118)
_CHEEK    = (228, 170, 150)
_GLINT    = (245, 248, 240)

_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TEE, tee_sh=_TEE_SH)


class Mayu(Humanoid):
    _palette = _PALETTE
    name = "Mayu"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Oh, hi!"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + x, py + y, w, h))

        r(-7, -16, 14, 5, _HAIR)                  # rounded top
        r(-7, -16, 4, 2, _HAIR_LT)
        r(-8, -13, 3, 12, _HAIR)                  # straight bob, down to the jaw
        r(5, -13, 3, 12, _HAIR)
        r(-8, -13, 1, 11, _HAIR_DK)
        r(7, -13, 1, 11, _HAIR_DK)
        r(-6, -3, 2, 2, _HAIR)
        r(4, -3, 2, 2, _HAIR)

        el(-5, -11, 10, 10, _SKIN)

        r(-6, -12, 12, 3, _HAIR)                  # blunt fringe across the brow
        r(-5, -12, 4, 1, _HAIR_LT)
        r(0, -11, 3, 1, _HAIR_DK)

        r(-4, -8, 3, 1, _LASH)
        r(1, -8, 3, 1, _LASH)
        r(-4, -7, 3, 2, _EYE)
        r(-4, -7, 1, 1, _GLINT)
        r(1, -7, 3, 2, _EYE)
        r(1, -7, 1, 1, _GLINT)
        r(-4, -5, 2, 1, _CHEEK)
        r(2, -5, 2, 1, _CHEEK)
        r(-1, -4, 2, 1, _LIP)

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        r(-7, -16, 13, 5, _HAIR)                  # top
        r(-7, -16, 4, 2, _HAIR_LT)
        r(-7, -13, 3, 13, _HAIR)                  # bob length down the back
        r(-7, -13, 1, 12, _HAIR_DK)

        el(-2, -12, 8, 10, _SKIN)
        r(-2, -10, 2, 6, _SKIN_SH)

        r(-2, -12, 8, 3, _HAIR)                   # fringe sweeping to the front
        r(0, -12, 3, 1, _HAIR_LT)
        r(5, -12, 1, 4, _HAIR)

        r(1, -8, 3, 1, _LASH)
        r(1, -7, 2, 2, _EYE)
        r(1, -7, 1, 1, _GLINT)
        r(5, -7, 1, 2, _SKIN)
        r(6, -6, 1, 1, _SKIN_SH)
        r(3, -5, 2, 1, _CHEEK)
        r(2, -4, 3, 1, _LIP)
        r(2, -3, 2, 1, _SKIN_SH)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -16, 14, 5, _HAIR)
        r(-7, -16, 4, 2, _HAIR_LT)
        r(-8, -11, 16, 11, _HAIR)                 # bob from behind, to the nape
        r(-8, -11, 2, 10, _HAIR_DK)
        r(6, -11, 2, 10, _HAIR_DK)
        r(-1, -11, 2, 9, _HAIR_LT)                # centre parting hint
