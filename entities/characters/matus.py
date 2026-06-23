"""Matúš — the referee. Reddish stubble, dark sunglasses, tank top, whistle.

Blow the whistle (loud) when spoken to in the overworld; courtside he just blows
it lazily on each point (the match plays it at a lower volume).
"""
import pygame
from ..humanoid import Humanoid, Palette
from config import WHISTLE_VOLUME

_SKIN     = (210, 158, 120)
_SKIN_SH  = (182, 132,  98)
_HAIR     = (150,  92,  52)      # reddish-brown
_HAIR_LT  = (180, 118,  70)
_HAIR_DK  = (110,  64,  34)
_STUBBLE  = (158, 110,  82)
_SHADE    = ( 26,  28,  34)      # sunglasses
_SHADE_HI = ( 96, 102, 116)
_TANK     = ( 52,  56,  64)
_TANK_SH  = ( 38,  41,  48)
_MOUTH    = (170, 110, 100)
_WHISTLE  = (236, 232, 224)
_LANYARD  = (200,  70,  60)

_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TANK, tee_sh=_TANK_SH)


class Matus(Humanoid):
    _palette = _PALETTE
    name = "Matúš"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y)
        self.sit('left')                  # the ref watches the court from the right-wall bench
        self.interaction_text = ["FWEEEEEET!!",
                                 "I listen to lonely people music.",
                                 "Which means you all have to listen to lonely people music."]

    def interaction_lines(self, story):
        # once the Ch1 match is won, he's angling for the pub invite he won't get
        if story is not None and 'w1_won_vb' in story.flags:
            return ["(I'm pretty sure Matúš comes to the pub,",
                    "but we don't really want him there...)"]
        return self.interaction_text

    def on_interact(self, game) -> None:
        """Talking to the ref earns a deafening overworld whistle."""
        if getattr(game, 'sfx', None) is not None:
            game.sfx.play('whistle_loud', WHISTLE_VOLUME)

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        pygame.draw.ellipse(screen, _SKIN, (px - 5, py - 11, 10, 10))   # face
        pygame.draw.ellipse(screen, _HAIR, (px - 6, py - 14, 12, 7))    # short messy cap
        pygame.draw.ellipse(screen, _HAIR_LT, (px - 4, py - 13, 6, 3))
        r(-6, -9, 2, 3, _HAIR)                                          # sideburns
        r( 4, -9, 2, 3, _HAIR)
        r(-6, -8, 1, 2, _HAIR_DK)

        r(-5, -8, 10, 3, _SHADE)                                        # sunglasses bar
        r(-5, -8, 10, 1, _SHADE_HI)
        r(-3, -8, 1, 3, _SHADE_HI)                                      # lens glints
        r( 3, -8, 1, 3, _SHADE_HI)

        r(-4, -4, 8, 1, _STUBBLE)                                       # stubble jaw
        r(-3, -3, 6, 1, _STUBBLE)
        r(-2, -3, 4, 1, _MOUTH)                                         # grin

        r(-3,  0, 6, 1, _LANYARD)                                       # whistle lanyard
        r( 1,  1, 2, 2, _WHISTLE)                                       # whistle at chest

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))
        pygame.draw.ellipse(screen, _HAIR, (px - 6, py - 14, 12, 8))
        pygame.draw.ellipse(screen, _HAIR_LT, (px - 4, py - 13, 6, 3))
        r(-6, -6, 2, 3, _HAIR_DK)
        r( 4, -6, 2, 3, _HAIR_DK)
