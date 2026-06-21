"""Scene 3 — The Salutation pub interior (154 King Street, Hammersmith).

Rebuilt from the audited spec (specs/the_salutation.scene.json + refs/the_salutation):
a wide, horizontally-scrolling room. The single L-shaped peninsula BAR sits across
the top-centre, its back-bar gantry (bottles, optics, glass-front fridges) against
the top wall. The front door is off-centre on the WEST edge (off King St); the rear
opens RIGHT into a narrower glazed CONSERVATORY lean-to whose bi-fold garden doors
are on the far EAST edge.

Bottom wall = tartan banquette runs flanking the teal "Salutation" fireplace, with
dining tables pulled up to them and chairs on the room side. Front room = cast-iron
bistro tables + dining; a leather-tub lounge nook sits by the bar; the conservatory
runs single-file along a mustard banquette.
"""
import pygame
from .base import Scene
from config import TILE_SIZE, SCREEN_HEIGHT

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
_FIRE_CR    = (224, 214, 196)
_FIRE_CR_DK = (188, 178, 160)
_BAR_WOOD   = (74, 50, 30)
_BAR_DK     = (50, 33, 18)
_BAR_TOP    = (104, 76, 48)
_BAR_PANEL  = (60, 41, 24)
_BRASS      = (206, 184, 122)
_BRASS_DK   = (168, 148, 92)
_MIRROR     = (180, 194, 202)
_FRIDGE     = (150, 170, 182)
_FRIDGE_DK  = (108, 128, 142)
_FRIDGE_LT  = (188, 206, 216)
_BOTTLE_G   = (40, 92, 60)
_BOTTLE_A   = (162, 110, 48)
_BOTTLE_C   = (188, 202, 212)
_BOTTLE_R   = (150, 60, 60)
_BOTTLE_B   = (70, 100, 150)
_SHELF      = (96, 72, 44)
_TABLE      = (158, 122, 76)
_TABLE_DK   = (132, 100, 60)
_CHAIR      = (120, 90, 56)
_LEATHER    = (150, 88, 52)
_LEATHER_DK = (122, 68, 38)
_TARTAN     = (140, 58, 56)
_TARTAN_DK  = (108, 42, 42)
_TARTAN_LN  = (196, 120, 90)
_MUST       = (196, 156, 74)
_MUST_DK    = (162, 124, 52)
_STAINED_R  = (180, 45, 55)
_STAINED_G  = (55, 135, 85)
_STAINED_B  = (65, 95, 160)
_STAINED_Y  = (220, 195, 85)
_DOOR_DK    = (40, 28, 18)
_DOOR_WOOD  = (74, 50, 30)
_GLASS      = (168, 188, 200)
_GLASS_HI   = (196, 212, 220)
_GLASS_DK   = (138, 158, 172)
_LEAD       = (150, 160, 168)
_IRON       = (45, 45, 48)
_SCONCE_GL  = (250, 232, 180)
_FRAME_DK   = (96, 82, 60)
_MOUNT      = (250, 246, 238)
_POSTER     = [(182, 72, 60), (96, 112, 150), (206, 186, 128),
               (122, 142, 112), (168, 150, 180), (150, 90, 70)]
_BACKBAR    = (52, 84, 92)        # teal-blue panelled back-bar gantry (gallery/27, 30)
_BACKBAR_DK = (38, 64, 70)
_BANQ_GRN   = (150, 170, 122)     # pale-green front-window banquette (gallery/28)
_BANQ_GRN_DK = (116, 134, 92)
_BEAM       = (228, 222, 208)     # painted ceiling beams


def _dk(c, n=25):
    return tuple(max(0, v - n) for v in c)


def _lt(c, n=22):
    return tuple(min(255, v + n) for v in c)


# ── Layout (tile coords, straight from the spec) ─────────────────────────────
_COLS = 34
_MAIN = pygame.Rect(1, 1, 22, 11)        # wood main room
_CONSV = pygame.Rect(23, 3, 10, 7)       # slate conservatory lean-to
_BAR = [(10, 1), (21, 1), (21, 3), (20, 4), (12, 4), (10, 3)]   # L-peninsula poly
_FRONT_DOOR_ROWS = (8, 10)               # west edge gap
_GARDEN_DOOR_ROWS = (3, 5)               # east edge gap

# blocking object footprints (tile rects: col, row, w, h)
_BAR_TILES = ([(c, r) for r in (1, 2) for c in range(10, 21)] +
              [(c, 3) for c in range(11, 20)])
