"""Wallace — short neat black hair, glasses, wide friendly face, teal tee."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (212, 176, 140)
_SKIN_SH  = (186, 152, 120)
_HAIR     = ( 34,  32,  40)
_HAIR_LT  = ( 60,  56,  68)
_HAIR_DK  = ( 20,  18,  26)
_TEE      = ( 66, 118, 118)
_TEE_SH   = ( 48,  92,  92)
_EYE      = ( 44,  34,  30)
_LIP      = (182, 122, 112)
_CHEEK    = (208, 162, 132)
_GLINT    = (240, 244, 242)
_FRAME    = ( 98,  98, 114)         # light enough to read as thin wire, not a mask

_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TEE, tee_sh=_TEE_SH)


class Wallace(Humanoid):
    _palette = _PALETTE
    name = "Wallace"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Helloooo what's up"]

    @staticmethod
    def _glasses_down(screen, px, py):
        pygame.draw.rect(screen, _FRAME, (px - 5, py - 8, 3, 3), 1)   # hollow lenses, clear gap
        pygame.draw.rect(screen, _FRAME, (px + 2, py - 8, 3, 3), 1)
        pygame.draw.rect(screen, _FRAME, (px - 2, py - 7, 4, 1))      # bridge
        pygame.draw.rect(screen, _FRAME, (px - 6, py - 7, 1, 1))      # temples
        pygame.draw.rect(screen, _FRAME, (px + 5, py - 7, 1, 1))

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + x, py + y, w, h))

        r(-7, -15, 14, 4, _HAIR)                  # short neat crop (wide)
        r(-4, -16, 8, 1, _HAIR)
        r(-7, -13, 2, 4, _HAIR)
        r(5, -13, 2, 4, _HAIR)
        r(-3, -15, 5, 1, _HAIR_LT)

        el(-6, -11, 12, 10, _SKIN)                # wider face
        r(-6, -11, 12, 2, _HAIR)                  # hairline

        r(-4, -7, 1, 1, _EYE)                     # small eyes, clear behind glasses
        r(3, -7, 1, 1, _EYE)
        self._glasses_down(screen, px, py)
        r(-4, -4, 1, 1, _CHEEK)
        r(3, -4, 1, 1, _CHEEK)
        r(-1, -3, 2, 1, _LIP)

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        r(-6, -15, 13, 4, _HAIR)                  # short crop, turned
        r(-3, -16, 5, 1, _HAIR)
        r(-6, -12, 3, 8, _HAIR)
        r(-6, -12, 1, 6, _HAIR_DK)

        el(-3, -12, 9, 10, _SKIN)                 # wider profile
        r(-3, -10, 2, 6, _SKIN_SH)
        r(-3, -12, 8, 2, _HAIR)
        r(5, -12, 1, 3, _HAIR)

        r(1, -7, 1, 1, _EYE)
        pygame.draw.rect(screen, _FRAME,
                         (px + (-(1 + 3) if flip else 1), py - 8, 3, 3), 1)   # front lens
        r(-1, -7, 1, 1, _FRAME)                   # temple to the back

        r(6, -7, 1, 2, _SKIN)
        r(7, -6, 1, 1, _SKIN_SH)
        r(3, -4, 2, 1, _CHEEK)
        r(2, -3, 3, 1, _LIP)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -15, 14, 4, _HAIR)
        r(-4, -16, 8, 1, _HAIR)
        r(-8, -11, 16, 9, _HAIR)
        r(-8, -11, 2, 8, _HAIR_DK)
        r(6, -11, 2, 8, _HAIR_DK)
        r(-2, -11, 4, 6, _HAIR_LT)
