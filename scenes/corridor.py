"""Scene 5 — Sports centre corridor

L-shaped corridor connecting the gym (south) to reception
(east), with a west extension past changing rooms.
"""
import pygame
from .base import Scene
from config import TILE_SIZE
from .palette import WALL as _WALL, WALL_DK as _WALL_DK, FLOOR as _FLOOR

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_DOOR       = (175, 135, 82)
_DOOR_DK    = (148, 112, 65)
_DOOR_FR    = (135, 102, 58)
_GLASS      = (155, 175, 190)
_GLASS_HI   = (180, 200, 215)
_CEIL_LIGHT = (242, 232, 205)
_POOL       = (70, 145, 190)
_POOL_DK    = (55, 128, 172)
_LANE_RED   = (200, 65, 55)
_LANE_YEL   = (220, 195, 55)
_LANE_WHT   = (230, 230, 225)
_SILL       = (178, 172, 162)
_CHROME     = (192, 195, 200)
_CHROME_DK  = (158, 162, 168)


# ── Walkable zones ───────────────────────────────────────────────────────────
# Main corridor: cols 1-18, rows 4-6
# West extension: cols 1-4, rows 7-11
# Gym passage: cols 8-11, rows 7-13

_BLOCKED = []
for _r in range(7, 12):
    for _c in range(5, 8):
        _BLOCKED.append((_c, _r))
    for _c in range(12, 19):
        _BLOCKED.append((_c, _r))
for _r in range(12, 14):
    for _c in range(1, 8):
        _BLOCKED.append((_c, _r))
    for _c in range(12, 19):
        _BLOCKED.append((_c, _r))

_FLOOR_ZONES = [
    (1, 19, 4, 7),
    (1, 5, 7, 12),
    (8, 12, 7, 14),
]

_BUILDING = [
    (0, 20, 0, 12),
    (7, 13, 12, 15),
]


# ── Drawing ──────────────────────────────────────────────────────────────────

def _draw_walls(surf):
    for c0, c1, r0, r1 in _BUILDING:
        x, y = c0 * _TS, r0 * _TS
        w, h = (c1 - c0) * _TS, (r1 - r0) * _TS
        pygame.draw.rect(surf, _WALL, (x, y, w, h))


def _draw_floor(surf):
    for c0, c1, r0, r1 in _FLOOR_ZONES:
        pygame.draw.rect(surf, _FLOOR,
                         (c0 * _TS, r0 * _TS,
                          (c1 - c0) * _TS, (r1 - r0) * _TS))


def _draw_ceiling_lights(surf):
    for c in range(3, 18, 4):
        x = c * _TS + _TS // 2
        y = 5 * _TS + _TS // 2
        pygame.draw.rect(surf, _CEIL_LIGHT, (x - 12, y - 2, 24, 4))
        pygame.draw.rect(surf, _WALL_DK, (x - 12, y - 2, 24, 4), 1)
    for r in range(8, 11):
        x = 2 * _TS + _TS // 2
        y = r * _TS + _TS // 2
        pygame.draw.rect(surf, _CEIL_LIGHT, (x - 2, y - 8, 4, 16))
        pygame.draw.rect(surf, _WALL_DK, (x - 2, y - 8, 4, 16), 1)


