"""Bailey — big round curly afro, round glasses, black/white striped tee."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (205, 165, 125)
_SKIN_SH  = (180, 140, 105)
_HAIR     = ( 78,  52,  32)
_HAIR_LT  = (112,  78,  46)
_HAIR_DK  = ( 52,  34,  20)
_TEE      = (238, 238, 238)
_TEE_SH   = (205, 205, 205)
_STRIPE   = ( 40,  40,  46)         # the dark bands of the striped tee
_EYE      = ( 50,  35,  25)
_LIP      = (190, 120, 110)
_CHEEK    = (210, 155, 130)
_GLINT    = (240, 245, 235)
_FRAME    = ( 70,  64,  78)         # light enough to read as thin wire, not a blob

_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TEE, tee_sh=_TEE_SH)


class Bailey(Humanoid):
    _palette = _PALETTE
    name = "Bailey"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Heyyy!"]

    @staticmethod
    def _glasses_down(screen, px, py):
        pygame.draw.rect(screen, _FRAME, (px - 4, py - 8, 3, 3), 1)   # hollow lenses
        pygame.draw.rect(screen, _FRAME, (px + 1, py - 8, 3, 3), 1)
        pygame.draw.rect(screen, _FRAME, (px - 1, py - 7, 2, 1))      # bridge

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + x, py + y, w, h))

        el(-12, -20, 24, 17, _HAIR)               # big round afro
        el(-10, -15, 8, 9, _HAIR)                 # rounded lobes (not drooping)
        el(2, -15, 8, 9, _HAIR)
        el(-8, -19, 16, 6, _HAIR_LT)              # top sheen
        r(-6, -18, 2, 2, _HAIR_DK)
        r(4, -18, 2, 2, _HAIR_DK)
        r(-9, -11, 2, 3, _HAIR_DK)
        r(7, -11, 2, 3, _HAIR_DK)

        el(-5, -11, 10, 10, _SKIN)
        r(-5, -11, 10, 2, _HAIR)                  # hairline over brow

        r(-3, -7, 1, 1, _EYE)                     # small eyes, clear behind glasses
        r(2, -7, 1, 1, _EYE)
        self._glasses_down(screen, px, py)
        r(-4, -4, 1, 1, _CHEEK)
        r(3, -4, 1, 1, _CHEEK)
        r(-1, -3, 2, 1, _LIP)

    def _draw_head_side(self, screen, px, py, flip):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + (-(x + w) if flip else x), py + y, w, h))

        el(-11, -20, 22, 17, _HAIR)               # round afro, turned
        el(-10, -15, 8, 9, _HAIR)
        el(-8, -19, 14, 6, _HAIR_LT)
        r(-9, -11, 2, 3, _HAIR_DK)

        el(-2, -12, 8, 10, _SKIN)
        r(-2, -10, 2, 6, _SKIN_SH)
        el(-3, -13, 8, 4, _HAIR)                  # curls over brow

        r(1, -7, 1, 1, _EYE)
        pygame.draw.rect(screen, _FRAME,
                         (px + (-(1 + 3) if flip else 1), py - 8, 3, 3), 1)   # front lens
        r(-1, -7, 1, 1, _FRAME)                   # temple to the back

        r(5, -7, 1, 2, _SKIN)
        r(6, -6, 1, 1, _SKIN_SH)
        r(3, -4, 2, 1, _CHEEK)
        r(2, -3, 3, 1, _LIP)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        def el(x, y, w, h, c):
            pygame.draw.ellipse(screen, c, (px + x, py + y, w, h))

        el(-12, -20, 24, 17, _HAIR)               # round afro from behind
        el(-8, -19, 16, 6, _HAIR_LT)
        r(-6, -10, 3, 4, _HAIR_DK)
        r(5, -10, 3, 4, _HAIR_DK)
        r(-4, -16, 2, 2, _HAIR_DK)
        r(2, -15, 2, 2, _HAIR_DK)

    def _draw_body(self, screen, px, py):
        # horizontal black/white striped tee
        p = self._palette
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-2, -1, 4, 2, p.skin)                   # neck
        bands = (_TEE, _STRIPE, _TEE, _STRIPE, _TEE)
        for i, c in enumerate(bands):             # striped torso
            r(-5, 1 + i, 10, 1, c)
        r(-7, 1, 3, 1, _TEE)                      # striped sleeve caps
        r(-7, 2, 3, 1, _STRIPE)
        r(4, 1, 3, 1, _TEE)
        r(4, 2, 3, 1, _STRIPE)
        r(-7, 3, 3, 2, p.skin)                    # forearms
        r(4, 3, 3, 2, p.skin)
        r(-4, 6, 8, 1, p.short_sh)                # shorts + legs + shoes (standard)
        r(-4, 7, 3, 3, p.short)
        r(1, 7, 3, 3, p.short)
        r(-4, 7, 3, 1, p.short_sh)
        r(1, 7, 3, 1, p.short_sh)
        r(-4, 10, 3, 3, p.skin)
        r(1, 10, 3, 3, p.skin)
        r(-4, 10, 1, 3, p.skin_sh)
        r(1, 10, 1, 3, p.skin_sh)
        r(-5, 13, 5, 2, p.shoe)
        r(1, 13, 5, 2, p.shoe)
        r(-5, 14, 5, 1, p.sole)
        r(1, 14, 5, 1, p.sole)