_FIRE_FRONT = [(4, 11), (5, 11)]
_FIRE_BACK = [(14, 11), (15, 11)]
_BANQ_B1 = [(c, 11) for c in range(10, 14)]
_BANQ_B2 = [(c, 11) for c in range(16, 21)]
_BANQ_CONSV = [(c, 3) for c in range(24, 31)]
_TABLES = ([(3, 8), (6, 8), (3, 10), (2, 6)]              # front-room bistros + dining (lower)
           + [(3, 3), (6, 3), (8, 3), (4, 5), (7, 5)]    # front-room tables (upper, by the entry)
           + [(c, 10) for c in range(10, 14)]            # bottom-wall long table (run 1)
           + [(c, 10) for c in range(16, 21)]            # bottom-wall long table (run 2)
           + [(8, 7), (8, 8)]                            # poseurs (off the chair row)
           + [(21, 7)]                                   # lounge low table
           + [(c, 4) for c in range(24, 31)]             # conservatory long table
           + [(26, 7), (29, 7)])                         # conservatory back-row dining pair
_COL_MID = [(16, 6)]


def _walls():
    blocked = set()
    for c in range(_COLS):                                # top + bottom walls
        blocked.add((c, 0))
        blocked.add((c, 12))
    for r in range(1, 12):                                # west wall (front-door gap)
        if not (_FRONT_DOOR_ROWS[0] <= r <= _FRONT_DOOR_ROWS[1]):
            blocked.add((0, r))
    for c in range(23, 33):                               # conservatory lean-to: above + below
        for r in (1, 2, 10, 11):
            blocked.add((c, r))
    for r in range(1, 12):                                # east wall (garden-door gap)
        if not (_GARDEN_DOOR_ROWS[0] <= r <= _GARDEN_DOOR_ROWS[1]):
            blocked.add((33, r))
    return blocked


# Banquettes stay WALKABLE — they're benches you sit ON (the cutscenes seat the
# crew on them, and the player can reach a neighbour to chat). Tables/bar/fireplaces
# /column are solid.
_BLOCKED = sorted(_walls()
                  | set(_BAR_TILES) | set(_FIRE_FRONT) | set(_FIRE_BACK)
                  | set(_TABLES) | set(_COL_MID))


# ── Floor ────────────────────────────────────────────────────────────────────

