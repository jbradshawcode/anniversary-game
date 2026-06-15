"""Scene 4 — The Salutation beer garden (elongated, scrolling).

Enter from the pub conservatory at the LEFT and walk the garden. THREE pillared
brick-bench BOOTHS line the top and bottom walls — CONTIGUOUS, divided only by
brick pillars (no gaps), as in np_09 / site_18. Each booth (site_23) is a U of
built-in brick benches — back + both long sides — wrapping a wooden table, so 6+
can sit; the benches are walkable (step on to sit), a raised planter sits behind.
The central aisle has the communal table + loose folding chairs; festoon lights
overhead, dense planting at the deep (right) end.
"""
import pygame
from .base import Scene
from config import TILE_SIZE, SCREEN_HEIGHT
from .palette import WOOD_DK as _DOOR_DK

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_YORK       = (178, 172, 162)
_YORK_ALT   = (168, 162, 152)
_YORK_DK    = (155, 148, 138)
_BRICK      = (155, 85, 65)
_BRICK_ALT  = (142, 78, 58)
_MORTAR     = (185, 178, 168)
_IVY        = (58, 108, 52)
_IVY_DK     = (42, 85, 38)
_IVY_LT     = (72, 128, 65)
_LEAF       = (55, 125, 55)
_HERB       = (112, 142, 82)
_FLOWER_R   = (210, 65, 75)
_FLOWER_P   = (195, 85, 165)
_FLOWER_W   = (245, 242, 235)
_OAK        = (128, 98, 62)
_OAK_DK     = (105, 78, 48)
_OAK_LT     = (148, 118, 78)
_FRAME_DK   = (38, 36, 32)
_TEAL_CUSH  = (58, 108, 118)
_TEAL_DK    = (42, 88, 98)
_GLASS      = (162, 182, 198)
_GLASS_HI   = (192, 208, 218)
_GLASS_DK   = (135, 155, 170)
_BRASS      = (200, 180, 120)
_BASKET     = (125, 95, 65)
_BULB       = (255, 236, 170)
_FOLD       = (200, 193, 172)
_FOLD_DK    = (166, 158, 138)

_COLS = 20
_BOOTHS = [5, 9, 13]                 # interior base col of each booth (3 wide)
_PILLARS = [4, 8, 12, 16]            # shared brick pillars dividing the bays


# ── Paving ───────────────────────────────────────────────────────────────────

