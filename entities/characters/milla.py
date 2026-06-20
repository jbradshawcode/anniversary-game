"""Milla — blonde woman behind the Salutation bar; her own sprite, wine top."""
import pygame
from config import TILE_SIZE
from ..humanoid import Humanoid, Palette

_SKIN     = (238, 205, 178)
_SKIN_SH  = (214, 178, 150)
_HAIR     = (224, 188, 104)
_HAIR_LT  = (244, 214, 140)
_HAIR_DK  = (188, 150,  78)
_TEE      = (125,  55,  65)
_TEE_SH   = ( 98,  42,  50)
_EYE      = ( 80, 120, 150)
_LASH     = ( 40,  28,  20)
_LIP      = (200, 120, 120)
_CHEEK    = (235, 180, 165)
_GLINT    = (245, 248, 240)

_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TEE, tee_sh=_TEE_SH)


class Milla(Humanoid):
    _palette = _PALETTE
    name = "Milla"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["What'll it be?"]

    def draw(self, screen):
        # Her tile is the order spot in FRONT of the bar (so you can face her to
        # order), but she's drawn ~2 tiles back, behind the counter.
        oy = self.y
        self.y = oy - 2 * TILE_SIZE
        super().draw(screen)
        self.y = oy

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        # blonde fringe + shoulder-length sides
        r(-7, -15, 14, 5, _HAIR)
        r(-4, -16,  5, 2, _HAIR)
        r( 4, -16,  3, 2, _HAIR)
        r(-3, -16,  3, 1, _HAIR_LT)
        r( 5, -16,  1, 1, _HAIR_LT)

        r(-8, -11, 3, 8, _HAIR)
        r( 5, -11, 3, 8, _HAIR)
        r(-9, -10, 2, 4, _HAIR)
        r( 7, -10, 2, 4, _HAIR)
        r(-8, -11, 1, 6, _HAIR_DK)
        r( 7, -11, 1, 6, _HAIR_DK)

        pygame.draw.ellipse(screen, _SKIN, (px - 5, py - 11, 10, 10))

        r(-5, -11, 4, 2, _HAIR)
        r( 1, -11, 4, 2, _HAIR)
        r(-3, -11, 2, 1, _HAIR_LT)
        r( 2, -11, 2, 1, _HAIR_LT)

        r(-4, -8, 3, 1, _LASH)
        r( 1, -8, 3, 1, _LASH)
        r(-4, -7, 3, 2, _EYE)
        r(-4, -7, 1, 1, _GLINT)
        r( 1, -7, 3, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r(-4, -5, 2, 1, _CHEEK)
        r( 2, -5, 2, 1, _CHEEK)

        r(-1, -4, 2, 1, _LIP)
