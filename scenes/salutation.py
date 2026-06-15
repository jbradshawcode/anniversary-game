"""Scene 3 — The Salutation pub interior (154 King Street).

Wide main bar room (bar runs the full depth down the LEFT/west wall, fireplace +
banquette on the east wall) that opens, at the rear-right, into a NARROWER skylit
conservatory wing whose bi-fold garden doors sit at its far-right end. Enter by
the front door (bottom, off King St); the rear-left is outside the building.

Palette/decor tuned to the photos: muted sage half-panelling + warm cream walls,
walls of framed educational posters, grey slate flagstones, a tall dark-green
fireplace with over-mantel mirror + chalkboard, and a glazed-lantern conservatory.
"""
import pygame
from .base import Scene
from config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .palette import WOOD_DK as _DOOR_DK

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_PINE       = (172, 140, 92)
_PINE_ALT   = (162, 130, 82)
_PINE_SEAM  = (146, 116, 70)
_SLATE      = (96, 102, 108)
_SLATE_ALT  = (88, 94, 100)
_GROUT      = (74, 80, 86)
_SAGE       = (110, 122, 104)
_SAGE_DK    = (88, 100, 82)
_CREAM      = (238, 230, 214)
_CREAM_DK   = (226, 217, 200)
_FIRE       = (46, 70, 60)
_FIRE_DK    = (32, 52, 44)
_BAR_WOOD   = (74, 50, 30)
_BAR_DK     = (50, 33, 18)
_BAR_TOP    = (96, 70, 44)
_BAR_PANEL  = (60, 41, 24)
_BRASS      = (206, 184, 122)
_BRASS_DK   = (168, 148, 92)
_MIRROR     = (180, 194, 202)
_BOTTLE_G   = (40, 92, 60)
_BOTTLE_A   = (162, 110, 48)
_BOTTLE_C   = (188, 202, 212)
_BOTTLE_R   = (150, 60, 60)
_SHELF      = (96, 72, 44)
_TABLE      = (158, 122, 76)
_TABLE_DK   = (132, 100, 60)
_CHAIR      = (120, 90, 56)
_LEATHER    = (150, 88, 52)
_LEATHER_DK = (122, 68, 38)
_RED_LEA    = (128, 54, 54)
_RED_LEA_DK = (98, 40, 40)
_STAINED_R  = (180, 45, 55)
_STAINED_G  = (55, 135, 85)
_STAINED_B  = (65, 95, 160)
_STAINED_Y  = (220, 195, 85)
_DOOR_WOOD  = (74, 50, 30)
_GLASS      = (168, 188, 200)
_GLASS_HI   = (196, 212, 220)
_GLASS_DK   = (138, 158, 172)
_IRON       = (45, 45, 48)
_SCONCE_GL  = (250, 232, 180)
_FRAME      = (150, 134, 108)
_FRAME_DK   = (96, 82, 60)
_MOUNT      = (250, 246, 238)
_BANQ       = (150, 156, 120)
_BANQ_DK    = (120, 128, 92)
_MUST       = (192, 152, 72)
_MUST_DK    = (160, 122, 52)
_TV         = (22, 24, 28)
_POSTER     = [(182, 72, 60), (96, 112, 150), (206, 186, 128),
               (122, 142, 112), (168, 150, 180), (150, 90, 70)]


def _dk(c, n=25):
    return tuple(max(0, v - n) for v in c)


# ── Floor ────────────────────────────────────────────────────────────────────

