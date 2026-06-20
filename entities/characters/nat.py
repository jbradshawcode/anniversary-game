"""Nat — voluminous curly bob, golden eyes, deep purple tee."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (165, 120,  80)
_SKIN_SH  = (140, 100,  65)
_HAIR     = ( 55,  35,  20)
_HAIR_LT  = ( 85,  58,  35)
_HAIR_DK  = ( 35,  20,  10)
_TEE      = ( 80,  30, 110)
_TEE_SH   = ( 58,  20,  82)
_EYE      = (195, 155,  45)
_LASH     = ( 25,  12,   3)
_GLINT    = (240, 245, 235)
_LIP      = (200, 110, 120)
_CHEEK    = (175, 125,  90)
_SHOE     = ( 55,  35,  22)
_SOLE     = ( 38,  25,  15)

_PALETTE = Palette(
    skin=_SKIN, skin_sh=_SKIN_SH,
    tee=_TEE, tee_sh=_TEE_SH,
    shoe=_SHOE, sole=_SOLE,
)


class Nat(Humanoid):
    _palette = _PALETTE
    name = "Nat"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Dawg I'm getting changed, can I have a minute?"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        pygame.draw.ellipse(screen, _HAIR, (px - 9, py - 17, 18, 13))
        pygame.draw.ellipse(screen, _HAIR_LT, (px - 5, py - 16, 8, 4))

        r(-8, -11, 3, 10, _HAIR)
        r(-9, -10, 2,  6, _HAIR)
        r(-8, -11, 1,  8, _HAIR_DK)
        r(-7,  -8, 1,  3, _HAIR_LT)
        r(-9,  -7, 1,  2, _HAIR_LT)

        r( 5, -11, 3, 10, _HAIR)
        r( 7, -10, 2,  6, _HAIR)
        r( 7, -11, 1,  8, _HAIR_DK)
        r( 6,  -8, 1,  3, _HAIR_LT)
        r( 8,  -7, 1,  2, _HAIR_LT)

        pygame.draw.ellipse(screen, _SKIN, (px - 5, py - 11, 10, 10))

        r(-5, -11, 10, 2, _HAIR)
        r(-3, -11,  4, 1, _HAIR_LT)

        r(-4, -8, 3, 1, _LASH)
        r( 1, -8, 3, 1, _LASH)
        r(-4, -7, 3, 2, _EYE)
        r(-4, -7, 1, 1, _GLINT)
        r( 1, -7, 3, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r(-4, -5, 2, 1, _CHEEK)
        r( 2, -5, 2, 1, _CHEEK)

        r(-1, -4, 2, 1, _LIP)

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        el(-9, -17, 17, 14, _HAIR)            # voluminous bob mass
        el(-7, -16,  8,  4, _HAIR_LT)
        r(-9, -8, 4, 6, _HAIR)                # length down the back
        r(-9, -8, 1, 6, _HAIR_DK)
        r(-7, -4, 3, 3, _HAIR)
        r(-6, -2, 2, 2, _HAIR_LT)

        el(-2, -12, 8, 10, _SKIN)             # face
        r(-2, -10, 2, 6, _SKIN_SH)
        el(-3, -13, 8, 4, _HAIR)              # hairline
        r( 0, -13, 3, 1, _HAIR_LT)
        r( 5, -12, 2, 4, _HAIR)               # front curl

        r( 1, -8, 3, 1, _LASH)                # eye (golden)
        r( 1, -7, 2, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r( 5, -7, 1, 2, _SKIN)                # nose
        r( 6, -6, 1, 1, _SKIN_SH)

        r( 3, -5, 2, 1, _CHEEK)               # cheek + lip
        r( 2, -4, 3, 1, _LIP)
        r( 2, -3, 2, 1, _SKIN_SH)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + x, py + y, w, h))

        el(-9, -17, 18, 14, _HAIR)
        el(-5, -16,  8,  4, _HAIR_LT)
        r(-9, -7, 3, 5, _HAIR)
        r( 6, -7, 3, 5, _HAIR)
        r(-9, -7, 1, 5, _HAIR_DK)
        r( 8, -7, 1, 5, _HAIR_DK)