def _draw_floor(surf):
    fx, fy = _TS, _TS
    fw, fh = 22 * _TS, 11 * _TS                           # stripped-pine main room
    pygame.draw.rect(surf, _PINE, (fx, fy, fw, fh))
    for i, x in enumerate(range(fx, fx + fw, 11)):
        if i % 2:
            pygame.draw.rect(surf, _PINE_ALT, (x, fy, 11, fh))
        pygame.draw.line(surf, _PINE_SEAM, (x, fy), (x, fy + fh), 1)

    px, py = _CONSV.x * _TS, _CONSV.y * _TS               # slate conservatory
    pw, ph = _CONSV.w * _TS, _CONSV.h * _TS
    pygame.draw.rect(surf, _SLATE, (px, py, pw, ph))
    y = py
    for ci, course in enumerate((26, 24, 28, 24, 26, 24, 28)):
        if y >= py + ph:
            break
        pygame.draw.line(surf, _GROUT, (px, y), (px + pw, y), 1)
        off = (ci * 13) % 30
        for x in range(px - off, px + pw, 30):
            pygame.draw.line(surf, _GROUT, (max(px, x), y),
                             (max(px, x), min(py + ph, y + course)), 1)
            if (x // 30 + ci) % 3 == 0:
                pygame.draw.rect(surf, _SLATE_ALT,
                                 (max(px + 1, x + 1), y + 1,
                                  min(28, px + pw - x - 1), course - 2))
        y += course


# ── Walls (cream upper / sage dado) ──────────────────────────────────────────

def _wall_band_h(surf, c0, c1, y, h, cap_bottom):
    x = c0 * _TS
    w = (c1 - c0) * _TS
    if cap_bottom:
        pygame.draw.rect(surf, _SAGE, (x, y, w, h * 2 // 3))
        pygame.draw.rect(surf, _CREAM_DK, (x, y + h * 2 // 3, w, h - h * 2 // 3))
        pygame.draw.line(surf, _SAGE_DK, (x, y + h * 2 // 3), (x + w, y + h * 2 // 3), 1)
        body = y + 4
    else:
        pygame.draw.rect(surf, _CREAM_DK, (x, y, w, h // 3))
        pygame.draw.rect(surf, _SAGE, (x, y + h // 3, w, h - h // 3))
        pygame.draw.line(surf, _SAGE_DK, (x, y + h // 3), (x + w, y + h // 3), 1)
        body = y + h // 3 + 4
    for px in range(x + 8, x + w - 8, 30):
        pygame.draw.rect(surf, _SAGE_DK, (px, body, min(24, x + w - 8 - px), 14), 1)


def _wall_v(surf, col, r0, r1):
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0) * _TS
    split = _TS * 2 // 5
    pygame.draw.rect(surf, _CREAM, (x, y, _TS, split))
    pygame.draw.rect(surf, _SAGE, (x, y + split, _TS, h - split))
    for py in range(y + split + 6, y + h - 6, 26):
        pygame.draw.rect(surf, _SAGE_DK, (x + 5, py, _TS - 10, 16), 1)


def _draw_walls(surf):
    _wall_band_h(surf, 1, 23, 0, _TS, False)                       # main top wall
    _wall_band_h(surf, 1, 23, 12 * _TS, SCREEN_HEIGHT - 12 * _TS, True)  # bottom wall -> screen base
    _wall_v(surf, 0, 1, 12)                                        # west wall
    # conservatory lean-to: short walls above and below the glazed wing
    _wall_band_h(surf, 23, 33, 0, 3 * _TS, False)
    _wall_band_h(surf, 23, 33, 10 * _TS, SCREEN_HEIGHT - 10 * _TS, True)
    _wall_v(surf, 33, 3, 10)


# ── Bar: L-peninsula + back-bar gantry (bottles, optics, fridges) ────────────

def _bar_poly_px():
    return [(c * _TS + (_TS if i in (1, 2) else 0),
             r * _TS + (_TS if i in (2, 3, 4) else 0)) for i, (c, r) in enumerate(_BAR)]


def _draw_bar(surf):
    pts = [(10 * _TS, 1 * _TS), (21 * _TS, 1 * _TS), (21 * _TS, 3 * _TS),
           (20 * _TS, 4 * _TS), (12 * _TS, 4 * _TS), (10 * _TS, 3 * _TS)]
    pygame.draw.polygon(surf, _BAR_WOOD, pts)
    pygame.draw.polygon(surf, _BAR_DK, pts, 2)
    # timber servery top (lighter inlay just inside the front/chamfered edge)
    inner = [(11 * _TS, 1 * _TS + 6), (20 * _TS, 1 * _TS + 6), (20 * _TS, 3 * _TS - 2),
             (19 * _TS - 4, 4 * _TS - 6), (13 * _TS + 4, 4 * _TS - 6), (11 * _TS, 3 * _TS - 2)]
    pygame.draw.polygon(surf, _BAR_TOP, inner)
    pygame.draw.polygon(surf, _BAR_PANEL, inner, 1)
    pygame.draw.line(surf, _BRASS, (12 * _TS, 4 * _TS - 6), (19 * _TS, 4 * _TS - 6), 2)  # foot rail

    # cask pumps + stained-glass-handle taps along the servery front
    for i in range(7):
        hx = (12 + i) * _TS + _TS // 2
        if hx > 19 * _TS:
            break
        py = 3 * _TS + 2
        pygame.draw.rect(surf, _BRASS_DK, (hx - 2, py, 4, 12))
        pygame.draw.rect(surf, _BRASS, (hx - 3, py - 3, 6, 4))
        pygame.draw.rect(surf, (_STAINED_R, _STAINED_G, _STAINED_B, _STAINED_Y)[i % 4],
                         (hx - 2, py + 3, 4, 5))

    # back-bar gantry against the top wall (row 0/1): shelves of bottles, optics,
    # a long mirror, and two glass-front fridges below.
    gx, gy = 10 * _TS, 1 * _TS + 1
    gw = 11 * _TS
    pygame.draw.rect(surf, _BACKBAR, (gx, 1 * _TS, gw, 2 * _TS))            # teal-blue back-bar panel
    for px in range(gx + 4, gx + gw - 2, _TS):                             # panel divisions
        pygame.draw.rect(surf, _BACKBAR_DK, (px, 1 * _TS + 6, _TS - 6, 2 * _TS - 10), 1)
    pygame.draw.rect(surf, _BAR_DK, (gx, 1 * _TS, gw, 5))                   # cornice
    pygame.draw.rect(surf, _BRASS_DK, (gx + 2, 1 * _TS + 4, gw - 4, 1))
    for sy in (gy + 6, gy + 15):                                           # two bottle shelves
        pygame.draw.rect(surf, _SHELF, (gx + 4, sy, gw - 8, 2))
        for i, bx in enumerate(range(gx + 6, gx + gw - 6, 6)):
            bc = (_BOTTLE_G, _BOTTLE_A, _BOTTLE_C, _BOTTLE_R, _BOTTLE_B)[i % 5]
            pygame.draw.rect(surf, bc, (bx, sy - 6, 3, 6))
    mid = gx + gw // 2                                                     # central mirror
    pygame.draw.rect(surf, _BRASS, (mid - 26, gy + 24, 52, 12), 1)
    pygame.draw.rect(surf, _MIRROR, (mid - 25, gy + 25, 50, 10))
    for fx in (gx + 8, gx + gw - 8 - 40):                                  # glass-front fridges
        pygame.draw.rect(surf, _FRIDGE_DK, (fx, gy + 38, 40, 22))
        pygame.draw.rect(surf, _FRIDGE, (fx + 2, gy + 40, 36, 18))
        pygame.draw.rect(surf, _FRIDGE_LT, (fx + 2, gy + 40, 36, 5))
        for cx in range(fx + 5, fx + 38, 6):
            pygame.draw.line(surf, _FRIDGE_DK, (cx, gy + 42, ), (cx, gy + 57), 1)
        pygame.draw.rect(surf, _GLASS_DK, (fx + 2, gy + 40, 36, 18), 1)


# ── Fireplaces (bottom wall) ─────────────────────────────────────────────────

def _draw_fireplaces(surf):
    # cream cast-iron fireplace, front-room end (cols 4-5)
    fx, fy = 4 * _TS, 11 * _TS
    fw = 2 * _TS
    pygame.draw.rect(surf, _FIRE_CR, (fx, fy, fw, _TS))
    pygame.draw.rect(surf, _FIRE_CR_DK, (fx, fy, fw, _TS), 2)
    pygame.draw.rect(surf, _IRON, (fx + fw // 2 - 9, fy + 10, 18, _TS - 12))
    pygame.draw.rect(surf, (150, 70, 40), (fx + fw // 2 - 6, fy + 14, 12, _TS - 18))
    # teal "Salutation" fireplace, bar-hall centre (cols 14-15)
    tx, ty = 14 * _TS, 11 * _TS
    tw = 2 * _TS
    pygame.draw.rect(surf, _FIRE_DK, (tx, ty, tw, _TS))
    pygame.draw.rect(surf, _FIRE, (tx + 2, ty + 2, tw - 4, _TS - 4))
    pygame.draw.rect(surf, _BRASS, (tx + 6, ty + 5, tw - 12, 11), 2)        # over-mantel mirror
    pygame.draw.rect(surf, _MIRROR, (tx + 7, ty + 6, tw - 14, 9))
    pygame.draw.rect(surf, (26, 28, 28), (tx + 8, ty + 18, tw - 16, 9))     # chalkboard
    pygame.draw.rect(surf, _IRON, (tx + fw // 2 - 6, ty + _TS - 9, 12, 7))  # hearth


# ── Banquettes / tables / chairs ─────────────────────────────────────────────

_OFF = {'N': (0, -16), 'S': (0, 16), 'W': (-16, 0), 'E': (16, 0)}


def _chair(surf, cx, cy, side):
    """A wooden chair seen from above: seat pad + a backrest slat on its outer edge."""
    dx, dy = _OFF[side]
    sx, sy = cx + dx, cy + dy
    pygame.draw.rect(surf, _CHAIR, (sx - 5, sy - 5, 10, 10))
    pygame.draw.rect(surf, _lt(_CHAIR), (sx - 5, sy - 5, 10, 3))       # seat highlight
    pygame.draw.rect(surf, _dk(_CHAIR), (sx - 5, sy - 5, 10, 10), 1)
    if dy < 0:                                                          # backrest on the far edge
        pygame.draw.rect(surf, _dk(_CHAIR, 35), (sx - 5, sy - 7, 10, 2))
    elif dy > 0:
        pygame.draw.rect(surf, _dk(_CHAIR, 35), (sx - 5, sy + 5, 10, 2))
    elif dx < 0:
        pygame.draw.rect(surf, _dk(_CHAIR, 35), (sx - 7, sy - 5, 2, 10))
    else:
        pygame.draw.rect(surf, _dk(_CHAIR, 35), (sx + 5, sy - 5, 2, 10))


def _banq_run(surf, c0, c1, row, back, color, dk):
    """A wall banquette along `row`; `back` is the wall side ('S' bottom / 'N' top)."""
    x, y = c0 * _TS, row * _TS
    w = (c1 - c0 + 1) * _TS
    if back == 'S':                                       # backrest at the bottom of the tile
        pygame.draw.rect(surf, dk, (x, y + _TS - 9, w, 9))
        seat = pygame.Rect(x + 2, y + 4, w - 4, _TS - 14)
    else:                                                 # backrest at the top
        pygame.draw.rect(surf, dk, (x, y, w, 9))
        seat = pygame.Rect(x + 2, y + 10, w - 4, _TS - 14)
    pygame.draw.rect(surf, color, seat)
    pygame.draw.rect(surf, dk, seat, 1)
    for lx in range(seat.x + 4, seat.right, 7):           # tartan slubs
        pygame.draw.line(surf, _TARTAN_LN if color is _TARTAN else dk,
                         (lx, seat.y), (lx, seat.bottom), 1)
    for sx in range(x + _TS, x + w, _TS):                 # cushion seams
        pygame.draw.line(surf, dk, (sx, seat.y), (sx, seat.bottom), 1)


def _wood_table(surf, col, row, chairs, landscape=True):
    """A solid rectangular wooden table (the pub's staple): legs, grained top, a sheen."""
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    w, h = (26, 18) if landscape else (18, 26)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    for lx in (r.x + 1, r.right - 3):                     # four legs peeking out under the top
        for ly in (r.y + 1, r.bottom - 3):
            pygame.draw.rect(surf, _dk(_TABLE_DK, 18), (lx, ly, 2, 2))
    pygame.draw.rect(surf, _TABLE, r)                     # top
    pygame.draw.rect(surf, _TABLE_DK, r, 1)
    pygame.draw.rect(surf, _lt(_TABLE), (r.x + 1, r.y + 1, w - 2, 3))   # top sheen
    for gx in range(r.x + 3, r.right - 2, 5):             # plank grain
        pygame.draw.line(surf, _TABLE_DK, (gx, r.y + 2), (gx, r.bottom - 2), 1)
    for s in chairs:
        _chair(surf, cx, cy, s)


# back-compat alias — most tables in the pub are these rectangular wooden ones
def _banq_run_v(surf, col, r0, r1, color, dk):
    """A banquette down a column with its backrest against the WEST wall (the
    front-window bench, gallery/28)."""
    x, y = col * _TS, r0 * _TS
    h = (r1 - r0 + 1) * _TS
    pygame.draw.rect(surf, dk, (x, y, 9, h))                       # backrest against the wall
    seat = pygame.Rect(x + 8, y + 3, _TS - 16, h - 6)
    pygame.draw.rect(surf, color, seat)
    pygame.draw.rect(surf, dk, seat, 1)
    for ly in range(seat.y + 4, seat.bottom, 7):                  # stripe piping
        pygame.draw.line(surf, _lt(color), (seat.x, ly), (seat.right, ly), 1)
    for sy in range(y + _TS, y + h, _TS):                         # cushion seams
        pygame.draw.line(surf, dk, (x + 1, sy), (seat.right, sy), 1)


def _dining_table(surf, col, row, chairs):
    _wood_table(surf, col, row, chairs)


def _bistro(surf, col, row, chairs):
    """A round cast-iron café table — the exception, by the windows."""
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.circle(surf, _IRON, (cx, cy + 8), 3)            # pedestal foot
    pygame.draw.rect(surf, _IRON, (cx - 1, cy, 2, 9))          # iron stem
    pygame.draw.circle(surf, (224, 210, 190), (cx, cy), 9)     # marble round top
    pygame.draw.circle(surf, _dk((224, 210, 190), 30), (cx, cy), 9, 1)
    pygame.draw.circle(surf, (242, 234, 222), (cx - 3, cy - 3), 3)   # sheen
    for s in chairs:
        dx, dy = _OFF[s]
        pygame.draw.circle(surf, _CHAIR, (cx + dx, cy + dy), 5)
        pygame.draw.arc(surf, _dk(_CHAIR, 35),
                        (cx + dx - 5, cy + dy - 5, 10, 10), 0.6, 3.7, 2)   # bentwood back
        pygame.draw.circle(surf, _dk(_CHAIR), (cx + dx, cy + dy), 5, 1)


def _poseur(surf, col, row, stools):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _BAR_DK, (cx - 9, cy - 9, 18, 18))
    pygame.draw.rect(surf, _BAR_WOOD, (cx - 7, cy - 7, 14, 14))
    pygame.draw.rect(surf, _BAR_TOP, (cx - 7, cy - 7, 14, 3))
    for s in stools:
        dx, dy = _OFF[s]
        pygame.draw.circle(surf, _TARTAN, (cx + dx, cy + dy), 5)
        pygame.draw.circle(surf, _TARTAN_DK, (cx + dx, cy + dy), 5, 1)


def _armchair(surf, col, row):
    x, y = col * _TS + 5, row * _TS + 6
    w, h = _TS - 10, _TS - 12
    pygame.draw.rect(surf, _LEATHER, (x, y, w, h))
    pygame.draw.rect(surf, _LEATHER_DK, (x, y, w, h), 1)
    pygame.draw.rect(surf, _LEATHER_DK, (x, y, 4, h))
    pygame.draw.rect(surf, _LEATHER_DK, (x + w - 4, y, 4, h))


def _low_table(surf, col, row):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _TABLE_DK, (cx - 11, cy - 7, 22, 14))
    pygame.draw.rect(surf, _dk(_TABLE_DK), (cx - 11, cy - 7, 22, 14), 1)


def _long_table(surf, c0, c1, row):
    """A run of rectangular wooden tables pushed together into one long communal table."""
    x = c0 * _TS
    y = row * _TS + 6
    w = (c1 - c0 + 1) * _TS
    h = _TS - 12
    for lx in range(x + 4, x + w, _TS):                  # legs under each pushed-together table
        pygame.draw.rect(surf, _dk(_TABLE_DK, 18), (lx, y + h - 2, 2, 2))
        pygame.draw.rect(surf, _dk(_TABLE_DK, 18), (lx + _TS - 10, y + h - 2, 2, 2))
    pygame.draw.rect(surf, _TABLE, (x + 2, y, w - 4, h))
    pygame.draw.rect(surf, _lt(_TABLE), (x + 3, y + 1, w - 6, 3))    # top sheen
    pygame.draw.rect(surf, _TABLE_DK, (x + 2, y, w - 4, h), 1)
    for gx in range(x + _TS, x + w, _TS):                # seams where they're pushed together
        pygame.draw.line(surf, _TABLE_DK, (gx, y), (gx, y + h), 1)
    for gx in range(x + 6, x + w, 6):                    # plank grain
        pygame.draw.line(surf, _dk(_TABLE, 10), (gx, y + 5), (gx, y + h - 2), 1)


def _draw_column(surf):
    """The panelled structural post mid-room (cited gallery/02) — drawn so its solid
    tile reads as a pillar, not invisible floor."""
    for c, r in _COL_MID:
        cx, cy = c * _TS + _TS // 2, r * _TS + _TS // 2
        pygame.draw.rect(surf, _dk(_BAR_DK), (cx - 8, cy - 11, 16, 22))   # base shadow
        pygame.draw.rect(surf, _BAR_WOOD, (cx - 6, cy - 11, 12, 22))      # post
        pygame.draw.rect(surf, _BAR_PANEL, (cx - 4, cy - 8, 8, 16))       # recessed panel
        pygame.draw.rect(surf, _BAR_TOP, (cx - 6, cy - 11, 12, 2))        # capital
        pygame.draw.rect(surf, _BAR_TOP, (cx - 6, cy + 9, 12, 2))         # base moulding
        pygame.draw.rect(surf, _dk(_BAR_DK), (cx - 6, cy - 11, 12, 22), 1)


def _chair_at(surf, col, row, facing):
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
    pygame.draw.rect(surf, _CHAIR, (cx - 6, cy - 6, 12, 12))
    pygame.draw.rect(surf, _dk(_CHAIR), (cx - 6, cy - 6, 12, 12), 1)
    by = cy - 7 if facing == 'down' else cy + 4          # backrest away from the table
    pygame.draw.rect(surf, _dk(_CHAIR, 35), (cx - 6, by, 12, 3))


def _stool(surf, col, row):
    """A loose wooden bar stool tucked up to the counter (passable — squeeze past)."""
    cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2 - 5
    pygame.draw.circle(surf, _BAR_WOOD, (cx, cy), 5)
    pygame.draw.circle(surf, _BAR_TOP, (cx, cy), 5, 1)
    pygame.draw.circle(surf, _BAR_DK, (cx, cy), 2)


def _draw_seating(surf):
    # Bottom wall: two tartan banquette runs flanking the teal fireplace, each with
    # a LONG table (tables pushed together to hang out) + a row of chairs spaced one
    # tile apart on the room side (ref 28: continuous banquette + long table + chairs).
    _banq_run(surf, 10, 13, 11, 'S', _TARTAN, _TARTAN_DK)
    _banq_run(surf, 16, 20, 11, 'S', _TARTAN, _TARTAN_DK)
    _long_table(surf, 10, 13, 10)
    _long_table(surf, 16, 20, 10)
    for c in (10, 11, 12, 13, 16, 17, 18, 19):           # a full row of chairs, facing the table
        _chair_at(surf, c, 9, 'down')
    # bar stools tucked along the counter front (loose — you can squeeze past them)
    for c in (13, 15, 18):
        _stool(surf, c, 4)
    # poseur cluster (off to the side, clear of the chair row) + leather-tub lounge nook
    _poseur(surf, 8, 7, {'S', 'E'})
    _poseur(surf, 8, 8, {'N', 'E'})
    _armchair(surf, 20, 7)
    _low_table(surf, 21, 7)
    _armchair(surf, 22, 7)
    # front-window bench: a pale-green banquette runs up the west wall under the leaded
    # bays (gallery/28), with café/dining tables drawn in front of it.
    _banq_run_v(surf, 1, 1, 7, _BANQ_GRN, _BANQ_GRN_DK)
    # front room — a busy public bar: mostly square/rectangular wooden tables, with a
    # couple of round cast-iron café tables by the windows.
    _wood_table(surf, 3, 3, {'N', 'S', 'E', 'W'})
    _bistro(surf, 6, 3, {'S', 'E', 'W'})
    _wood_table(surf, 8, 3, {'S', 'W'}, landscape=False)
    _wood_table(surf, 4, 5, {'N', 'S', 'E'})
    _bistro(surf, 7, 5, {'S', 'W', 'N'})
    _wood_table(surf, 3, 8, {'S', 'E', 'W'})
    _wood_table(surf, 6, 8, {'S', 'W', 'N'})
    _bistro(surf, 2, 6, {'S', 'E'})
    _wood_table(surf, 3, 10, {'N', 'E'}, landscape=False)


def _draw_conservatory_seating(surf):
    _banq_run(surf, 24, 30, 3, 'N', _MUST, _MUST_DK)      # mustard run along the top
    _long_table(surf, 24, 30, 4)                          # one long table pushed together
    for c in (24, 25, 26, 27, 28, 29, 30):               # a full row of diners on the room side
        _chair_at(surf, c, 5, 'up')
    _dining_table(surf, 26, 7, {'N', 'S', 'E', 'W'})     # a back dining pair deeper in the glasshouse
    _dining_table(surf, 29, 7, {'N', 'S', 'W'})


# ── Windows / prints ─────────────────────────────────────────────────────────

def _leaded_bay(surf, row):
    x, y = 0, row * _TS + 4
    pygame.draw.rect(surf, _GLASS, (x + 4, y, _TS - 6, _TS - 8))
    pygame.draw.rect(surf, _GLASS_HI, (x + 4, y, (_TS - 6) // 2, (_TS - 8) // 2))
    for gx in range(x + 4, x + _TS - 2, 7):
        pygame.draw.line(surf, _LEAD, (gx, y), (gx, y + _TS - 8), 1)
    for gy in range(y, y + _TS - 8, 7):
        pygame.draw.line(surf, _LEAD, (x + 4, gy), (x + _TS - 2, gy), 1)
    pygame.draw.rect(surf, _GLASS_DK, (x + 4, y, _TS - 6, _TS - 8), 1)


def _frame(surf, x, y, w, h, fill):
    pygame.draw.rect(surf, _MOUNT, (x - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, _FRAME_DK, (x - 1, y - 1, w + 2, h + 2), 1)
    pygame.draw.rect(surf, fill, (x, y, w, h))
    pygame.draw.rect(surf, _dk(fill, 30), (x, y, w, max(2, h // 3)))


def _draw_windows_prints(surf):
    for r in (2, 4):                                      # leaded bays on the west wall
        _leaded_bay(surf, r)
    _leaded_bay(surf, 6)                                  # glazed screen
    for i, c in enumerate(range(5, 8)):                   # prints over the front room
        _frame(surf, c * _TS + 7, 6, _TS - 14, 18, _POSTER[i % len(_POSTER)])
    for i, c in enumerate(range(24, 30)):                 # prints down the conservatory
        _frame(surf, c * _TS + 8, 8 * _TS + 6, _TS - 16, 17, _POSTER[(i + 2) % len(_POSTER)])


# ── Doors ────────────────────────────────────────────────────────────────────

def _draw_front_door(surf):
    dx = 0
    dy = _FRONT_DOOR_ROWS[0] * _TS
    dh = (_FRONT_DOOR_ROWS[1] - _FRONT_DOOR_ROWS[0] + 1) * _TS
    pygame.draw.rect(surf, _DOOR_DK, (dx, dy, _TS, dh))
    half = dh // 2 - 3
    for ddy in (dy + 2, dy + dh // 2 + 1):
        pygame.draw.rect(surf, _DOOR_WOOD, (dx + 2, ddy, _TS - 6, half))
        pygame.draw.rect(surf, _DOOR_DK, (dx + 2, ddy, _TS - 6, half), 1)
        gx, gy, gw, gh = dx + 5, ddy + 4, _TS - 12, half - 8
        if gw > 4 and gh > 2:
            third = max(1, gh // 3)
            pygame.draw.rect(surf, _STAINED_B, (gx, gy, gw, third))
            pygame.draw.rect(surf, _STAINED_R, (gx, gy + third, gw, third))
            pygame.draw.rect(surf, _STAINED_G, (gx, gy + 2 * third, gw, gh - 2 * third))
    pygame.draw.rect(surf, _BRASS, (dx + _TS - 6, dy + dh // 2 - 3, 4, 6))


def _draw_garden_doors(surf):
    dx = 33 * _TS
    dy = _GARDEN_DOOR_ROWS[0] * _TS
    dh = (_GARDEN_DOOR_ROWS[1] - _GARDEN_DOOR_ROWS[0] + 1) * _TS
    pygame.draw.rect(surf, _DOOR_DK, (dx, dy, _TS, dh))
    ph = dh // 3 - 2
    for i in range(3):
        py = dy + 1 + i * (ph + 1)
        pygame.draw.rect(surf, _GLASS, (dx + 2, py, _TS - 4, ph))
        pygame.draw.rect(surf, _GLASS_HI, (dx + 2, py, (_TS - 4) // 2, ph // 2))
        pygame.draw.rect(surf, _GLASS_DK, (dx + 2, py, _TS - 4, ph), 1)
    old = surf.get_clip()
    surf.set_clip(pygame.Rect(dx + 2, dy + 1, _TS - 4, dh - 2))
    for gy in range(dy, dy + dh, 14):                     # garden greenery glimpsed through
        pygame.draw.circle(surf, (55, 120, 65), (dx + _TS // 2, gy + 7), 9)
        pygame.draw.circle(surf, (40, 95, 50), (dx + _TS // 2, gy + 7), 9, 1)
    surf.set_clip(old)


# ── Lighting ─────────────────────────────────────────────────────────────────

_PENDANTS = [(4, 8), (8, 9), (12, 9), (16, 9), (20, 9)]
_LANTERNS = [(16, 1), (26, 5), (30, 5), (2, 11)]


def _draw_lights(surf):
    for cx, cr in _PENDANTS:
        px, py = cx * _TS + _TS // 2, cr * _TS + _TS // 2
        pygame.draw.line(surf, _BRASS_DK, (px, py - 20), (px, py - 9), 1)   # flex
        pygame.draw.circle(surf, _BRASS, (px, py - 9), 2)                   # ceiling rose
        pygame.draw.circle(surf, _SCONCE_GL, (px, py - 5), 8)               # glass globe
        pygame.draw.circle(surf, _lt(_SCONCE_GL), (px - 2, py - 7), 3)      # highlight
        pygame.draw.circle(surf, _BRASS, (px, py - 5), 8, 1)
    for cx, cr in _LANTERNS:
        px, py = cx * _TS + _TS // 2, cr * _TS + _TS // 2
        pygame.draw.rect(surf, _IRON, (px - 5, py - 8, 10, 13), 1)
        pygame.draw.rect(surf, _SCONCE_GL, (px - 3, py - 6, 6, 9))


def _glow(ov, cx, cy, r, color):
    g = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    for rr in range(r, 4, -7):
        layer = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        pygame.draw.circle(layer, (color[0], color[1], color[2], 7), (r, r), rr)
        g.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    ov.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


class Salutation(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('salutation')
        self._overlay = None

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_floor(screen)
        _draw_walls(screen)
        _draw_windows_prints(screen)
        _draw_bar(screen)
        _draw_fireplaces(screen)
        _draw_seating(screen)
        _draw_column(screen)
        _draw_conservatory_seating(screen)
        _draw_front_door(screen)
        _draw_garden_doors(screen)
        _draw_lights(screen)
        self._draw_objects(screen)

    def draw_overlay(self, screen: pygame.Surface):
        if self._overlay is None:
            ov = pygame.Surface((self.world_width, SCREEN_HEIGHT), pygame.SRCALPHA)
            beam = (92, 64, 38, 120)
            x0, x1 = _CONSV.x * _TS, (_CONSV.x + _CONSV.w) * _TS   # glazed lantern over the wing
            for ry in range(_CONSV.y * _TS, (_CONSV.y + _CONSV.h) * _TS, 18):
                pygame.draw.rect(ov, beam, (x0, ry, x1 - x0, 3))
            for rx in range(_CONSV.x * _TS, x1, 2 * _TS):
                pygame.draw.rect(ov, beam, (rx, _CONSV.y * _TS, 3, _CONSV.h * _TS))
            # painted ceiling beams crossing the main room (gallery/27, 28)
            for bc in (5, 9, 13, 17, 21):
                pygame.draw.rect(ov, (_BEAM[0], _BEAM[1], _BEAM[2], 34),
                                 (bc * _TS - 3, _MAIN.y * _TS, 6, _MAIN.h * _TS))
            for cx, cr in _PENDANTS:
                _glow(ov, cx * _TS + _TS // 2, cr * _TS + _TS // 2 - 6, 40, (255, 222, 150))
            for cx, cr in _LANTERNS:
                _glow(ov, cx * _TS + _TS // 2, cr * _TS + _TS // 2, 26, (255, 224, 156))
            self._overlay = ov
        screen.blit(self._overlay, (0, 0))
