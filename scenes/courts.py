"""Scene 9 — Netball courts

Single court behind the sports centre enclosed by wire fence
on three sides (open to walkway at top).  Stairs run up to
the right at top-left; a two-wide gate at the bottom-left
(cols 3,4) lets the court out to the bottom walkway, and the
left pathway runs alongside down to the same walkway.
"""
import pygame
from .base import Scene
from config import TILE_SIZE

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_TARMAC     = (62, 65, 68)
_TARMAC_ALT = (58, 61, 64)
_LINE       = (235, 235, 230)
_FENCE_POST = (42, 42, 40)
_MESH       = (130, 133, 128)
_MESH_DK    = (100, 103, 98)
_BRICK      = (155, 68, 48)
_BRICK_DK   = (130, 52, 35)
_CONCRETE   = (175, 170, 165)
_HOOP_OR    = (230, 120, 40)
_HOOP_DK    = (200, 95, 25)
_POLE       = (140, 142, 145)
_POLE_DK    = (110, 112, 115)
_SKY        = (165, 185, 210)
_LIGHT      = (240, 238, 230)
_STAIR      = (155, 150, 145)
_STAIR_DK   = (135, 130, 125)
_STAIR_NOSE = (175, 170, 165)
_RAIL       = (85, 85, 90)
_RAIL_LT    = (110, 110, 115)

# ── Walls (edges between tiles) ─────────────────────────────────────────────
_WALLS = set()
# Stair bottom wall — prevents north/south between stairs and walkway
for _c in range(2, 4):
    _WALLS.add(((_c, 3), (_c, 4)))
    _WALLS.add(((_c, 4), (_c, 3)))
# Left fence
for _r in range(5, 13):
    _WALLS.add(((2, _r), (3, _r)))
    _WALLS.add(((3, _r), (2, _r)))
# Bottom fence — two-wide exit at far-left (cols 3,4 stay open)
for _c in range(5, 17):
    _WALLS.add(((_c, 12), (_c, 13)))
    _WALLS.add(((_c, 13), (_c, 12)))

_FW = 6

# ── Court rectangle (pixel coords for line markings) ─────────────────────────
_COURT = pygame.Rect(
    3 * _TS + 10,
    6 * _TS,
    14 * _TS - 20,
    6 * _TS,
)


# ── Drawing helpers ──────────────────────────────────────────────────────────

def _brick_rect(surf, x, y, w, h):
    pygame.draw.rect(surf, _BRICK, (x, y, w, h))
    offset = 0
    for gy in range(y, y + h, 4):
        for gx in range(x + offset, x + w, 8):
            pygame.draw.line(surf, _BRICK_DK, (gx, gy), (gx, gy + 4), 1)
        offset = 4 - offset
        pygame.draw.line(surf, _BRICK_DK, (x, gy), (x + w, gy), 1)


def _draw_mesh(surf, rect):
    old_clip = surf.get_clip()
    surf.set_clip(rect)
    for y in range(rect.top - 8, rect.bottom + 8, 8):
        for x in range(rect.left - 8, rect.right + 8, 8):
            pygame.draw.line(surf, _MESH, (x, y), (x + 8, y + 8), 1)
            pygame.draw.line(surf, _MESH_DK, (x + 8, y), (x, y + 8), 1)
    surf.set_clip(old_clip)


# ── Scene elements ──────────────────────────────────────────────────────────

def _draw_sky_strip(surf):
    pygame.draw.rect(surf, _SKY, (0, 0, 20 * _TS, _TS))
    for cx in (5 * _TS, 14 * _TS):
        pygame.draw.ellipse(surf, _LIGHT,
                            (cx - 14, _TS - 10, 28, 10))


def _draw_back_wall(surf):
    _brick_rect(surf, 0, _TS, 20 * _TS, _TS)


def _draw_side_walls(surf):
    _brick_rect(surf, 0, 2 * _TS, 2 * _TS, 13 * _TS)
    _brick_rect(surf, 17 * _TS, 2 * _TS, 3 * _TS, 13 * _TS)


def _draw_walkway(surf):
    x0, y0 = 2 * _TS, 2 * _TS
    w, h = 15 * _TS, 3 * _TS
    pygame.draw.rect(surf, _CONCRETE, (x0, y0, w, h))


def _draw_stairs(surf):
    x0, y0 = 2 * _TS, 2 * _TS
    w = 2 * _TS
    h = 2 * _TS
    num_steps = 8
    step_w = w // num_steps

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

    pygame.draw.rect(surf, _STAIR_DK, (x0, y0, w, h), 1)

    for ry in (y0 + 2, y0 + h - 4):
        pygame.draw.rect(surf, _RAIL, (x0 - 2, ry, w + 4, 2))
        pygame.draw.rect(surf, _RAIL_LT, (x0 - 2, ry, w + 4, 1))
        pygame.draw.rect(surf, _RAIL, (x0 - 4, ry - 1, 3, 4))
        pygame.draw.rect(surf, _RAIL, (x0 + w + 1, ry - 1, 3, 4))


def _draw_left_pathway(surf):
    x0, y0 = 2 * _TS, 5 * _TS
    w, h = _TS, 8 * _TS
    pygame.draw.rect(surf, _CONCRETE, (x0, y0, w, h))