def _draw_doors(surf):
    for c in (6, 13, 16):
        x = c * _TS + 4
        y = 7 * _TS - 2
        w = _TS - 8
        pygame.draw.rect(surf, _DOOR_FR, (x - 2, y - 2, w + 4, 6))
        pygame.draw.rect(surf, _DOOR, (x, y, w, 4))
        pygame.draw.rect(surf, _DOOR_DK, (x, y, w, 4), 1)

    for c in (9, 10):
        x = c * _TS
        y = 14 * _TS - 6
        pygame.draw.rect(surf, _DOOR_FR, (x, y, _TS, 6))
        pygame.draw.rect(surf, _GLASS, (x + 4, y + 1, _TS - 8, 4))
        pygame.draw.rect(surf, _DOOR_DK, (x + 4, y + 1, _TS - 8, 4), 1)

    dx = 5 * _TS - 2
    dy = 10 * _TS + 2
    dh = 2 * _TS - 4
    pygame.draw.rect(surf, _DOOR_FR, (dx - 2, dy - 2, 6, dh + 4))
    for i in range(2):
        py = dy + i * (dh // 2)
        ph = dh // 2
        pygame.draw.rect(surf, _DOOR, (dx, py, 4, ph))
        pygame.draw.rect(surf, _DOOR_DK, (dx, py, 4, ph), 1)
        pygame.draw.rect(surf, _GLASS, (dx + 1, py + 4, 2, ph - 8))
    pygame.draw.line(surf, _DOOR_FR, (dx, dy + dh // 2), (dx + 4, dy + dh // 2), 1)


def _draw_water_fountain(surf):
    fx = 5 * _TS - 10
    fy = 9 * _TS
    fw, fh = 14, _TS - 2

    pygame.draw.rect(surf, _CHROME_DK, (fx, fy, fw, fh))
    pygame.draw.rect(surf, _CHROME, (fx + 1, fy + 1, fw - 2, fh - 2))

    pygame.draw.rect(surf, _CHROME_DK, (fx + 2, fy + 2, fw - 4, 8))
    pygame.draw.rect(surf, (85, 145, 190), (fx + 3, fy + 3, fw - 6, 6))
    pygame.draw.rect(surf, (65, 125, 170), (fx + 5, fy + 4, 4, 2))

    pygame.draw.line(surf, _CHROME_DK, (fx, fy + 11), (fx + fw, fy + 11), 1)

    pygame.draw.rect(surf, _CHROME_DK, (fx + 2, fy + 14, fw - 4, 12))
    pygame.draw.rect(surf, _CHROME, (fx + 3, fy + 15, fw - 6, 10))
    pygame.draw.rect(surf, (110, 165, 200), (fx + 4, fy + 17, fw - 8, 6))
    pygame.draw.rect(surf, _CHROME_DK, (fx + 4, fy + 17, fw - 8, 6), 1)

    pygame.draw.rect(surf, _CHROME_DK, (fx, fy, fw, fh), 1)


def _draw_pool_windows(surf):
    sections = [
        (1 * _TS, 6 * _TS),
        (8 * _TS, 5 * _TS),
        (14 * _TS, 5 * _TS),
    ]
    wy = 1 * _TS
    wh = 3 * _TS

    for wx, ww in sections:
        pad = 3
        gx, gy = wx + pad, wy + pad
        gw, gh = ww - pad * 2, wh - pad * 2

        pygame.draw.rect(surf, _SILL, (wx, wy, ww, wh))
        pygame.draw.rect(surf, _POOL, (gx, gy, gw, gh))

        for ry in range(gy + 6, gy + gh, 8):
            pygame.draw.line(surf, _POOL_DK, (gx, ry), (gx + gw, ry), 1)

        num_lanes = min(8, max(3, gw // 30))
        lane_w = gw // num_lanes
        for i in range(1, num_lanes):
            lx = gx + i * lane_w
            for dy in range(0, gh, 5):
                seg = (dy // 5) % 4
                if seg < 2:
                    c = _LANE_RED
                elif seg == 2:
                    c = _LANE_YEL
                else:
                    c = _LANE_WHT
                pygame.draw.rect(surf, c, (lx - 1, gy + dy, 3, 3))

        pygame.draw.rect(surf, _GLASS_HI, (gx, gy, gw, 6))

        num_panes = max(2, gw // 48)
        pane_w = gw // num_panes
        for i in range(1, num_panes):
            mx = gx + i * pane_w
            pygame.draw.line(surf, _SILL, (mx, gy), (mx, gy + gh), 2)

        pygame.draw.line(surf, _SILL,
                         (gx, gy + gh // 2), (gx + gw, gy + gh // 2), 2)

        pygame.draw.rect(surf, _WALL_DK, (gx, gy, gw, gh), 1)




# ── Scene ────────────────────────────────────────────────────────────────────

class Corridor(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('corridor')

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_walls(screen)
        _draw_pool_windows(screen)
        _draw_floor(screen)
        _draw_ceiling_lights(screen)
        _draw_doors(screen)
        _draw_water_fountain(screen)
        self._draw_objects(screen)
