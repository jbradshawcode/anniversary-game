"""Shared base for humanoid characters (player + NPCs).

Holds the palette and the one shared body sprite. Static NPCs face down and
use the default draw(); the Player overrides draw() to add facing + a walk bob.
A mover (e.g. the follower party) can set `walking`/`walk_phase` to bob too.
"""
import math
import random
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


# Drink glasses carried/rested by a humanoid. Each kind reads by glass shape +
# liquid colour: pints (beer/cider) are tall tumblers; wines are stemmed.
DRINKS = ('beer', 'cider', 'white_wine', 'red_wine')
_GLASS    = (214, 228, 238)     # glass highlight
_GLASS_SH = (150, 170, 186)     # glass edge / stem
_FOAM     = (250, 248, 240)
_LIQUID = {'beer': (240, 178, 36), 'cider': (228, 196, 104),
           'white_wine': (236, 228, 156), 'red_wine': (146, 30, 46)}
_LIQUID_SH = {'beer': (208, 150, 22), 'cider': (198, 166, 80),
              'white_wine': (206, 196, 120), 'red_wine': (110, 20, 34)}


def draw_drink(screen, gx, gy, kind):
    """A small drink sprite resting on its base at (gx, gy) — the bottom centre."""
    if kind not in _LIQUID:
        return
    fill, fill_sh = _LIQUID[kind], _LIQUID_SH[kind]

    def r(x, y, w, h, c):
        pygame.draw.rect(screen, c, (int(gx) + x, int(gy) + y, w, h))

    if kind in ('beer', 'cider'):                # tall pint tumbler
        r(-3, -10, 6, 10, _GLASS_SH)             # glass body outline
        r(-2,  -9, 4,  9, fill)                  # liquid
        r(-2,  -9, 1,  9, fill_sh)               # shaded left edge
        r( 2,  -9, 1,  9, _GLASS)                # highlight
        if kind == 'beer':
            r(-2, -10, 4, 2, _FOAM)              # foam head
    else:                                        # stemmed wine glass
        r(-3,  -9, 6, 3, _GLASS_SH)              # bowl
        r(-2,  -8, 4, 2, fill)
        r(-2,  -8, 1, 2, fill_sh)
        r( 2,  -9, 1, 3, _GLASS)
        r(-1,  -6, 2, 4, _GLASS_SH)              # stem
        r(-2,  -2, 4, 1, _GLASS_SH)              # foot


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
    diving = None          # None | 'left' | 'right' — a sprawled, near-horizontal dive
    sitting = False        # seated side-pose (on a bench)
    fade = 255             # 0..255 sprite opacity; a cutscene 'vanish' tweens this to 0
    holding = None         # None | one of DRINKS — a glass carried in hand / set on the table
    _drink_xy = None       # frozen table spot for the held drink once seated

    def __init__(self, tile_x: int, tile_y: int, blocking: bool = True):
        super().__init__(tile_x, tile_y, blocking=blocking)

    def place_drink(self) -> None:
        """Freeze where a seated character's drink rests on the table — pushed far
        enough toward the table (the way they're facing as they sit) to land ON the
        table sprite, not their lap. Stays put even if they later turn to chat, and a
        little random scatter keeps the glasses from lining up unnaturally."""
        bx = float(getattr(self, '_sit_x', self.x))
        off = {'up': (0, -22), 'down': (0, 32), 'left': (-28, 4), 'right': (28, 4)}
        ox, oy = off.get(self.facing, (0, 32))
        self._drink_xy = (bx + ox + random.uniform(-3.5, 3.5),
                          self.y + oy + random.uniform(-2.0, 2.0))

    def _blit_drink(self, screen: pygame.Surface) -> None:
        if not self.holding:
            return
        if self.sitting:                          # resting on the table in front of them
            if self._drink_xy is None:
                self.place_drink()
            gx, gy = self._drink_xy
        else:                                     # carried in hand, beside the body
            gx, gy = self.x + 8, self.y + 6
        draw_drink(screen, gx, gy, self.holding)

    def _draw_sitting(self, screen: pygame.Surface, px: int, py: int):
        """Seated pose. Facing left/right gives a side pose with the legs folded
        forward; facing up/down (e.g. round a table) a compact front/back pose with
        the legs tucked under. Uses the character's own directional head art."""
        p = self._palette
        dy = 4                            # sitting sinks the body lower than standing
        if self.facing in ('left', 'right'):
            right = self.facing == 'right'

            def r(x, y, w, h, c):
                x0 = px + (x if right else -x - w)
                pygame.draw.rect(screen, c, (x0, py + dy + y, w, h))

            (self._draw_head_right if right else self._draw_head_left)(screen, px, py + dy)
            r(-5, 1, 10, 5, p.tee)        # torso
            r(-5, 1, 1, 5, p.tee_sh)
            r(-2, 1, 4, 1, p.tee_sh)
            r(-4, 6, 5, 3, p.short)       # hips / seat
            r(-4, 6, 5, 1, p.short_sh)
            r(0, 6, 7, 3, p.short)        # thigh, flat out front
            r(0, 6, 7, 1, p.short_sh)
            r(6, 9, 3, 3, p.skin)         # shin dropping to the floor
            r(6, 9, 1, 3, p.skin_sh)
            r(6, 12, 5, 2, p.shoe)        # foot
            r(6, 13, 5, 1, p.sole)
            return

        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + dy + y, w, h))

        (self._draw_head_up if self.facing == 'up' else self._draw_head_down)(screen, px, py + dy)
        r(-5, 1, 10, 5, p.tee)            # torso
        r(-5, 1, 1, 5, p.tee_sh)
        r(-2, 1, 4, 1, p.tee_sh)
        r(-5, 6, 10, 3, p.short)          # lap (wide — knees out to the sides when sat)
        r(-5, 6, 10, 1, p.short_sh)
        r(-4, 9, 3, 2, p.skin)            # knees tucked
        r(1, 9, 3, 2, p.skin)
        r(-4, 11, 3, 2, p.shoe)           # feet
        r(1, 11, 3, 2, p.shoe)
        r(-4, 12, 3, 1, p.sole)
        r(1, 12, 3, 1, p.sole)
        if self.facing == 'up':
            self._draw_back_hair(screen, px, py + dy)

    def _draw_diving(self, screen: pygame.Surface):
        """A dive/prone pose, reusing the upright art: render the body to a scratch
        surface, then rotate it nearly flat in the dive direction."""
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        cx, cy = 20, 18
        self._draw_head_side(surf, cx, cy, self.diving == 'left')
        self._draw_body(surf, cx, cy)
        rot = pygame.transform.rotate(surf, 80 if self.diving == 'left' else -80)
        sh = pygame.Surface((28, 8), pygame.SRCALPHA)        # wide grounded shadow
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, 28, 8))
        screen.blit(sh, (int(self.x) - 14, int(self.y) + 11))
        screen.blit(rot, rot.get_rect(center=(int(self.x), int(self.y) + 5)))

    def draw(self, screen: pygame.Surface):
        if self.fade >= 255:
            self._render(screen)
        elif self.fade > 0:                 # fading out: render through a translucent layer
            scratch = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            self._render(scratch)
            scratch.fill((255, 255, 255, int(self.fade)), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(scratch, (0, 0))
        # fade <= 0: fully gone, draw nothing

    def _render(self, screen: pygame.Surface):
        if self.diving:
            self._draw_diving(screen)
            return
        if self.sitting:
            draw_shadow(screen, self.x, self.y)
            self._draw_sitting(screen, int(self.x), int(self.y))
            self._blit_drink(screen)
            return
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
        self._blit_drink(screen)

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
