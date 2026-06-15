"""Scene 6 — Sports centre reception lobby

Wide, shallow room connecting the corridor (west) to the
passage (east).  Stairs up on the left, sofas in the middle,
reception desk with windows on the right.
"""
import pygame
from .base import Scene
from config import TILE_SIZE
from .palette import (
    DOOR_FR as _DOOR_FR, WALL as _WALL, FLOOR as _FLOOR,
)

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_DESK       = (105, 78, 48)
_DESK_LT    = (128, 98, 62)
_DESK_TOP   = (148, 118, 78)
_GLASS      = (155, 175, 190)
_GLASS_HI   = (180, 200, 215)
_GLASS_FR   = (85, 100, 115)
_SOFA       = (58, 62, 68)
_SOFA_CUSH  = (72, 78, 88)
_SOFA_ARM   = (48, 52, 58)
_STAIR      = (155, 150, 145)
_STAIR_DK   = (135, 130, 125)
_STAIR_NOSE = (175, 170, 165)
_RAIL       = (85, 85, 90)
_RAIL_LT    = (110, 110, 115)
_MAT        = (65, 85, 55)
_MONITOR    = (60, 60, 65)
_SCREEN     = (80, 120, 180)
_WIN_FRAME  = (178, 172, 162)


# ── Blocked furniture tiles ─────────────────────────────────────────────────
_BLOCKED = []
for _c in range(1, 4):
    _BLOCKED.append((_c, 9))
    _BLOCKED.append((_c, 10))
_BLOCKED.extend([(6, 9), (6, 10)])
for _r in range(8, 11):
    _BLOCKED.append((7, _r))
for _c in range(10, 14):
    _BLOCKED.append((_c, 9))
    _BLOCKED.append((_c, 10))


# ── Drawing ──────────────────────────────────────────────────────────────────

def _draw_walls(surf):
    for c0, c1, r0, r1 in [(0, 16, 4, 5), (0, 16, 11, 12)]:
        x, y = c0 * _TS, r0 * _TS
        w, h = (c1 - c0) * _TS, (r1 - r0) * _TS
        pygame.draw.rect(surf, _WALL, (x, y, w, h))

    for c0, c1, r0, r1 in [(0, 1, 5, 11), (15, 16, 5, 11)]:
        x, y = c0 * _TS, r0 * _TS
        w, h = (c1 - c0) * _TS, (r1 - r0) * _TS
        pygame.draw.rect(surf, _WALL, (x, y, w, h))


def _draw_floor(surf):
    x0, y0 = 1 * _TS, 5 * _TS
    w, h = 14 * _TS, 6 * _TS
    pygame.draw.rect(surf, _FLOOR, (x0, y0, w, h))
    pygame.draw.rect(surf, _MAT, (1 * _TS, 7 * _TS, 2 * _TS, _TS))


