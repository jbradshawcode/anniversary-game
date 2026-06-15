"""Shared base for humanoid characters (player + NPCs).

Holds the palette and the one shared body sprite. Static NPCs face down and
use the default draw(); the Player overrides draw() to add facing + a walk bob.
A mover (e.g. the follower party) can set `walking`/`walk_phase` to bob too.
"""
import math
import pygame
from typing import NamedTuple, Tuple
from .base import GameObject

Color = Tuple[int, int, int]


class Palette(NamedTuple):
    skin: Color
    skin_sh: Color
    tee: Color
    tee_sh: Color
    short: Color = (35, 35, 38)
    short_sh: Color = (25, 25, 28)
    shoe: Color = (65, 42, 28)
    sole: Color = (45, 30, 18)


_shadow_surf = None


def draw_shadow(screen, px, py):
    """A soft grounding shadow under a humanoid's feet (py = sprite origin)."""
    global _shadow_surf
    if _shadow_surf is None:
        _shadow_surf = pygame.Surface((18, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(_shadow_surf, (0, 0, 0, 70), (0, 0, 18, 7))
    screen.blit(_shadow_surf, (int(px) - 9, int(py) + 12))


def draw_body(screen, px, py, p: Palette):
    """Draw the shared humanoid body at a free pixel position with a palette."""
    def r(x, y, w, h, c):
        pygame.draw.rect(screen, c, (px + x, py + y, w, h))

    r(-2, -1, 4, 2, p.skin)
    r(-7,  1, 3, 2, p.tee)
    r( 4,  1, 3, 2, p.tee)
    r(-7,  3, 3, 2, p.skin)
    r( 4,  3, 3, 2, p.skin)
    r(-5,  1, 10, 5, p.tee)
    r(-5,  1, 1, 5, p.tee_sh)
    r(-2,  1, 4, 1, p.tee_sh)
    r(-4,  6, 8, 1, p.short_sh)
    r(-4,  7, 3, 3, p.short)
    r( 1,  7, 3, 3, p.short)
    r(-4,  7, 3, 1, p.short_sh)
    r( 1,  7, 3, 1, p.short_sh)
    r(-4, 10, 3, 3, p.skin)
    r( 1, 10, 3, 3, p.skin)
    r(-4, 10, 1, 3, p.skin_sh)
    r( 1, 10, 1, 3, p.skin_sh)
    r(-5, 13, 5, 2, p.shoe)
    r( 1, 13, 5, 2, p.shoe)
    r(-5, 14, 5, 1, p.sole)
    r( 1, 14, 5, 1, p.sole)


class Humanoid(GameObject):
    _palette: Palette
    walking = False        # set by a mover to enable the walk bob
    walk_phase = 0.0       # advanced by distance moved
    facing = 'down'        # movers (party/cutscene) set this; statics stay 'down'

    def __init__(self, tile_x: int, tile_y: int, blocking: bool = True):
        super().__init__(tile_x, tile_y, blocking=blocking)

    def draw(self, screen: pygame.Surface):
        py = self.y
        if self.walking:
            py -= int(3 * abs(math.sin(self.walk_phase)))
        draw_shadow(screen, self.x, self.y)        # stays grounded under the bob
        if self.facing == 'up':
            self._draw_head_up(screen, self.x, py)
        elif self.facing == 'right':
            self._draw_head_right(screen, self.x, py)
        elif self.facing == 'left':
            self._draw_head_left(screen, self.x, py)
        else:
            self._draw_head_down(screen, self.x, py)
        self._draw_body(screen, self.x, py)
        if self.facing == 'up':
            self._draw_back_hair(screen, self.x, py)

    # Direction dispatch. left/right share one bespoke profile head (auto-mirrored);
    # characters without turned art fall back to the front head, as before.
    def _draw_head_right(self, screen, px, py):
        self._draw_head_side(screen, px, py, False)

    def _draw_head_left(self, screen, px, py):
        self._draw_head_side(screen, px, py, True)

    def _draw_head_side(self, screen, px, py, flip):
        self._draw_head_down(screen, px, py)

    def _draw_head_up(self, screen, px, py):
        self._draw_head_down(screen, px, py)

    def _draw_back_hair(self, screen, px, py):
        pass

    def _draw_body(self, screen, px, py):
        p = self._palette
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-2, -1, 4, 2, p.skin)
        r(-7,  1, 3, 2, p.tee)
        r( 4,  1, 3, 2, p.tee)
        r(-7,  3, 3, 2, p.skin)
        r( 4,  3, 3, 2, p.skin)
        r(-5,  1, 10, 5, p.tee)
        r(-5,  1, 1, 5, p.tee_sh)
        r(-2,  1, 4, 1, p.tee_sh)
        r(-4,  6, 8, 1, p.short_sh)
        r(-4,  7, 3, 3, p.short)
        r( 1,  7, 3, 3, p.short)
        r(-4,  7, 3, 1, p.short_sh)
        r( 1,  7, 3, 1, p.short_sh)
        r(-4, 10, 3, 3, p.skin)
        r( 1, 10, 3, 3, p.skin)
        r(-4, 10, 1, 3, p.skin_sh)
        r( 1, 10, 1, 3, p.skin_sh)
        r(-5, 13, 5, 2, p.shoe)
        r( 1, 13, 5, 2, p.shoe)
        r(-5, 14, 5, 1, p.sole)
        r( 1, 14, 5, 1, p.sole)
