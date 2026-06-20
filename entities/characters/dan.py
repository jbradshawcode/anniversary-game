"""Dan — organizes the 3v3; tall messy quiff, light stubble, red tee."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (205, 165, 125)
_SKIN_SH  = (180, 140, 105)
_STUBBLE  = (195, 180, 155)
_HAIR     = (140, 120,  60)
_HAIR_LT  = (175, 155,  85)
_HAIR_DK  = (105,  88,  40)
_TEE      = (205,  55,  45)
_TEE_SH   = (165,  38,  32)
_EYE      = ( 50,  35,  25)
_LASH     = ( 40,  28,  15)
_LIP      = (190, 125, 110)
_CHEEK    = (210, 155, 130)
_GLINT    = (240, 245, 235)

_PALETTE = Palette(
    skin=_SKIN, skin_sh=_SKIN_SH,
    tee=_TEE, tee_sh=_TEE_SH,
)


class Dan(Humanoid):
    _palette = _PALETTE
    name = "Dan"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["What's uuuup"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-6, -16, 12, 6, _HAIR)
        r(-3, -17,  6, 2, _HAIR)
        r(-7, -14,  2, 3, _HAIR)
        r( 5, -15,  2, 3, _HAIR)
        r(-2, -17,  4, 2, _HAIR_LT)
        r(-5, -16,  3, 3, _HAIR_LT)
        r( 3, -15,  2, 2, _HAIR_LT)
        r(-6, -14,  1, 4, _HAIR_DK)
        r( 5, -13,  1, 3, _HAIR_DK)

        r(-7, -11, 2, 4, _HAIR)
        r( 5, -11, 2, 4, _HAIR)

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

        r(-4, -4, 2, 1, _STUBBLE)
        r( 2, -4, 2, 1, _STUBBLE)
        r(-3, -3, 6, 1, _STUBBLE)
        r(-2, -2, 4, 1, _STUBBLE)

        r(-1, -4, 2, 1, _LIP)

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        r(-6, -15, 12, 4, _HAIR)              # quiff stacked up and swept forward
        r(-6, -18,  5, 4, _HAIR)
        r(-3, -19,  6, 3, _HAIR)
        r( 1, -20,  5, 3, _HAIR)
        r( 0, -19,  3, 2, _HAIR_LT)
        r(-4, -17,  3, 2, _HAIR_LT)
        r(-6, -12,  4, 8, _HAIR)
        r(-6, -12,  1, 6, _HAIR_DK)

        el(-2, -12, 8, 10, _SKIN)             # face
        r(-2, -10, 2, 6, _SKIN_SH)

        r(-2, -12, 7, 2, _HAIR)               # fringe
        r( 0, -12, 3, 1, _HAIR_LT)
        r( 5, -12, 1, 3, _HAIR)

        r( 1, -8, 3, 1, _LASH)                # eye
        r( 1, -7, 2, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r( 5, -7, 1, 2, _SKIN)                # nose
        r( 6, -6, 1, 1, _SKIN_SH)

        r( 2, -4, 3, 1, _LIP)                 # mouth + stubble
        r( 3, -5, 2, 1, _STUBBLE)
        r( 2, -3, 3, 1, _STUBBLE)
        r( 0, -3, 2, 1, _STUBBLE)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-6, -16, 12, 5, _HAIR)
        r(-3, -19,  7, 4, _HAIR)              # quiff from behind
        r(-1, -20,  5, 2, _HAIR_LT)
        r(-7, -11, 14, 9, _HAIR)
        r(-8, -10,  2, 4, _HAIR)
        r( 6, -10,  2, 4, _HAIR)
        r(-2, -11,  5, 6, _HAIR_LT)
        r(-7, -11,  2, 6, _HAIR_DK)
        r( 5, -11,  2, 6, _HAIR_DK)