def _draw_corridor_door(surf):
    dx = 0
    dy = 6 * _TS + 2
    dw = _TS
    dh = 2 * _TS - 4
    pygame.draw.rect(surf, _DOOR_FR, (dx, dy - 2, dw, dh + 4))
    pygame.draw.rect(surf, _GLASS, (dx + 2, dy, dw - 4, dh))
    pygame.draw.rect(surf, _GLASS_HI,
                     (dx + 2, dy, (dw - 4) // 2, dh // 2))
    pygame.draw.rect(surf, _GLASS_FR, (dx + 2, dy, dw - 4, dh), 1)
    pygame.draw.line(surf, _GLASS_FR,
                     (dx + dw // 2, dy), (dx + dw // 2, dy + dh), 1)


def _draw_passage_door(surf):
    dx = 15 * _TS
    dy = 6 * _TS + 2
    dw = _TS
    dh = 2 * _TS - 4
    pygame.draw.rect(surf, _DOOR_FR, (dx, dy - 2, dw, dh + 4))
    pygame.draw.rect(surf, _GLASS, (dx + 2, dy, dw - 4, dh))
    pygame.draw.rect(surf, _GLASS_HI,
                     (dx + 2, dy, (dw - 4) // 2, dh // 2))
    pygame.draw.rect(surf, _GLASS_FR, (dx + 2, dy, dw - 4, dh), 1)
    pygame.draw.line(surf, _GLASS_FR,
                     (dx + dw // 2, dy), (dx + dw // 2, dy + dh), 1)


def _draw_stairs(surf):
    x0, y0 = 1 * _TS, 9 * _TS
    w = 3 * _TS
    h = 2 * _TS
    num_steps = 10
    step_w = w // num_steps

    pygame.draw.rect(surf, _WALL, (x0 - 4, y0, 4, h))

    for i in range(num_steps):
        sx = x0 + (num_steps - 1 - i) * step_w
        t = i / max(1, num_steps - 1)
        shade = int(_STAIR[0] * (1 - t * 0.25))
        c = (max(110, shade), max(105, shade - 5), max(100, shade - 10))
        pygame.draw.rect(surf, c, (sx, y0, step_w, h))
        pygame.draw.rect(surf, _STAIR_DK, (sx, y0, step_w, h), 1)
        pygame.draw.line(surf, _STAIR_NOSE, (sx, y0), (sx, y0 + h), 1)

    for ry in (y0 + 2, y0 + h - 4):
        pygame.draw.rect(surf, _RAIL, (x0 - 6, ry, w + 8, 2))
        pygame.draw.rect(surf, _RAIL_LT, (x0 - 6, ry, w + 8, 1))
        pygame.draw.rect(surf, _RAIL, (x0 - 8, ry - 1, 3, 4))
        pygame.draw.rect(surf, _RAIL, (x0 + w + 4, ry - 1, 3, 4))


def _draw_sofas(surf):
    sx = 6 * _TS
    sy = 9 * _TS
    sw = _TS
    sh = 2 * _TS

    pygame.draw.rect(surf, _SOFA, (sx + 1, sy + 1, sw - 2, sh - 2))

    back_w = 7
    pygame.draw.rect(surf, _SOFA_ARM,
                     (sx + sw - back_w - 1, sy + 1, back_w, sh - 2))

    arm_h = 6
    pygame.draw.rect(surf, _SOFA_ARM, (sx + 1, sy + 1, sw - 2, arm_h))
    pygame.draw.rect(surf, _SOFA_ARM,
                     (sx + 1, sy + sh - arm_h - 1, sw - 2, arm_h))

    cush_x = sx + 2
    cush_w = sw - back_w - 4
    cush_top = sy + arm_h + 2
    cush_h = (sh - 2 * arm_h - 6) // 2
    for i in range(2):
        cy = cush_top + i * (cush_h + 2)
        pygame.draw.rect(surf, _SOFA_CUSH, (cush_x, cy, cush_w, cush_h))
        pygame.draw.rect(surf, _SOFA, (cush_x, cy, cush_w, cush_h), 1)


def _draw_glass_partition(surf):
    gx = 7 * _TS
    gy = 8 * _TS
    gw = _TS
    gh = 3 * _TS

    pygame.draw.rect(surf, _GLASS_FR, (gx, gy, gw, gh))
    pygame.draw.rect(surf, _GLASS, (gx + 2, gy + 2, gw - 4, gh - 4))
    pygame.draw.rect(surf, _GLASS_HI,
                     (gx + 2, gy + 2, (gw - 4) // 2, (gh - 4) // 2))

    for py in range(gy + _TS, gy + gh, _TS):
        pygame.draw.line(surf, _GLASS_FR, (gx + 2, py), (gx + gw - 2, py), 1)
    pygame.draw.line(surf, _GLASS_FR,
                     (gx + gw // 2, gy + 2), (gx + gw // 2, gy + gh - 2), 1)

    pygame.draw.rect(surf, _GLASS_FR, (gx, gy, gw, gh), 1)


def _draw_desk(surf):
    x0, y0 = 10 * _TS, 9 * _TS
    w = 4 * _TS
    h = 2 * _TS

    pygame.draw.rect(surf, _DESK, (x0, y0, w, h))
    pygame.draw.rect(surf, _DESK_LT, (x0 + 2, y0 + 2, w - 4, h - 4))
    pygame.draw.rect(surf, _DESK_TOP, (x0 + 4, y0 + 4, w - 8, 6))
    pygame.draw.rect(surf, _DESK, (x0, y0, w, h), 1)

    pygame.draw.rect(surf, _MONITOR, (x0 + 8, y0 + 14, 14, 10))
    pygame.draw.rect(surf, _SCREEN, (x0 + 9, y0 + 15, 12, 7))
    pygame.draw.rect(surf, _MONITOR, (x0 + 13, y0 + 24, 6, 3))

    pygame.draw.rect(surf, _MONITOR, (x0 + w - 22, y0 + 14, 14, 10))
    pygame.draw.rect(surf, _SCREEN, (x0 + w - 21, y0 + 15, 12, 7))
    pygame.draw.rect(surf, _MONITOR, (x0 + w - 19, y0 + 24, 6, 3))


def _draw_windows(surf):
    wy = 11 * _TS
    wh = _TS
    for col in (11, 12):
        wx = col * _TS + 4
        ww = _TS - 8
        pygame.draw.rect(surf, _WIN_FRAME, (wx - 2, wy, ww + 4, wh))
        pygame.draw.rect(surf, _GLASS, (wx, wy + 2, ww, wh - 4))
        pygame.draw.rect(surf, _GLASS_HI, (wx, wy + 2, ww // 2, (wh - 4) // 2))
        pygame.draw.rect(surf, _GLASS_FR, (wx, wy + 2, ww, wh - 4), 1)
        pygame.draw.line(surf, _GLASS_FR,
                         (wx + ww // 2, wy + 2), (wx + ww // 2, wy + wh - 2), 1)




# ── Scene ────────────────────────────────────────────────────────────────────

class Reception(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('reception')

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_walls(screen)
        _draw_floor(screen)
        _draw_corridor_door(screen)
        _draw_passage_door(screen)
        _draw_stairs(screen)
        _draw_sofas(screen)
        _draw_glass_partition(screen)
        _draw_desk(screen)
        _draw_windows(screen)
        self._draw_objects(screen)
