"""Matt — round afro, beard, green tee, friendly smile."""
import pygame
from ..humanoid import Humanoid, Palette

_SKIN     = (165, 120,  80)
_SKIN_SH  = (140, 100,  65)
_HAIR     = ( 70,  45,  25)
_HAIR_LT  = (100,  65,  38)
_HAIR_DK  = ( 45,  28,  15)
_BEARD    = ( 65,  42,  25)
_TEETH    = (240, 235, 225)
_TEE      = ( 75, 160, 100)
_TEE_SH   = ( 55, 130,  75)
_EYE      = ( 50,  35,  25)
_LASH     = ( 25,  12,   3)
_GLINT    = (240, 245, 235)

_PALETTE = Palette(
    skin=_SKIN, skin_sh=_SKIN_SH,
    tee=_TEE, tee_sh=_TEE_SH,
)


class Matt(Humanoid):
    _palette = _PALETTE
    name = "Matt"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.interaction_text = ["Hey! Great to see you out here!"]

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        pygame.draw.ellipse(screen, _HAIR, (px - 11, py - 17, 22, 16))
        pygame.draw.ellipse(screen, _HAIR_LT, (px - 6, py - 16, 10, 5))
        r(-10, -11, 2, 5, _HAIR_DK)
        r(  8, -11, 2, 5, _HAIR_DK)

        pygame.draw.ellipse(screen, _SKIN, (px - 5, py - 11, 10, 10))

        r(-5, -11, 10, 2, _HAIR)
        r(-3, -11,  4, 1, _HAIR_LT)

        r(-4, -8, 3, 1, _LASH)
        r( 1, -8, 3, 1, _LASH)
        r(-4, -7, 3, 2, _EYE)
        r(-4, -7, 1, 1, _GLINT)
        r( 1, -7, 3, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r(-4, -5, 2, 3, _BEARD)
        r( 2, -5, 2, 3, _BEARD)
        r(-3, -3, 6, 2, _BEARD)

        r(-2, -4, 4, 1, _TEETH)
