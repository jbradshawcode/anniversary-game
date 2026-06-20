"""Player character — tile-based movement with smooth pixel interpolation"""
import pygame
from ..humanoid import Humanoid, Palette, draw_shadow
from config import TILE_SIZE, TILE_MOVE_SPEED

_SKIN    = (205, 165, 125)
_SKIN_SH = (180, 140, 105)
_HAIR    = ( 95,  55,  30)
_HAIR_LT = (140,  85,  48)
_HAIR_DK = ( 65,  35,  18)
_TEE     = (238, 236, 230)
_TEE_SH  = (210, 208, 200)
_EYE     = ( 50,  35,  25)
_LASH    = ( 25,  12,   3)
_LIP     = (195, 120, 110)
_CHEEK   = (210, 155, 130)
_GLINT   = (240, 245, 235)
_EYE_W   = (235, 235, 240)

# shorts/shoes match the Palette defaults
_PALETTE = Palette(skin=_SKIN, skin_sh=_SKIN_SH, tee=_TEE, tee_sh=_TEE_SH)


class Player(Humanoid):
    _palette = _PALETTE
    name = "Sarah"

    def __init__(self, tile_x: int, tile_y: int):
        super().__init__(tile_x, tile_y, blocking=False)
        self.x         = float(self.x)
        self.y         = float(self.y)
        self._target_x = self.x
        self._target_y = self.y
        self.moving    = False
        self.facing    = 'down'
        self._sit_x    = self.x        # draw-x while seated (set onto the bench by sit())

    def teleport(self, tile_x: int, tile_y: int):
        self.tile_x    = tile_x
        self.tile_y    = tile_y
        self.x         = float(tile_x * TILE_SIZE + TILE_SIZE // 2)
        self.y         = float(tile_y * TILE_SIZE + TILE_SIZE // 2)
        self._target_x = self.x
        self._target_y = self.y
        self.moving    = False

    def sit(self, bench) -> None:
        self.sitting = True
        self.facing = 'left' if bench.tile_x > self.tile_x else 'right'   # face into the room
        self._sit_x = bench.tile_x * TILE_SIZE + TILE_SIZE // 2           # seated ON the bench

    def try_move(self, dtx: int, dty: int, scene) -> bool:
        """Attempt to step one tile in (dtx, dty). Returns True if move started."""
        self.sitting = False              # any move stands you up
        if self.moving:
            return False
        new_tx = self.tile_x + dtx
        new_ty = self.tile_y + dty
        if not scene.is_walkable(new_tx, new_ty):
            return False
        if scene.has_wall(self.tile_x, self.tile_y, new_tx, new_ty):
            return False
        self.tile_x    = new_tx
        self.tile_y    = new_ty
        self._target_x = new_tx * TILE_SIZE + TILE_SIZE // 2
        self._target_y = new_ty * TILE_SIZE + TILE_SIZE // 2
        self.moving    = True
        if dtx > 0:
            self.facing = 'right'
        elif dtx < 0:
            self.facing = 'left'
        elif dty > 0:
            self.facing = 'down'
        else:
            self.facing = 'up'
        return True

    def update(self, dt: float):
        if not self.moving:
            return
        dx   = self._target_x - self.x
        dy   = self._target_y - self.y
        dist = (dx * dx + dy * dy) ** 0.5
        step = TILE_MOVE_SPEED * dt
        if step >= dist:
            self.x      = self._target_x
            self.y      = self._target_y
            self.moving = False
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, screen: pygame.Surface):
        px, py = int(self.x), int(self.y)
        if self.sitting:
            draw_shadow(screen, self._sit_x, self.y)
            self._draw_sitting(screen, int(self._sit_x), py)
            return
        draw_shadow(screen, self.x, self.y)        # grounded under the walk bob
        if self.moving:
            dx = self._target_x - self.x
            dy = self._target_y - self.y
            remaining = (dx * dx + dy * dy) ** 0.5
            t = 1.0 - remaining / TILE_SIZE
            py -= int(3 * 4 * t * (1 - t))
        if self.facing == 'up':
            self._draw_head_up(screen, px, py)
        elif self.facing == 'right':
            self._draw_head_right(screen, px, py)
        elif self.facing == 'left':
            self._draw_head_left(screen, px, py)
        else:
            self._draw_head_down(screen, px, py)
        self._draw_body(screen, px, py)
        if self.facing == 'up':
            self._draw_back_hair(screen, px, py)

    def _draw_head_down(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -15, 14, 5, _HAIR)
        r(-8, -11, 3, 8, _HAIR)
        r( 5, -11, 3, 8, _HAIR)
        r(-4, -15, 3, 2, _HAIR_LT)
        r(-8, -11, 1, 6, _HAIR_DK)
        r( 7, -11, 1, 6, _HAIR_DK)

        pygame.draw.ellipse(screen, _SKIN, (px - 5, py - 11, 10, 10))

        r(-5, -11, 10, 2, _HAIR)
        r(-3, -11, 4, 1, _HAIR_LT)

        r(-4, -8, 3, 1, _LASH)
        r( 1, -8, 3, 1, _LASH)
        r(-4, -7, 3, 2, _EYE)
        r(-4, -7, 1, 1, _GLINT)
        r( 1, -7, 3, 2, _EYE)
        r( 1, -7, 1, 1, _GLINT)

        r(-4, -5, 2, 1, _CHEEK)
        r( 2, -5, 2, 1, _CHEEK)

        r(-1, -4, 2, 1, _LIP)

    def _draw_head_up(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-7, -15, 14, 4, _HAIR)
        r(-8, -11, 16, 10, _HAIR)
        r(-4, -15, 3, 2, _HAIR_LT)
        r(-2, -11, 4, 8, _HAIR_LT)
        r(-8, -11, 2, 8, _HAIR_DK)
        r( 6, -11, 2, 8, _HAIR_DK)

    def _draw_head_right(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r( -7, -15, 14,  3, _HAIR)
        r( -5, -15,  4,  2, _HAIR_LT)

        r( -7, -12,  5, 10, _HAIR)
        r( -5, -12,  2,  7, _HAIR_LT)

        r(-10,  -9,  4,  3, _HAIR)
        r(-12,  -7,  5,  3, _HAIR)
        r(-12,  -4,  4,  3, _HAIR)
        r(-11,  -1,  3,  3, _HAIR)
        r(-10,   2,  2,  2, _HAIR)
        r(-10,  -8,  2,  4, _HAIR_LT)
        r(-12,  -5,  2,  3, _HAIR_DK)
        r(-11,  -2,  2,  2, _HAIR_DK)

        r(  5, -12,  2,  5, _HAIR)
        r(  5, -12,  1,  3, _HAIR_LT)

        pygame.draw.ellipse(screen, _SKIN, (px - 2, py - 12, 8, 10))
        r( -2, -10,  2,  6, _SKIN_SH)

        r( -2, -12,  8,  2, _HAIR)
        r(  0, -12,  3,  1, _HAIR_LT)

        r(  1,  -9,  3,  1, _LASH)
        r(  1,  -8,  1,  2, _EYE_W)
        r(  2,  -8,  2,  2, _EYE)
        r(  2,  -8,  1,  1, _GLINT)
        r(  1,  -6,  3,  1, _LASH)

        r(  5,  -7,  1,  2, _SKIN)
        r(  6,  -6,  1,  1, _SKIN_SH)

        r(  3,  -5,  2,  1, _CHEEK)
        r(  2,  -4,  3,  1, _LIP)
        r(  2,  -3,  2,  1, _SKIN_SH)

    def _draw_head_left(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r( -7, -15, 14,  3, _HAIR)
        r(  1, -15,  4,  2, _HAIR_LT)

        r(  2, -12,  5, 10, _HAIR)
        r(  3, -12,  2,  7, _HAIR_LT)

        r(  6,  -9,  4,  3, _HAIR)
        r(  7,  -7,  5,  3, _HAIR)
        r(  8,  -4,  4,  3, _HAIR)
        r(  8,  -1,  3,  3, _HAIR)
        r(  8,   2,  2,  2, _HAIR)
        r(  8,  -8,  2,  4, _HAIR_LT)
        r( 10,  -5,  2,  3, _HAIR_DK)
        r(  9,  -2,  2,  2, _HAIR_DK)

        r( -7, -12,  2,  5, _HAIR)
        r( -6, -12,  1,  3, _HAIR_LT)

        pygame.draw.ellipse(screen, _SKIN, (px - 6, py - 12, 8, 10))
        r(  0, -10,  2,  6, _SKIN_SH)

        r( -6, -12,  8,  2, _HAIR)
        r( -3, -12,  3,  1, _HAIR_LT)

        r( -4,  -9,  3,  1, _LASH)
        r( -2,  -8,  1,  2, _EYE_W)
        r( -4,  -8,  2,  2, _EYE)
        r( -3,  -8,  1,  1, _GLINT)
        r( -4,  -6,  3,  1, _LASH)

        r( -6,  -7,  1,  2, _SKIN)
        r( -7,  -6,  1,  1, _SKIN_SH)

        r( -5,  -5,  2,  1, _CHEEK)
        r( -5,  -4,  3,  1, _LIP)
        r( -4,  -3,  2,  1, _SKIN_SH)

    def _draw_back_hair(self, screen, px, py):
        def r(x, y, w, h, c):
            pygame.draw.rect(screen, c, (px + x, py + y, w, h))

        r(-3, -2, 6, 3, _HAIR)
        r(-2,  1, 4, 4, _HAIR)
        r(-1,  5, 2, 3, _HAIR)
        r(-1, -1, 2, 2, _HAIR_LT)
        r( 0,  2, 1, 3, _HAIR_LT)
        r(-2,  1, 1, 3, _HAIR_DK)
