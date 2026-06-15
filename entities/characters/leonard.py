"""Leonard — slightly taller build, messy brown hair, white tee."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (200, 160, 120)
_SKIN_SH  = (175, 138, 100)
_HAIR     = ( 90,  58,  30)
_HAIR_LT  = (125,  85,  48)
_HAIR_DK  = ( 60,  35,  16)
_TEE      = (238, 236, 230)
_TEE_SH   = (210, 208, 200)
_EYE      = ( 50,  35,  25)
_LASH     = ( 25,  12,   3)
_LIP      = (190, 120, 110)
_CHEEK    = (210, 155, 130)
_SHOE     = ( 60,  40,  25)
_SOLE     = ( 42,  28,  16)
_GLINT    = (240, 245, 235)

_PALETTE = Palette(
    skin=_SKIN, skin_sh=_SKIN_SH,
    tee=_TEE, tee_sh=_TEE_SH,
    shoe=_SHOE, sole=_SOLE,
)


class Leonard(Humanoid):
    _palette = _PALETTE
    name = "Leonard"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Hello!", "I am tall and also German"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -16, 14, 5, _HAIR)
        r(-4, -17,  4, 2, _HAIR)
        r( 2, -17,  4, 2, _HAIR)
        r(-1, -18,  3, 2, _HAIR)
        r(-3, -17,  3, 1, _HAIR_LT)
        r( 3, -17,  2, 1, _HAIR_LT)
        r(-1, -18,  2, 1, _HAIR_LT)

        r(-7, -11, 2, 5, _HAIR)
        r( 5, -11, 2, 5, _HAIR)
        r(-7, -11, 1, 3, _HAIR_DK)
        r( 6, -11, 1, 3, _HAIR_DK)

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

        r(-7, -16, 13, 5, _HAIR)              # messy back + tuft up top
        r(-3, -18,  4, 3, _HAIR)
        r( 1, -17,  3, 2, _HAIR)
        r(-2, -18,  2, 1, _HAIR_LT)
        r(-5, -16,  3, 1, _HAIR_LT)
        r(-7, -12,  3, 9, _HAIR)
        r(-7, -12,  1, 6, _HAIR_DK)
        r(-7, -4,  2, 2, _HAIR)

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

        r( 3, -5, 2, 1, _CHEEK)               # cheek + lip
        r( 2, -4, 3, 1, _LIP)
        r( 2, -3, 2, 1, _SKIN_SH)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -16, 14, 5, _HAIR)
        r(-3, -18,  5, 3, _HAIR)              # messy tuft
        r(-8, -11, 16, 9, _HAIR)
        r(-9, -10,  2, 4, _HAIR)
        r( 7, -10,  2, 4, _HAIR)
        r(-2, -11,  5, 7, _HAIR_LT)
        r(-8, -11,  2, 7, _HAIR_DK)
        r( 6, -11,  2, 7, _HAIR_DK)

    def _draw_body(self, screen, px, py):
        # taller torso + longer legs than the standard Humanoid body
        p = self._palette
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-2, -1, 4, 2, p.skin)
        r(-7,  1, 3, 3, p.tee)
        r( 4,  1, 3, 3, p.tee)
        r(-7,  4, 3, 2, p.skin)
        r( 4,  4, 3, 2, p.skin)
        r(-5,  1, 10, 7, p.tee)
        r(-5,  1, 1, 7, p.tee_sh)
        r(-2,  1, 4, 1, p.tee_sh)
        r(-4,  8, 8, 1, p.short_sh)
        r(-4,  9, 3, 3, p.short)
        r( 1,  9, 3, 3, p.short)
        r(-4,  9, 3, 1, p.short_sh)
        r( 1,  9, 3, 1, p.short_sh)
        r(-4, 12, 3, 3, p.skin)
        r( 1, 12, 3, 3, p.skin)
        r(-4, 12, 1, 3, p.skin_sh)
        r( 1, 12, 1, 3, p.skin_sh)
        r(-5, 15, 5, 2, p.shoe)
        r( 1, 15, 5, 2, p.shoe)
        r(-5, 16, 5, 1, p.sole)
        r( 1, 16, 5, 1, p.sole)