def _draw_floor(surf):
    # Stripped-pine boards run lengthwise (toward the rear) — main room
    fx, fy = 2 * _TS, 6 * _TS
    fw, fh = 15 * _TS, 7 * _TS
    pygame.draw.rect(surf, _PINE, (fx, fy, fw, fh))
    for i, x in enumerate(range(fx, fx + fw, 11)):
        if i % 2:
            pygame.draw.rect(surf, _PINE_ALT, (x, fy, 11, fh))
        pygame.draw.line(surf, _PINE_SEAM, (x, fy), (x, fy + fh), 1)

    # Grey slate flagstones (irregular courses, low contrast) — conservatory wing
    px, py = 10 * _TS, 1 * _TS
    pw, ph = 7 * _TS, 5 * _TS
    pygame.draw.rect(surf, _SLATE, (px, py, pw, ph))
    y = py
    for ci, course in enumerate((26, 24, 28, 24, 26)):
        pygame.draw.line(surf, _GROUT, (px, y), (px + pw, y), 1)
        off = (ci * 13) % 30
        for x in range(px - off, px + pw, 30):
            pygame.draw.line(surf, _GROUT, (max(px, x), y), (max(px, x), min(py + ph, y + course)), 1)
            if (x // 30 + ci) % 3 == 0:
                pygame.draw.rect(surf, _SLATE_ALT,
                                 (max(px + 1, x + 1), y + 1,
                                  min(28, px + pw - x - 1), course - 2))
        y += course


# ── Walls (cream upper / sage dado) ──────────────────────────────────────────

def _wall_v(surf, col, r0, r1):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    split = h * 2 // 5
    pygame.draw.rect(surf, _CREAM, (x, y, _TS, split))
    pygame.draw.rect(surf, _SAGE, (x, y + split, _TS, h - split))
    pygame.draw.line(surf, _SAGE_DK, (x, y + split), (x + _TS, y + split), 2)
    for py in range(y + split + 6, y + h - 6, 24):
        ph = min(18, y + h - 6 - py)
        if ph > 6:
            pygame.draw.rect(surf, _SAGE_DK, (x + 5, py, _TS - 10, ph), 1)


def _wall_h(surf, c0, c1, row, cap_bottom=False):
    x, y = c0 * _TS, row * _TS
    w = (c1 - c0 + 1) * _TS
    if cap_bottom:
        pygame.draw.rect(surf, _SAGE, (x, y, w, 22))
        pygame.draw.rect(surf, _CREAM_DK, (x, y + 22, w, 10))
        pygame.draw.line(surf, _SAGE_DK, (x, y + 22), (x + w, y + 22), 1)
        body_y = y + 4
    else:
        pygame.draw.rect(surf, _CREAM_DK, (x, y, w, 10))
        pygame.draw.rect(surf, _SAGE, (x, y + 10, w, 22))
        pygame.draw.line(surf, _SAGE_DK, (x, y + 10), (x + w, y + 10), 1)
        body_y = y + 14
    for px in range(x + 6, x + w - 6, 28):
        pw = min(22, x + w - 6 - px)
        if pw > 8:
            pygame.draw.rect(surf, _SAGE_DK, (px, body_y, pw, 14), 1)


def _draw_walls(surf):
    _wall_v(surf, 1, 6, 12)
    _wall_v(surf, 17, 1, 12)
    _wall_v(surf, 9, 1, 5)
    _wall_h(surf, 2, 9, 5)
    _wall_h(surf, 10, 16, 0)
    _wall_h(surf, 2, 16, 13, cap_bottom=True)


# ── Framed educational posters ───────────────────────────────────────────────

def _frame(surf, x, y, w, h, fill):
    pygame.draw.rect(surf, _MOUNT, (x - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, _FRAME_DK, (x - 1, y - 1, w + 2, h + 2), 1)
    pygame.draw.rect(surf, fill, (x, y, w, h))
    pygame.draw.rect(surf, _dk(fill, 30), (x, y, w, max(2, h // 3)))


def _draw_posters(surf):
    # Feature wall: a row across the main-room rear wall (row 5, cols 3-9)
    for i, c in enumerate(range(3, 10)):
        _frame(surf, c * _TS + 7, 5 * _TS + 4, _TS - 14, 22, _POSTER[i % len(_POSTER)])
    # Conservatory wing: framed prints up its east wall (col 16, rows 1-4)
    for i, r in enumerate(range(1, 5)):
        _frame(surf, 16 * _TS + 8, r * _TS + 7, 16, 17, _POSTER[(i + 2) % len(_POSTER)])
    # A couple on the conservatory rear wall, beside the garden doors
    for i, c in enumerate((11, 12)):
        _frame(surf, c * _TS + 7, 6, _TS - 14, 18, _POSTER[(i + 4) % len(_POSTER)])


# ── Bar (LEFT / west wall, full depth) ───────────────────────────────────────

def _draw_bar(surf):
    # Back-bar gantry against the west wall (col 2): dense bottle shelves +
    # optics + a long mirror, capped by a carved cornice.
    bx, by = 2 * _TS, 6 * _TS
    bw, bh = _TS, 7 * _TS
    pygame.draw.rect(surf, _BAR_DK, (bx, by, bw, bh))
    pygame.draw.rect(surf, _BAR_WOOD, (bx + 2, by + 2, bw - 4, bh - 4))
    pygame.draw.rect(surf, _BAR_DK, (bx, by, bw, 6))            # cornice
    pygame.draw.rect(surf, _BRASS_DK, (bx + 2, by + 5, bw - 4, 1))
    for sy in range(by + 12, by + bh - 6, 14):
        pygame.draw.rect(surf, _SHELF, (bx + 4, sy, bw - 8, 2))
        for i, boff in enumerate(range(bx + 5, bx + bw - 4, 5)):
            bc = (_BOTTLE_G, _BOTTLE_A, _BOTTLE_C, _BOTTLE_R)[i % 4]
            pygame.draw.rect(surf, bc, (boff, sy - 7, 3, 7))
    for my in (by + bh // 3, by + 2 * bh // 3):                 # mirror panels
        pygame.draw.rect(surf, _BRASS, (bx + 6, my - 8, bw - 12, 16), 1)
        pygame.draw.rect(surf, _MIRROR, (bx + 7, my - 7, bw - 14, 14))

    # Counter (col 3): heavy panelled front, brass rail + copper cask pumps
    cx, cy = 3 * _TS, 6 * _TS
    cw, ch = _TS, 7 * _TS
    pygame.draw.rect(surf, _BAR_WOOD, (cx, cy, cw, ch))
    pygame.draw.rect(surf, _BAR_DK, (cx, cy, cw, ch), 1)
    pygame.draw.rect(surf, _BAR_TOP, (cx + cw - 6, cy, 6, ch))
    for py in range(cy + 6, cy + ch - 8, 20):
        pygame.draw.rect(surf, _BAR_PANEL, (cx + 3, py, cw - 10, 14), 1)
        pygame.draw.line(surf, _BAR_TOP, (cx + 4, py + 1), (cx + cw - 8, py + 1), 1)
    pygame.draw.line(surf, _BRASS, (cx + cw, cy + 6), (cx + cw, cy + ch - 6), 2)
    stained = (_STAINED_R, _STAINED_G, _STAINED_B, _STAINED_Y)
    for i in range(5):
        py = cy + 16 + i * (_TS - 2)
        if py + 11 > cy + ch - 4:
            break
        pygame.draw.rect(surf, _BRASS_DK, (cx + cw - 9, py, 5, 11))
        pygame.draw.rect(surf, _BRASS, (cx + cw - 10, py - 2, 7, 3))
        pygame.draw.rect(surf, stained[i % 4], (cx + cw - 9, py + 4, 6, 4))

    for r in (7, 9, 11):                                        # bar stools (loose)
        sx, sy = 4 * _TS + _TS // 2, r * _TS + _TS // 2
        pygame.draw.circle(surf, _LEATHER, (sx, sy), 6)
        pygame.draw.circle(surf, _LEATHER_DK, (sx, sy), 6, 1)
        pygame.draw.line(surf, _IRON, (sx, sy + 5), (sx, sy + 9), 2)


# ── East wall: fireplace (rear) + continuous banquette ───────────────────────

def _draw_fireplace(surf):
    fx, fy = 16 * _TS, 6 * _TS
    fw, fh = _TS, 2 * _TS
    pygame.draw.rect(surf, _FIRE_DK, (fx, fy, fw, fh))
    pygame.draw.rect(surf, _FIRE, (fx + 2, fy + 2, fw - 4, fh - 4))
    mh = fh * 2 // 5
    pygame.draw.rect(surf, _BRASS, (fx + 5, fy + 5, fw - 10, mh), 2)   # over-mantel mirror
    pygame.draw.rect(surf, _MIRROR, (fx + 6, fy + 6, fw - 12, mh - 2))
    pygame.draw.rect(surf, _FIRE_DK, (fx + 3, fy + mh + 7, fw - 6, 4))  # mantel shelf
    pygame.draw.rect(surf, (26, 28, 28), (fx + 6, fy + mh + 12, fw - 12, 12))  # chalkboard
    for lx in range(fx + 8, fx + fw - 8, 4):
        pygame.draw.line(surf, (120, 150, 130), (lx, fy + mh + 15), (lx, fy + mh + 21), 1)
    pygame.draw.rect(surf, _BAR_DK, (fx + 6, fy + fh - 12, fw - 12, 10))  # hearth
    pygame.draw.rect(surf, (150, 70, 40), (fx + 9, fy + fh - 10, fw - 18, 7))


# ── Seating primitives (loose chairs/stools stay passable) ───────────────────

_OFF = {'N': (0, -15), 'S': (0, 15), 'W': (-15, 0), 'E': (15, 0)}


def _chair(surf, cx, cy, side):
    dx, dy = _OFF[side]
    pygame.draw.rect(surf, _CHAIR, (cx + dx - 5, cy + dy - 5, 10, 10))
    pygame.draw.rect(surf, _dk(_CHAIR), (cx + dx - 5, cy + dy - 5, 10, 10), 1)


def _dining_table(surf, col, row, chairs):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _TABLE, (cx - 12, cy - 10, 24, 20))
    pygame.draw.rect(surf, _TABLE_DK, (cx - 12, cy - 10, 24, 20), 1)
    pygame.draw.line(surf, _TABLE_DK, (cx, cy - 10), (cx, cy + 10), 1)
    for s in chairs:
        _chair(surf, cx, cy, s)


def _poseur(surf, col, row, stools):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _BAR_DK, (cx - 10, cy - 10, 20, 20))     # tall = dark, bold
    pygame.draw.rect(surf, _BAR_WOOD, (cx - 8, cy - 8, 16, 16))
    pygame.draw.rect(surf, _BAR_TOP, (cx - 8, cy - 8, 16, 3))
    for s in stools:
        dx, dy = _OFF[s]
        pygame.draw.circle(surf, _RED_LEA, (cx + dx, cy + dy), 5)
        pygame.draw.circle(surf, _RED_LEA_DK, (cx + dx, cy + dy), 5, 1)


def _cast_iron_table(surf, col, row, chairs):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.circle(surf, (224, 210, 190), (cx, cy), 9)         # marble top
    pygame.draw.circle(surf, _IRON, (cx, cy), 9, 2)
    pygame.draw.circle(surf, _IRON, (cx, cy), 2)
    for s in chairs:                                               # bentwood chairs
        dx, dy = _OFF[s]
        pygame.draw.circle(surf, _CHAIR, (cx + dx, cy + dy), 5)
        pygame.draw.circle(surf, _dk(_CHAIR), (cx + dx, cy + dy), 5, 1)


def _banquette_run(surf, col, r0, r1, facing, color, color_dk):
    x = col * _TS
    y0, y1 = r0 * _TS, (r1 + 1) * _TS
    if facing == 'W':                                              # backrest on east wall
        pygame.draw.rect(surf, color_dk, (x + _TS - 8, y0, 8, y1 - y0))
        sx0, sx1 = x + 4, x + _TS - 10
    else:                                                          # backrest on west wall
        pygame.draw.rect(surf, color_dk, (x, y0, 8, y1 - y0))
        sx0, sx1 = x + 12, x + _TS - 2
    pygame.draw.rect(surf, color, (sx0, y0 + 2, sx1 - sx0, y1 - y0 - 4))
    pygame.draw.rect(surf, color_dk, (sx0, y0 + 2, sx1 - sx0, y1 - y0 - 4), 1)
    for cy in range(y0 + _TS, y1, _TS):                            # cushion seams
        pygame.draw.line(surf, color_dk, (sx0, cy), (sx1, cy), 1)
    for lx in range(sx0 + 2, sx1, 6):                              # upholstery stripes
        pygame.draw.line(surf, color_dk, (lx, y0 + 3), (lx, y1 - 3), 1)


def _armchairs(surf):
    for ac, ar in [(5, 12), (6, 12)]:                              # leather tub chairs (loose)
        ax, ay = ac * _TS + 5, ar * _TS + 6
        aw, ah = _TS - 10, _TS - 12
        pygame.draw.rect(surf, _LEATHER, (ax, ay, aw, ah))
        pygame.draw.rect(surf, _LEATHER_DK, (ax, ay, aw, ah), 1)
        pygame.draw.rect(surf, _LEATHER_DK, (ax, ay, 4, ah))
        pygame.draw.rect(surf, _LEATHER_DK, (ax + aw - 4, ay, 4, ah))
        pygame.draw.rect(surf, _LEATHER_DK, (ax, ay, aw, 4))


# ── Main-room seating ────────────────────────────────────────────────────────

def _draw_seating(surf):
    # Long sage-striped banquette down the east wall (below the fireplace)
    _banquette_run(surf, 16, 8, 12, 'W', _BANQ, _BANQ_DK)
    # Tables pulled up to it: bench is the east seat, chair only on the west
    for r in (8, 10, 12):
        _dining_table(surf, 15, r, {'W'})
    # Free-standing tables through the centre (chairs all sides)
    for tc, tr in [(8, 8), (12, 8), (10, 9), (8, 11), (12, 11)]:
        _dining_table(surf, tc, tr, {'N', 'S', 'E', 'W'})
    # Poseur-table cluster + cast-iron round table by the fireplace (rear)
    _poseur(surf, 14, 6, {'S', 'W'})
    _cast_iron_table(surf, 13, 7, {'W', 'S'})
    # Leather tub armchairs near the front, by the bar
    _armchairs(surf)


# ── Rear conservatory wing ───────────────────────────────────────────────────

def _draw_conservatory(surf):
    # Mustard banquette down the wing's west wall, tables pulled up to it
    _banquette_run(surf, 10, 2, 4, 'E', _MUST, _MUST_DK)
    for r in (2, 4):
        _dining_table(surf, 11, r, {'E'})
    # Poseur run with tall stools by the garden doors (right side)
    _poseur(surf, 15, 2, {'W', 'S'})
    _poseur(surf, 15, 4, {'W', 'N'})

    tvx, tvy = 11 * _TS + 6, 4                                     # wall TV (rear wall)
    pygame.draw.rect(surf, _IRON, (tvx - 1, tvy - 1, 26, 16))
    pygame.draw.rect(surf, _TV, (tvx, tvy, 24, 14))
    pygame.draw.rect(surf, (60, 80, 120), (tvx + 2, tvy + 2, 20, 10))


# ── Doors ────────────────────────────────────────────────────────────────────

def _draw_front_door(surf):
    dx, dy = 8 * _TS, 13 * _TS
    dw, dh = 4 * _TS, _TS
    pygame.draw.rect(surf, _DOOR_DK, (dx, dy, dw, dh))
    half = dw // 2 - 3
    for ddx in (dx + 2, dx + dw // 2 + 1):
        pygame.draw.rect(surf, _DOOR_WOOD, (ddx, dy + 2, half, dh - 4))
        pygame.draw.rect(surf, _DOOR_DK, (ddx, dy + 2, half, dh - 4), 1)
        gx, gy = ddx + 4, dy + 4
        gw, gh = half - 8, dh - 10
        if gw > 4 and gh > 2:
            third = max(1, gw // 3)
            pygame.draw.rect(surf, _STAINED_B, (gx, gy, third, gh))
            pygame.draw.rect(surf, _STAINED_R, (gx + third, gy, third, gh))
            pygame.draw.rect(surf, _STAINED_G, (gx + 2 * third, gy, gw - 2 * third, gh))
            pygame.draw.rect(surf, _STAINED_Y, (gx, gy, gw, 2))
            pygame.draw.rect(surf, _STAINED_Y, (gx, gy + gh - 2, gw, 2))
    pygame.draw.rect(surf, _BRASS, (dx + dw // 2 - 3, dy + dh // 2 - 2, 6, 4))


def _draw_garden_doors(surf):
    dx, dy = 14 * _TS, 0
    dw, dh = 3 * _TS, _TS
    pygame.draw.rect(surf, _DOOR_DK, (dx, dy, dw, dh))
    pw = dw // 3 - 2
    for i in range(3):
        px = dx + 1 + i * (pw + 1)
        pygame.draw.rect(surf, _GLASS, (px, dy + 2, pw, dh - 4))
        pygame.draw.rect(surf, _GLASS_HI, (px, dy + 2, pw // 2, (dh - 4) // 2))
        pygame.draw.rect(surf, _GLASS_DK, (px, dy + 2, pw, dh - 4), 1)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(dx + 1, dy + 2, dw - 2, dh - 4))
    for gx in range(dx, dx + dw, 14):
        pygame.draw.circle(surf, (55, 120, 65), (gx + 7, dy + dh // 2 + 2), 9)
        pygame.draw.circle(surf, (40, 95, 50), (gx + 7, dy + dh // 2 + 2), 9, 1)
    surf.set_clip(old_clip)


# ── Lighting fixtures ────────────────────────────────────────────────────────

_PENDANTS = [(6, 9), (10, 10), (14, 9)]
_LANTERNS = [(12, 2), (14, 4)]
_SCONCES  = [(1, 8), (1, 11), (17, 9)]


def _draw_lights(surf):
    for cx, cr in _PENDANTS:
        px, py = cx * _TS + _TS // 2, cr * _TS + _TS // 2
        pygame.draw.line(surf, _BRASS_DK, (px, py - 18), (px, py - 8), 1)
        pygame.draw.circle(surf, _SCONCE_GL, (px, py - 6), 7)
        pygame.draw.circle(surf, _BRASS, (px, py - 6), 7, 1)
    for cx, cr in _LANTERNS:
        px, py = cx * _TS + _TS // 2, cr * _TS + _TS // 2
        pygame.draw.line(surf, _IRON, (px, py - 16), (px, py - 7), 1)
        pygame.draw.rect(surf, _IRON, (px - 5, py - 7, 10, 12), 1)
        pygame.draw.rect(surf, _SCONCE_GL, (px - 3, py - 5, 6, 8))
    for cc, cr in _SCONCES:
        sx = cc * _TS + (_TS - 8 if cc == 1 else 4)
        sy = cr * _TS + _TS // 2
        pygame.draw.rect(surf, _BRASS_DK, (sx + 2, sy, 4, 8))
        pygame.draw.circle(surf, _SCONCE_GL, (sx + 4, sy - 2), 5)
        pygame.draw.circle(surf, _BRASS, (sx + 4, sy - 2), 5, 1)


def _glow(ov, cx, cy, r, color):
    g = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    for rr in range(r, 4, -7):
        layer = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        pygame.draw.circle(layer, (color[0], color[1], color[2], 7), (r, r), rr)
        g.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    ov.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


# ── Scene ────────────────────────────────────────────────────────────────────

# Non-walkable: rear-left void, the bar, the fireplace, both banquettes, every
# table/poseur footprint. Loose chairs/stools/armchairs stay walkable.
_VOID      = [(c, r) for r in range(1, 6) for c in range(2, 10)]
_BAR       = [(c, r) for r in range(6, 13) for c in (2, 3)]
_FIRE_T    = [(16, 6), (16, 7)]
_BANQ_T    = [(16, 8), (16, 9), (16, 10), (16, 11), (16, 12)]
_MAIN_TBL  = [(15, 8), (15, 10), (15, 12),               # banquette row
              (8, 8), (12, 8), (10, 9), (8, 11), (12, 11),  # centre tables
              (14, 6), (13, 7)]                          # fireplace poseur + cast-iron
_CONSV     = [(10, 2), (10, 3), (10, 4),            # mustard banquette
              (11, 2), (11, 4),                      # banquette tables
              (15, 2), (15, 4)]                      # poseur run
_BLOCKED   = _VOID + _BAR + _FIRE_T + _BANQ_T + _MAIN_TBL + _CONSV


class Salutation(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('salutation')
        self._overlay = None

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_floor(screen)
        _draw_walls(screen)
        _draw_posters(screen)
        _draw_bar(screen)
        _draw_fireplace(screen)
        _draw_seating(screen)
        _draw_conservatory(screen)
        _draw_front_door(screen)
        _draw_garden_doors(screen)
        _draw_lights(screen)
        self._draw_objects(screen)

    def draw_overlay(self, screen: pygame.Surface):
        if self._overlay is None:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Glazed-lantern roof over the conservatory wing: timber rafters
            beam = (92, 64, 38, 120)
            beam_hi = (146, 112, 70, 70)
            x0, x1 = 10 * _TS, 17 * _TS
            for ry in range(_TS // 2, 5 * _TS, 18):              # purlins across the wing
                pygame.draw.rect(ov, beam, (x0, ry, x1 - x0, 3))
                pygame.draw.rect(ov, beam_hi, (x0, ry, x1 - x0, 1))
            for rx in (11 * _TS, 13 * _TS, 15 * _TS):            # rafters down the wing
                pygame.draw.rect(ov, beam, (rx - 1, 0, 3, 5 * _TS))
            # warm light pools under every fitting
            for cx, cr in _PENDANTS:
                _glow(ov, cx * _TS + _TS // 2, cr * _TS + _TS // 2 - 6, 40, (255, 222, 150))
            for cx, cr in _LANTERNS:
                _glow(ov, cx * _TS + _TS // 2, cr * _TS + _TS // 2 - 4, 28, (255, 224, 156))
            for cc, cr in _SCONCES:
                sx = cc * _TS + (_TS - 4 if cc == 1 else 4)
                _glow(ov, sx, cr * _TS + _TS // 2, 26, (255, 226, 168))
            self._overlay = ov
        screen.blit(self._overlay, (0, 0))