def _draw_paving(surf):
    px, py = 1 * _TS, 1 * _TS
    pw, ph = 16 * _TS, 13 * _TS
    pygame.draw.rect(surf, _YORK, (px, py, pw, ph))
    tsz = 28
    for tx in range(px, px + pw, tsz):
        for ty in range(py, py + ph, tsz):
            if ((tx - px) // tsz + (ty - py) // tsz) % 2:
                pygame.draw.rect(surf, _YORK_ALT, (tx, ty, tsz, tsz))
            if ((tx - px) // tsz * 3 + (ty - py) // tsz * 7) % 5 == 0:
                pygame.draw.rect(surf, _YORK_DK, (tx + 2, ty + 2, tsz - 4, tsz - 4))


# ── Brick primitives ─────────────────────────────────────────────────────────

def _brick_h(surf, c0, c1, row):
    x, y = c0 * _TS, row * _TS
    w = (c1 - c0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x, y, w, _TS))
    for by in range(y, y + _TS, 8):
        pygame.draw.line(surf, _MORTAR, (x, by), (x + w, by), 1)
        offset = 8 if ((by - y) // 8) % 2 else 0
        for bx in range(x + offset, x + w, 16):
            pygame.draw.line(surf, _MORTAR, (bx, by), (bx, by + 8), 1)


def _brick_v(surf, col, r0, r1):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x, y, _TS, h))
    for by in range(y, y + h, 8):
        pygame.draw.line(surf, _MORTAR, (x, by), (x + _TS, by), 1)
        offset = 4 if ((by - y) // 8) % 2 else 0
        for bx in range(x + offset, x + _TS, 8):
            pygame.draw.line(surf, _MORTAR, (bx, by), (bx, by + 8), 1)


def _greenery(surf, cx, cy, n, spread):
    for j in range(n):
        lx = cx + (j * 11) % spread - spread // 2
        ly = cy + (j * 7) % spread - spread // 2
        pygame.draw.circle(surf, _IVY if j % 2 else _IVY_LT, (lx, ly), 4)
        pygame.draw.circle(surf, _IVY_DK, (lx, ly), 4, 1)


# ── Perimeter (walls, pub door, deep-end planting) ───────────────────────────

def _draw_perimeter(surf):
    _brick_h(surf, 0, _COLS - 1, 0)
    _brick_h(surf, 0, _COLS - 1, 14)
    _brick_v(surf, _COLS - 1, 0, 14)
    _brick_v(surf, 0, 0, 14)
    dy, dh = 6 * _TS, 3 * _TS                 # pub conservatory glazed doors
    pygame.draw.rect(surf, _DOOR_DK, (0, dy, _TS, dh))
    for i in range(3):
        py = dy + 3 + i * _TS
        pygame.draw.rect(surf, _GLASS, (4, py, _TS - 8, _TS - 8))
        pygame.draw.rect(surf, _GLASS_HI, (4, py, (_TS - 8) // 2, (_TS - 8) // 2))
        pygame.draw.rect(surf, _GLASS_DK, (4, py, _TS - 8, _TS - 8), 1)
    pygame.draw.rect(surf, _BRASS, (_TS - 7, dy + dh // 2 - 3, 4, 6))
    for c in (17, 18):                        # dense planting, deep end (close)
        x = c * _TS
        pygame.draw.rect(surf, _IVY_DK, (x, _TS, _TS, 13 * _TS))
        for r in range(1, 14):
            _greenery(surf, x + _TS // 2, r * _TS + _TS // 2, 5, _TS - 6)


# ── U-bench booths (back + both sides wrap the table) ────────────────────────

def _brick_bed(surf, c0, c1, row):
    x, y = c0 * _TS, row * _TS
    w = (c1 - c0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x, y, w, _TS))
    pygame.draw.rect(surf, _BRICK_ALT, (x, y, w, _TS), 2)
    pygame.draw.rect(surf, _IVY_DK, (x + 3, y + 3, w - 6, _TS - 8))
    for j in range(w // 7):
        lx = x + 5 + (j * 7) % (w - 8)
        ly = y + 5 + (j * 5) % (_TS - 10)
        pygame.draw.circle(surf, _HERB if j % 2 else _IVY_LT, (lx, ly), 3)


def _pillar_v(surf, col, r0, r1):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x + 4, y, _TS - 8, h))
    pygame.draw.rect(surf, _BRICK_ALT, (x + 4, y, _TS - 8, h), 2)
    for by in range(y + 5, y + h, 7):
        pygame.draw.line(surf, _MORTAR, (x + 4, by), (x + _TS - 4, by), 1)
    pygame.draw.rect(surf, _IVY_DK, (x + 5, y + 2, _TS - 10, _TS - 8))
    for j in range(3):
        pygame.draw.circle(surf, _IVY_LT, (x + 8 + j * 5, y + 8), 2)


def _v_table(surf, col, r0, r1):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    pygame.draw.rect(surf, _OAK_LT, (x + 4, y + 2, _TS - 8, h - 4))
    pygame.draw.rect(surf, _OAK_DK, (x + 4, y + 2, _TS - 8, h - 4), 1)
    for gx in (x + _TS // 2 - 3, x + _TS // 2 + 2):
        pygame.draw.line(surf, _OAK, (gx, y + 5), (gx, y + h - 5), 1)


def _vbench(surf, col, r0, r1, face):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x + 6, y, _TS - 10, h))
    for by in range(y + 4, y + h, 7):
        pygame.draw.line(surf, _MORTAR, (x + 6, by), (x + _TS - 4, by), 1)
    sx = x + _TS - 11 if face == 'E' else x + 4
    pygame.draw.rect(surf, _OAK_LT, (sx, y + 2, 7, h - 4))
    pygame.draw.rect(surf, _OAK_DK, (sx, y + 2, 7, h - 4), 1)


def _hbench(surf, c0, c1, row, face):
    x, y = c0 * _TS, row * _TS
    w = (c1 - c0 + 1) * _TS
    pygame.draw.rect(surf, _BRICK, (x, y + 6, w, _TS - 10))
    for by in range(y + 10, y + _TS - 2, 7):
        pygame.draw.line(surf, _MORTAR, (x, by), (x + w, by), 1)
    sy = y + _TS - 11 if face == 'S' else y + 4
    pygame.draw.rect(surf, _OAK_LT, (x + 2, sy, w - 4, 7))
    pygame.draw.rect(surf, _OAK_DK, (x + 2, sy, w - 4, 7), 1)


def _draw_booths(surf):
    for pc in _PILLARS:
        _pillar_v(surf, pc, 1, 4)
        _pillar_v(surf, pc, 10, 13)
    for i in _BOOTHS:
        # TOP booth (opens down): planter row1, back bench row2, table+sides rows 3-4
        _brick_bed(surf, i, i + 2, 1)
        _hbench(surf, i, i + 2, 2, 'S')
        _v_table(surf, i + 1, 3, 4)
        _vbench(surf, i, 3, 4, 'E')
        _vbench(surf, i + 2, 3, 4, 'W')
        # BOTTOM booth (opens up)
        _brick_bed(surf, i, i + 2, 13)
        _hbench(surf, i, i + 2, 12, 'N')
        _v_table(surf, i + 1, 10, 11)
        _vbench(surf, i, 10, 11, 'E')
        _vbench(surf, i + 2, 10, 11, 'W')


# ── Central aisle: communal table + loose seating ────────────────────────────

def _draw_communal(surf):
    x, y = 8 * _TS + 4, 6 * _TS + 3
    w, h = 4 * _TS - 8, 3 * _TS - 6
    pygame.draw.rect(surf, _OAK_LT, (x, y, w, h))
    pygame.draw.rect(surf, _OAK_DK, (x, y, w, h), 1)
    for gy in range(y + 5, y + h - 2, 7):
        pygame.draw.line(surf, _OAK, (x + 3, gy), (x + w - 3, gy), 1)
    for by in (5 * _TS + _TS - 9, 9 * _TS + 2):
        pygame.draw.rect(surf, _TEAL_CUSH, (8 * _TS + 6, by, 4 * _TS - 12, 8))
        pygame.draw.rect(surf, _TEAL_DK, (8 * _TS + 6, by, 4 * _TS - 12, 8), 1)


def _fold_chair(surf, cx, cy):
    pygame.draw.rect(surf, _FOLD, (cx - 5, cy - 5, 10, 10))
    pygame.draw.rect(surf, _FOLD_DK, (cx - 5, cy - 5, 10, 10), 1)
    pygame.draw.line(surf, _FOLD_DK, (cx - 4, cy - 4), (cx + 4, cy + 4), 1)
    pygame.draw.line(surf, _FOLD_DK, (cx + 4, cy - 4), (cx - 4, cy + 4), 1)


def _wood_table(surf, col, row):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _OAK_LT, (cx - 11, cy - 9, 22, 18))
    pygame.draw.rect(surf, _OAK_DK, (cx - 11, cy - 9, 22, 18), 1)
    for gx in range(cx - 8, cx + 9, 5):
        pygame.draw.line(surf, _OAK, (gx, cy - 8), (gx, cy + 8), 1)


def _draw_loose(surf):
    for tc, tr in [(2, 4), (2, 11)]:          # free tables in the pub-end foreground
        _wood_table(surf, tc, tr)
        cx, cy = tc * _TS + _TS // 2, tr * _TS + _TS // 2
        for dx, dy in [(15, 0), (0, -15), (0, 15)]:
            _fold_chair(surf, cx + dx, cy + dy)
    for cc, cr in [(7, 6), (7, 8), (12, 6), (12, 8), (3, 7)]:   # chairs round the communal table
        _fold_chair(surf, cc * _TS + _TS // 2, cr * _TS + _TS // 2)


# ── Hanging baskets ──────────────────────────────────────────────────────────

def _draw_baskets(surf):
    for pc in _PILLARS[::2]:
        for hy in (5 * _TS, 9 * _TS + 4):
            x = pc * _TS + _TS // 2
            pygame.draw.line(surf, _FRAME_DK, (x, hy), (x, hy + 8), 2)
            pygame.draw.polygon(surf, _BASKET,
                                [(x - 7, hy + 6), (x + 7, hy + 6),
                                 (x + 5, hy + 14), (x - 5, hy + 14)])
            for fi, fc in enumerate([_FLOWER_R, _FLOWER_P, _FLOWER_W]):
                pygame.draw.circle(surf, _LEAF, (x - 4 + fi * 4, hy + 14), 3)
                pygame.draw.circle(surf, fc, (x - 4 + fi * 4, hy + 12), 2)


# ── Scene ────────────────────────────────────────────────────────────────────

# Solid: deep-end planting, the dividing pillars, and per booth the planter-behind
# + table. The U of brick benches (back + sides) and the open aisle are walkable
# (step on a bench = sit), so a booth seats 6+.
_BLOCKED = [(c, r) for c in (17, 18) for r in range(1, 14)]
for _pc in _PILLARS:
    _BLOCKED += [(_pc, r) for r in range(1, 5)] + [(_pc, r) for r in range(10, 14)]
for _i in _BOOTHS:
    _BLOCKED += [(_i, 1), (_i + 1, 1), (_i + 2, 1), (_i + 1, 3), (_i + 1, 4)]
    _BLOCKED += [(_i, 13), (_i + 1, 13), (_i + 2, 13), (_i + 1, 10), (_i + 1, 11)]
_BLOCKED += [(c, r) for c in (8, 9, 10, 11) for r in (6, 7, 8)]      # communal table
_BLOCKED += [(2, 4), (2, 11)]                                        # loose foreground tables


class Garden(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('garden')
        self._overlay = None

    def enter(self, player):
        player.facing = 'right'

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_paving(screen)
        _draw_perimeter(screen)
        _draw_booths(screen)
        _draw_communal(screen)
        _draw_loose(screen)
        _draw_baskets(screen)
        self._draw_objects(screen)

    def draw_overlay(self, screen: pygame.Surface):
        if self._overlay is None:
            ov = pygame.Surface((self.world_width, SCREEN_HEIGHT), pygame.SRCALPHA)
            beam = (90, 65, 40, 110)
            beam_hi = (140, 110, 72, 65)
            x0, x1 = 4 * _TS, 16 * _TS               # pergola over the booth run
            for ry in (_TS + 4, 4 * _TS - 6, 10 * _TS + 4, 13 * _TS - 6):
                pygame.draw.rect(ov, beam, (x0, ry, x1 - x0, 4))
                pygame.draw.rect(ov, beam_hi, (x0, ry, x1 - x0, 2))
            for col in _PILLARS + [i + 1 for i in _BOOTHS]:
                x = col * _TS + _TS // 2
                pygame.draw.rect(ov, beam, (x - 2, _TS, 4, 3 * _TS))
                pygame.draw.rect(ov, beam, (x - 2, 11 * _TS, 4, 3 * _TS))
            for y0 in (6 * _TS - 6, 9 * _TS + 6):    # festoon down the aisle
                x_l, x_r = 2 * _TS, 16 * _TS
                pts = []
                n = (x_r - x_l) // _TS
                for k in range(n + 1):
                    x = x_l + (x_r - x_l) * k // n
                    sag = int(7 * (1 - ((k - n / 2) / (n / 2)) ** 2))
                    pts.append((x, y0 + sag))
                pygame.draw.lines(ov, (60, 55, 50, 200), False, pts, 1)
                for k, (x, y) in enumerate(pts):
                    if 0 < k < n:
                        pygame.draw.circle(ov, _BULB, (x, y + 3), 2)
            self._overlay = ov
        screen.blit(self._overlay, (0, 0))
