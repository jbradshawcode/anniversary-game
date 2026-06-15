"""Scene 8 — Underground passage

Narrow alley alongside the sports centre → stairs down →
tunnel running east → stairs up and right → exit to courts.

Layout (walkable):
  Cols 1-3,   rows 10-12 — flat outdoor alley (enter from left)
  Cols 1-3,   rows 8-9   — stairs down
  Cols 1-16,  rows 5-7   — underground tunnel
  Cols 17-18, rows 5-7   — stairs ascending rightward (exit)
"""
import pygame
from .base import Scene
from config import TILE_SIZE
from .palette import DOOR as _DOOR, DOOR_DK as _DOOR_DK, DOOR_FR as _DOOR_FR

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_BRICK      = (155, 68, 48)
_BRICK_DK   = (130, 52, 35)
_BRICK_GR   = (118, 112, 105)
_BRICK_GDK  = (98, 92, 85)
_CONCRETE   = (165, 160, 155)
_CONC_DK    = (148, 143, 138)
_TUNNEL_W   = (92, 90, 88)
_TUNNEL_WLT = (105, 102, 98)
_TUNNEL_FL  = (108, 105, 100)
_PIPE       = (95, 100, 108)
_PIPE_DK    = (78, 82, 90)
_STAIR      = (155, 150, 145)
_STAIR_DK   = (135, 130, 125)
_STAIR_NOSE = (175, 170, 165)
_RAIL       = (85, 85, 90)
_RAIL_LT    = (110, 110, 115)
_LIGHT      = (235, 225, 195)
_LIGHT_FR   = (85, 85, 90)
_GLASS      = (155, 175, 190)
_GLASS_HI   = (180, 200, 215)
_DRAIN      = (70, 68, 65)
_DRAIN_DK   = (55, 53, 50)
_SKY        = (165, 185, 210)
_WALL_CAP   = (178, 172, 162)

# ── Layout ───────────────────────────────────────────────────────────────────
_BLOCKED = []
for _r in range(8, 13):
    for _c in range(4, 19):
        _BLOCKED.append((_c, _r))


# ── Drawing helpers ──────────────────────────────────────────────────────────

def _brick_rect(surf, x, y, w, h, color, dark):
    pygame.draw.rect(surf, color, (x, y, w, h))
    offset = 0
    for gy in range(y, y + h, 4):
        for gx in range(x + offset, x + w, 8):
            pygame.draw.line(surf, dark, (gx, gy), (gx, gy + 4), 1)
        offset = 4 - offset
        pygame.draw.line(surf, dark, (x, gy), (x + w, gy), 1)


# ── Scene elements ──────────────────────────────────────────────────────────

def _draw_walls(surf):
    _brick_rect(surf, 0, 5 * _TS - 6, 1 * _TS, 3 * _TS + 6 + 6,
                _BRICK, _BRICK_DK)

    _brick_rect(surf, 4 * _TS, 5 * _TS - 6, 16 * _TS, 3 * _TS + 12,
                _BRICK_GR, _BRICK_GDK)

    _brick_rect(surf, 0, 8 * _TS, 1 * _TS, 5 * _TS, _BRICK, _BRICK_DK)
    _brick_rect(surf, 4 * _TS, 8 * _TS, 16 * _TS, 5 * _TS,
                _BRICK, _BRICK_DK)

    _brick_rect(surf, 0, 13 * _TS, 4 * _TS, 2 * _TS, _BRICK, _BRICK_DK)


def _draw_tunnel(surf):
    x0, y0 = 1 * _TS, 5 * _TS
    w = 16 * _TS
    h = 3 * _TS

    pygame.draw.rect(surf, _TUNNEL_W, (x0, y0 - 6, w, 6))
    pygame.draw.line(surf, _TUNNEL_WLT, (x0, y0 - 3), (x0 + w, y0 - 3), 1)
    pygame.draw.line(surf, _BRICK_GDK, (x0, y0 - 6), (x0 + w, y0 - 6), 1)

    pygame.draw.rect(surf, _TUNNEL_FL, (x0, y0, w, h))

    pygame.draw.rect(surf, _TUNNEL_W, (x0, y0 + h, w, 6))
    pygame.draw.line(surf, _TUNNEL_WLT,
                     (x0, y0 + h + 2), (x0 + w, y0 + h + 2), 1)


def _draw_tunnel_pipes(surf):
    x0 = 1 * _TS
    y0 = 5 * _TS - 5
    w = 16 * _TS
    pygame.draw.line(surf, _PIPE, (x0, y0), (x0 + w, y0), 3)
    pygame.draw.line(surf, _PIPE_DK, (x0, y0 + 2), (x0 + w, y0 + 2), 1)

    y1 = y0 - 6
    pygame.draw.line(surf, _PIPE_DK, (x0, y1), (x0 + w, y1), 2)
    pygame.draw.line(surf, _PIPE, (x0, y1 + 1), (x0 + w, y1 + 1), 1)

    for bx in range(x0 + 3 * _TS, x0 + w, 5 * _TS):
        pygame.draw.rect(surf, _PIPE_DK, (bx, y1 - 2, 6, 10))


def _draw_tunnel_lights(surf):
    y0 = 5 * _TS - 4
    for lx in range(4 * _TS, 17 * _TS, 4 * _TS):
        pygame.draw.rect(surf, _LIGHT_FR, (lx - 10, y0 - 2, 20, 4))
        pygame.draw.rect(surf, _LIGHT, (lx - 8, y0 - 1, 16, 3))

        glow = pygame.Surface((48, 3 * _TS), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 248, 220, 18), (0, 0, 48, 3 * _TS))
        surf.blit(glow, (lx - 24, 5 * _TS))