def _draw_court_surface(surf):
    x0, y0 = 3 * _TS, 5 * _TS
    w, h = 14 * _TS, 8 * _TS
    pygame.draw.rect(surf, _TARMAC, (x0, y0, w, h))
    for ty in range(y0, y0 + h, _TS):
        for tx in range(x0, x0 + w, _TS):
            if ((tx - x0) // _TS + (ty - y0) // _TS) % 5 == 0:
                pygame.draw.rect(surf, _TARMAC_ALT, (tx, ty, _TS, _TS))


def _draw_court_lines(surf):
    ct = _COURT
    pygame.draw.rect(surf, _LINE, ct, 2)
    third_w = ct.width // 3
    for i in (1, 2):
        lx = ct.left + i * third_w
        pygame.draw.line(surf, _LINE, (lx, ct.top), (lx, ct.bottom), 2)
    pygame.draw.circle(surf, _LINE, ct.center, 22, 2)
    d_r = ct.height // 2
    arc_l = pygame.Rect(ct.left - d_r, ct.centery - d_r, d_r * 2, d_r * 2)
    pygame.draw.arc(surf, _LINE, arc_l, -1.5708, 1.5708, 2)
    arc_r = pygame.Rect(ct.right - d_r, ct.centery - d_r, d_r * 2, d_r * 2)
    pygame.draw.arc(surf, _LINE, arc_r, 1.5708, 4.7124, 2)


def _draw_hoops(surf):
    ct = _COURT
    for hx in (ct.left + 2, ct.right - 2):
        hy = ct.centery
        pygame.draw.rect(surf, _POLE, (hx - 2, hy - 3, 4, 6))
        pygame.draw.rect(surf, _POLE_DK, (hx - 2, hy - 3, 4, 6), 1)
        pygame.draw.circle(surf, _HOOP_OR, (hx, hy), 6, 2)
        pygame.draw.circle(surf, _HOOP_DK, (hx, hy), 6, 1)


def _draw_fence(surf):
    fw = _FW
    fence_top = 5 * _TS
    fence_h = 8 * _TS

    # Left fence — thin strip on left edge of col 3
    lx = 3 * _TS
    lf = pygame.Rect(lx, fence_top, fw, fence_h)
    _draw_mesh(surf, lf)
    for r in range(5, 13, 2):
        pygame.draw.rect(surf, _FENCE_POST, (lx, r * _TS, fw, 8))
    pygame.draw.rect(surf, _FENCE_POST, (lx, fence_top, fw, 3))
    pygame.draw.rect(surf, _FENCE_POST, (lx, fence_top + fence_h - 3, fw, 3))

    # Right fence — thin strip on right edge of col 16
    rx = 17 * _TS - fw
    rf = pygame.Rect(rx, fence_top, fw, fence_h)
    _draw_mesh(surf, rf)
    for r in range(5, 13, 2):
        pygame.draw.rect(surf, _FENCE_POST, (rx, r * _TS, fw, 8))
    pygame.draw.rect(surf, _FENCE_POST, (rx, fence_top, fw, 3))
    pygame.draw.rect(surf, _FENCE_POST, (rx, fence_top + fence_h - 3, fw, 3))

    # Bottom fence — thin strip at bottom of row 12, with a two-wide exit at
    # the far-left (cols 3,4 open), so the mesh runs from col 5 to col 16.
    by = 13 * _TS - fw
    bx = 5 * _TS
    bw = 12 * _TS
    bf = pygame.Rect(bx, by, bw, fw)
    _draw_mesh(surf, bf)
    for c in range(5, 17, 2):
        pygame.draw.rect(surf, _FENCE_POST, (c * _TS, by, 8, fw))

    # Bottom-right corner post — seal where bottom fence meets the right fence.
    pygame.draw.rect(surf, _FENCE_POST, (rx, by, fw, fw))

    # Exit jambs — left jamb is the bottom of the left fence; right jamb frames
    # the opening at the start of the bottom fence (col 5).
    pygame.draw.rect(surf, _FENCE_POST, (3 * _TS, by - 2, fw, fw + 4))
    pygame.draw.rect(surf, _FENCE_POST, (5 * _TS - fw, by - 2, fw, fw + 4))


def _draw_bottom_walkway(surf):
    x0, y0 = 2 * _TS, 13 * _TS
    w, h = 15 * _TS, 2 * _TS
    pygame.draw.rect(surf, _CONCRETE, (x0, y0, w, h))


# ── Scene ────────────────────────────────────────────────────────────────────

class Courts(Scene):
    walls = _WALLS

    def __init__(self):
        super().__init__('courts')

    def draw_structures(self, screen: pygame.Surface):
        _draw_sky_strip(screen)
        _draw_back_wall(screen)
        _draw_side_walls(screen)
        _draw_walkway(screen)
        _draw_stairs(screen)
        _draw_court_surface(screen)
        _draw_left_pathway(screen)
        _draw_court_lines(screen)
        _draw_hoops(screen)
        _draw_fence(screen)
        _draw_bottom_walkway(screen)
