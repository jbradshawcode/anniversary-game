"""James — one of the crew; wavy reddish-brown hair."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (200, 160, 120)
_SKIN_SH  = (175, 135, 100)
_HAIR     = (145,  75,  40)
_HAIR_LT  = (185, 115,  65)
_HAIR_DK  = (100,  45,  20)
_TEE      = (238, 236, 230)
_TEE_SH   = (210, 208, 200)
_EYE      = ( 50,  35,  25)
_LASH     = ( 25,  12,   3)
_LIP      = (195, 120, 110)
_CHEEK    = (210, 155, 130)
_GLINT    = (240, 245, 235)

_PALETTE = Palette(
    skin=_SKIN, skin_sh=_SKIN_SH,
    tee=_TEE, tee_sh=_TEE_SH,
)


class James(Humanoid):
    _palette = _PALETTE
    name = "James"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Heyyy there beautiful lady.",
                                 "(James was not actually brave enough to say this)"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -15, 14, 5, _HAIR)
        r(-4, -16,  5, 2, _HAIR)
        r( 4, -16,  3, 2, _HAIR)
        r(-3, -16,  3, 1, _HAIR_LT)
        r( 5, -16,  1, 1, _HAIR_LT)

        r(-8, -11, 3, 7, _HAIR)
        r( 5, -11, 3, 7, _HAIR)
        r(-9, -10, 2, 3, _HAIR)
        r( 7, -10, 2, 3, _HAIR)
        r(-8, -11, 1, 5, _HAIR_DK)
        r( 7, -11, 1, 5, _HAIR_DK)

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

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        r(-7, -15, 13, 4, _HAIR)              # back + top, wavy tail
        r(-5, -15, 4, 2, _HAIR_LT)
        r(-7, -12, 4, 9, _HAIR)
        r(-5, -12, 2, 6, _HAIR_LT)
        r(-8, -10, 2, 4, _HAIR)
        r(-8, -6, 2, 3, _HAIR)
        r(-7, -3, 2, 2, _HAIR_DK)

        el(-2, -12, 8, 10, _SKIN)             # face, turned right
        r(-2, -10, 2, 6, _SKIN_SH)

        r(-2, -12, 8, 2, _HAIR)               # fringe + front tuft
        r( 0, -12, 3, 1, _HAIR_LT)
        r( 5, -12, 2, 4, _HAIR)

        r( 1, -8, 3, 1, _LASH)                # eye
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

        r(-7, -16, 14, 5, _HAIR)
        r(-4, -16,  5, 2, _HAIR)
        r(-8, -11, 16, 9, _HAIR)
        r(-9, -10,  2, 4, _HAIR)
        r( 7, -10,  2, 4, _HAIR)
        r(-5, -15,  4, 2, _HAIR_LT)
        r(-2, -11,  5, 7, _HAIR_LT)
        r(-8, -11,  2, 7, _HAIR_DK)
        r( 6, -11,  2, 7, _HAIR_DK)