def _draw_alley(surf):
    x0, y0 = 1 * _TS, 10 * _TS
    w = 3 * _TS
    h = 3 * _TS
    pygame.draw.rect(surf, _CONCRETE, (x0, y0, w, h))

    pygame.draw.rect(surf, _DRAIN, (2 * _TS + 8, 11 * _TS + 8, 14, 14))
    pygame.draw.rect(surf, _DRAIN_DK, (2 * _TS + 9, 11 * _TS + 9, 12, 12))
    for dy in range(0, 12, 3):
        pygame.draw.line(surf, _DRAIN,
                         (2 * _TS + 10, 11 * _TS + 10 + dy),
                         (2 * _TS + 20, 11 * _TS + 10 + dy), 1)

    pygame.draw.rect(surf, _WALL_CAP, (4 * _TS - 4, y0, 4, h))

    pygame.draw.rect(surf, _SKY, (x0, y0 - _TS, w, _TS))
    pygame.draw.line(surf, _WALL_CAP, (x0, y0 - 1), (x0 + w, y0 - 1), 2)


def _draw_stairs_down(surf):
    x0 = 1 * _TS
    w = 3 * _TS
    num_steps = 8
    stair_top = 8 * _TS
    total_h = 2 * _TS
    step_h = total_h // num_steps

    for i in range(num_steps):
        sy = stair_top + i * step_h
        t = i / max(1, num_steps - 1)
        r = int(_STAIR[0] * (1 - t * 0.35))
        g = int(_STAIR[1] * (1 - t * 0.35))
        b = int(_STAIR[2] * (1 - t * 0.35))
        pygame.draw.rect(surf, (r, g, b), (x0, sy, w, step_h))
        pygame.draw.rect(surf, _STAIR_DK, (x0, sy, w, step_h), 1)
        nr = int(_STAIR_NOSE[0] * (1 - t * 0.3))
        ng = int(_STAIR_NOSE[1] * (1 - t * 0.3))
        nb = int(_STAIR_NOSE[2] * (1 - t * 0.3))
        pygame.draw.line(surf, (nr, ng, nb), (x0, sy), (x0 + w, sy), 2)

    for rx in (x0 + 2, x0 + w - 4):
        pygame.draw.rect(surf, _RAIL, (rx, stair_top - 2, 2, total_h + 4))
        pygame.draw.rect(surf, _RAIL_LT, (rx, stair_top - 2, 1, total_h + 4))
        pygame.draw.rect(surf, _RAIL, (rx - 1, stair_top - 4, 4, 3))
        pygame.draw.rect(surf, _RAIL, (rx - 1, stair_top + total_h + 1, 4, 3))


def _draw_stairs_right(surf):
    x0 = 17 * _TS
    y0 = 5 * _TS
    total_w = 2 * _TS
    h = 3 * _TS
    num_steps = 8
    step_w = total_w // num_steps

    for i in range(num_steps):
        sx = x0 + i * step_w
        t = i / max(1, num_steps - 1)
        r = int(_STAIR[0] * (1 - (1 - t) * 0.35))
        g = int(_STAIR[1] * (1 - (1 - t) * 0.35))
        b = int(_STAIR[2] * (1 - (1 - t) * 0.35))
        pygame.draw.rect(surf, (r, g, b), (sx, y0, step_w, h))
        pygame.draw.rect(surf, _STAIR_DK, (sx, y0, step_w, h), 1)
        nr = int(_STAIR_NOSE[0] * (1 - (1 - t) * 0.3))
        ng = int(_STAIR_NOSE[1] * (1 - (1 - t) * 0.3))
        nb = int(_STAIR_NOSE[2] * (1 - (1 - t) * 0.3))
        pygame.draw.line(surf, (nr, ng, nb), (sx, y0), (sx, y0 + h), 2)

    for ry in (y0 + 2, y0 + h - 4):
        pygame.draw.rect(surf, _RAIL, (x0 - 2, ry, total_w + 4, 2))
        pygame.draw.rect(surf, _RAIL_LT, (x0 - 2, ry, total_w + 4, 1))
        pygame.draw.rect(surf, _RAIL, (x0 - 4, ry - 1, 3, 4))
        pygame.draw.rect(surf, _RAIL, (x0 + total_w + 1, ry - 1, 3, 4))


def _draw_reception_door(surf):
    dx = 1 * _TS - 4
    dy = 11 * _TS + 2
    dw = 6
    dh = _TS - 4
    pygame.draw.rect(surf, _DOOR_FR, (dx - 2, dy - 2, dw + 4, dh + 4))
    pygame.draw.rect(surf, _DOOR, (dx, dy, dw, dh))
    pygame.draw.rect(surf, _DOOR_DK, (dx, dy, dw, dh), 1)
    pygame.draw.rect(surf, _GLASS, (dx + 1, dy + 3, dw - 2, dh - 6))
    pygame.draw.rect(surf, _GLASS_HI,
                     (dx + 1, dy + 3, (dw - 2) // 2, (dh - 6) // 2))


# ── Scene ────────────────────────────────────────────────────────────────────

class Passage(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('passage')

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_walls(screen)
        _draw_tunnel(screen)
        _draw_tunnel_pipes(screen)
        _draw_tunnel_lights(screen)
        _draw_alley(screen)
        _draw_stairs_down(screen)
        _draw_stairs_right(screen)
        _draw_reception_door(screen)
        self._draw_objects(screen)
