"""High-detail, true-to-life PREVIEW render of a scene_spec — the human sign-off artifact.

Distinct from render_ingame.py (the fast fidelity gate): this is allowed to be heavy. It
supersamples (draws at SS x the base tile, then smoothscales down for anti-aliasing) and uses
detailed procedural sprites with photo-derived colours, so a reviewer judges something
true-to-life — oak refectory tables with chairs tucked around them, an upholstered mustard
banquette, a panelled bar with brass + a bottle gantry, leaded windows with real panes — not
abstract boxes. Top-down, stylised-detailed (RimWorld/Project-Zomboid tier), not photoreal.

Colour fidelity: each object's `palette` maps to a photo-derived tone; an object may also
carry `color: "#rrggbb"` read straight off its cited photo to override. Tables with `seats: N`
are drawn as a setting (table + N chairs tucked to its edges).

Run: SDL_VIDEODRIVER=dummy python3 $SK/render_detail.py the_salutation
Out: refs/<slug>/_render/detail.png
"""
import argparse
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import math  # noqa: E402
import pygame  # noqa: E402
from pygame import gfxdraw  # noqa: E402

import spec as S  # type: ignore  # noqa: E402

REPO_ROOT = S.REPO_ROOT

SS = 2          # supersample factor
TILE = 48 * SS  # internal pixels per tile (downscaled by SS at the end)

# ── photo-derived palette (tones read off the Salutation gallery) ───────────────
WOOD, WOOD2, SEAM = (158, 126, 82), (140, 110, 70), (112, 88, 54)
SLATE, SLATE2, GROUT = (96, 102, 110), (84, 90, 98), (62, 68, 74)
TEAL, TEAL_HI, CREAM, CREAM_DK = (42, 72, 68), (56, 90, 84), (232, 226, 212), (200, 192, 174)
OAKD, OAKD2, BRASS, BRASSD = (56, 40, 26), (40, 30, 20), (198, 170, 100), (150, 126, 70)
BOTTLES = [(46, 96, 64), (158, 74, 52), (196, 206, 214), (200, 152, 74)]
MIRROR = (180, 194, 200)
MUSTARD, MUSTARD_D = (200, 152, 70), (168, 124, 50)
BURG, BURG_D = (138, 70, 62), (108, 50, 46)
LEATHER, LEATHER_D = (152, 90, 52), (120, 66, 38)
TBL, TBL_D, LEG = (156, 116, 70), (126, 92, 54), (84, 62, 38)
CHAIR, CHAIR_D = (116, 84, 50), (86, 62, 34)
FCREAM, FTEAL, FIREBOX, EMBER = (216, 210, 198), (40, 70, 66), (30, 26, 24), (158, 74, 42)
GLASS, AMBER, LEAD = (196, 208, 208), (216, 188, 122), (46, 46, 50)
STAIN = [(150, 62, 66), (70, 122, 92), (80, 102, 152)]
PLASTER, PLASTER_D = (216, 210, 198), (150, 144, 132)
FACADE, FACADE_D, FACWIN = (152, 98, 74), (118, 72, 52), (210, 202, 154)
SCONCE, FRAME, MOUNT = (252, 232, 176), (120, 96, 64), (248, 244, 236)

_OBJ_COL = {
    "cream": FCREAM, "teal": TEAL, "mustard": MUSTARD, "tartan": BURG, "green": (90, 112, 80),
    "oak": OAKD, "dark": OAKD, "brass": BRASS, "_": (150, 134, 108),
}


def _dk(c, n=24):
    return tuple(max(0, v - n) for v in c)


def _lt(c, n=24):
    return tuple(min(255, v + n) for v in c)


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def _basecol(o, default):
    if o.get("color"):
        try:
            return _hex(o["color"])
        except Exception:  # noqa: BLE001
            pass
    if o.get("palette") in _OBJ_COL:
        return _OBJ_COL[o["palette"]]
    return default


def _rrect(s, col, rect, rad=6, border=None, bw=2):
    pygame.draw.rect(s, col, rect, border_radius=rad)
    if border:
        pygame.draw.rect(s, border, rect, bw, border_radius=rad)


def _px(c, r, w=1, h=1):
    return c * TILE, r * TILE, w * TILE, h * TILE


# ── floors ─────────────────────────────────────────────────────────────────────

def _floor(s, reg):
    c, r, w, h = reg["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    mat = reg.get("material", "wood")
    if mat == "slate":
        s.fill(SLATE, (x, y, pw, ph))
        step = TILE // 2
        for ri, yy in enumerate(range(y, y + ph, step)):
            for xi, xx in enumerate(range(x - (ri % 2) * step // 2, x + pw, step)):
                fx = max(x, xx)
                pygame.draw.rect(s, SLATE2 if (xi + ri) % 2 else SLATE,
                                 (fx + 1, yy + 1, min(step, x + pw - fx) - 2, step - 2))
                pygame.draw.rect(s, GROUT, (fx, yy, min(step, x + pw - fx), step), 1)
    else:
        plank = max(10, TILE // 3)
        for i, xx in enumerate(range(x, x + pw, plank)):
            pygame.draw.rect(s, WOOD2 if i % 2 else WOOD, (xx, y, plank, ph))
            pygame.draw.line(s, SEAM, (xx, y), (xx, y + ph))
            for gy in range(y + 14, y + ph, TILE):   # short grain dashes
                pygame.draw.line(s, _dk(WOOD, 12), (xx + 3, gy), (xx + plank - 4, gy))


# ── walls + treatments (panelled wainscot / facade) ──────────────────────────────

def _panel(s, x, y, w, h, vertical):
    pygame.draw.rect(s, CREAM, (x, y, w, h))
    if vertical:
        split = x + int(w * 0.55)
        pygame.draw.rect(s, TEAL, (split, y, x + w - split, h))
        for py in range(y + 6, y + h - 8, 26):
            _rrect(s, _dk(TEAL, 10), (split + 5, py, (x + w - split) - 10, 20), 3, TEAL_HI, 1)
    else:
        split = y + int(h * 0.55)
        pygame.draw.rect(s, TEAL, (x, split, w, y + h - split))
        for px in range(x + 6, x + w - 8, 26):
            _rrect(s, _dk(TEAL, 10), (px, split + 5, 20, (y + h - split) - 10), 3, TEAL_HI, 1)
        pygame.draw.line(s, CREAM_DK, (x, split), (x + w, split), 2)


def _facade(s, x, y, w, h):
    pygame.draw.rect(s, FACADE, (x, y, w, h))
    for ri, yy in enumerate(range(y, y + h, 10)):
        pygame.draw.line(s, FACADE_D, (x, yy), (x + w, yy))
        for xx in range(x - (ri % 2) * 8, x + w, 16):
            pygame.draw.line(s, FACADE_D, (max(x, xx), yy), (max(x, xx), min(y + h, yy + 10)))
    band = y + max(6, h // 3)
    for wx in range(x + 10, x + w - 14, 34):
        _rrect(s, FACWIN, (wx, band, 18, min(16, h - 12)), 2, FACADE_D, 2)


def draw_walls(s, spec, kind):
    ext = kind in ("exterior", "street")
    for c, r, w, h in spec.get("walls", []):
        x, y, pw, ph = _px(c, r, w, h)
        if ext:
            _facade(s, x, y, pw, ph)
        else:
            pygame.draw.rect(s, PLASTER, (x, y, pw, ph))
            pygame.draw.rect(s, PLASTER_D, (x, y, pw, ph), 2)


def draw_treatments(s, spec):
    for t in spec.get("treatments", []):
        c, r, w, h = t["rect"]
        x, y, pw, ph = _px(c, r, w, h)
        if t.get("style", "panel") == "panel":
            _panel(s, x, y, pw, ph, w < h)
        else:
            pygame.draw.rect(s, _OBJ_COL.get(t.get("palette"), PLASTER), (x, y, pw, ph))


# ── doors ────────────────────────────────────────────────────────────────────────

def draw_doors(s, spec):
    cols, rows = S.grid_dims(spec)
    for ex in spec.get("exits", {}).values():
        tiles = ex.get("tiles", [])
        if not tiles:
            continue
        cs = [c for c, _ in tiles]
        rs = [c for _, c in tiles]
        vert = min(cs) in (0, cols - 1)
        x, y, pw, ph = _px(min(cs), min(rs), max(cs) - min(cs) + 1, max(rs) - min(rs) + 1)
        style = ex.get("style", "timber")
        if style in ("glazed", "bifold"):
            n = max(2, (ph if vert else pw) // (TILE // 2))
            pygame.draw.rect(s, OAKD, (x, y, pw, ph))
            for i in range(n):
                gx = x + (0 if vert else i * pw // n) + 3
                gy = y + (i * ph // n if vert else 0) + 3
                gw, gh = (pw - 6 if vert else pw // n - 5), (ph // n - 5 if vert else ph - 6)
                _rrect(s, GLASS, (gx, gy, gw, gh), 2, OAKD2, 2)
        else:
            pygame.draw.rect(s, OAKD, (x, y, pw, ph))
            inset = (x + 5, y + 5, pw - 10, ph - 10)
            _rrect(s, OAKD2, inset, 3, BRASS, 1)
            pygame.draw.circle(s, BRASS, (x + pw - 9 if vert else x + pw // 2, y + ph // 2), 4)


# ── furniture / fittings ───────────────────────────────────────────────────────

def _fp_px(o):
    """Footprint polygon in pixels (true chamfered/rotated shape), or None."""
    fp = o.get("footprint")
    if not fp:
        return None
    return [(px * TILE, py * TILE) for px, py in S._footprint_polygon(fp)]


def _longest_edge(poly):
    best, bl = (poly[0], poly[1]), -1.0
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d > bl:
            best, bl = (a, b), d
    return best


def draw_bar(s, o):
    poly = _fp_px(o)
    base = _basecol(o, OAKD)
    if poly:   # true canted/curved peninsula — complete sprite: back-bar + counter + pumps
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1, y0 = min(xs), max(xs), min(ys)
        pygame.draw.polygon(s, base, poly)
        pygame.draw.polygon(s, OAKD2, poly, 3)
        # back-bar shelving (bottles + etched mirror) along the WALL edge (the top/back band)
        pygame.draw.rect(s, OAKD2, (int(x0) + 4, int(y0) + 2, int(x1 - x0) - 8, 12))
        for i, bx in enumerate(range(int(x0) + 8, int(x1) - 6, 7)):
            pygame.draw.rect(s, BOTTLES[i % 4], (bx, int(y0) + 3, 4, 8))
        pygame.draw.rect(s, MIRROR, (int(x0) + 10, int(y0) + 4, 26, 5))
        # cask pumps along the FRONT (the longest edge that isn't the back/wall band)
        edges = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
        front = max((e for e in edges if (e[0][1] + e[1][1]) / 2 > y0 + 4),
                    key=lambda e: math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]),
                    default=_longest_edge(poly))
        (ax, ay), (bx, by) = front
        n = max(2, int(math.hypot(bx - ax, by - ay) // 14))
        for i in range(1, n):
            px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            pygame.draw.circle(s, BRASS, (int(px), int(py)), 4)
            pygame.draw.circle(s, BRASSD, (int(px), int(py)), 4, 1)
        return
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    _rrect(s, base, (x, y, pw, ph), 5, OAKD2, 2)
    for px in range(x + 8, x + pw - 14, 28):   # raised panels
        _rrect(s, _lt(base, 10), (px, y + 6, 20, ph - 12), 3, OAKD2, 1)
    pygame.draw.line(s, BRASS, (x + 3, y + ph - 4), (x + pw - 3, y + ph - 4), 3)  # foot rail
    for px in range(x + 12, x + pw - 8, 16):   # pump bank
        pygame.draw.rect(s, BRASSD, (px, y + 4, 5, 12))
        pygame.draw.circle(s, BRASS, (px + 2, y + 4), 4)


def draw_gantry(s, o):
    poly = _fp_px(o)
    if poly:
        pygame.draw.polygon(s, OAKD2, poly)
        pygame.draw.polygon(s, BRASSD, poly, 2)
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        mx, my = (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
        pygame.draw.rect(s, MIRROR, (mx - 14, my - 5, 28, 10))   # etched mirror
        return
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    pygame.draw.rect(s, OAKD2, (x, y, pw, ph))
    _rrect(s, MIRROR, (x + 6, y + ph // 2 - 4, pw - 12, ph // 2), 2, BRASS, 2)
    for sy in range(y + 6, y + ph // 2, 11):   # bottle shelves
        pygame.draw.line(s, BRASSD, (x + 4, sy + 9), (x + pw - 4, sy + 9), 2)
        for i, bx in enumerate(range(x + 6, x + pw - 5, 7)):
            pygame.draw.rect(s, BOTTLES[i % 4], (bx, sy, 4, 9))


def _one_chair(s, px, py, horiz, outward, col):
    sw, sh = (20, 16) if horiz else (16, 20)
    _rrect(s, col, (px - sw // 2, py - sh // 2, sw, sh), 3, _dk(col), 1)
    if horiz:   # backrest on the outward edge
        yy = py - sh // 2 if outward < 0 else py + sh // 2 - 4
        pygame.draw.rect(s, _dk(col), (px - sw // 2, yy, sw, 4))
    else:
        xx = px - sw // 2 if outward < 0 else px + sw // 2 - 4
        pygame.draw.rect(s, _dk(col), (xx, py - sh // 2, 4, sh))


def _place_chairs(s, cx, cy, tw, th, n, against, col):
    """Chairs around a table. With `against` (a wall/bench side), all chairs go on the
    OPPOSITE (room) side, spread along it — never on the bench side. Else distribute."""
    hw, hh = tw // 2 + 7, th // 2 + 7
    if against in ("top", "bottom", "left", "right"):
        opp = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}[against]
        horiz = opp in ("top", "bottom")
        span = tw if horiz else th
        for i in range(n):
            d = (i - (n - 1) / 2) * (span / max(1, n))
            if horiz:
                py = cy - hh if opp == "top" else cy + hh
                _one_chair(s, int(cx + d), py, True, -1 if opp == "top" else 1, col)
            else:
                px = cx - hw if opp == "left" else cx + hw
                _one_chair(s, px, int(cy + d), False, -1 if opp == "left" else 1, col)
        return
    spots = [(cx, cy - hh, True, -1), (cx, cy + hh, True, 1),
             (cx - hw, cy, False, -1), (cx + hw, cy, False, 1)]
    for i in range(min(n, 4)):
        px, py, horiz, outward = spots[i]
        _one_chair(s, px, py, horiz, outward, col)


def draw_table(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    against = o.get("against")
    off = {"top": (0, -0.16), "bottom": (0, 0.16), "left": (-0.16, 0),
           "right": (0.16, 0)}.get(against, (0, 0))   # nudge table tight to the bench/wall
    cx, cy = x + pw // 2 + int(off[0] * pw), y + ph // 2 + int(off[1] * ph)
    if o.get("seats"):
        _place_chairs(s, cx, cy, int(pw * 0.62), int(ph * 0.62), int(o["seats"]), against, CHAIR)
    top = _basecol(o, TBL)
    tw, th = int(pw * 0.62), int(ph * 0.62)
    if o.get("shape") == "round":   # bistro / cast-iron pedestal table
        rad = min(tw, th) // 2
        pygame.draw.rect(s, LEG, (cx - 2, cy - 2, 4, 4))            # pedestal foot
        gfxdraw.filled_circle(s, cx, cy, rad, top)
        gfxdraw.aacircle(s, cx, cy, rad, TBL_D)
        return
    for lx, ly in [(cx - tw // 2, cy - th // 2), (cx + tw // 2 - 5, cy - th // 2),
                   (cx - tw // 2, cy + th // 2 - 5), (cx + tw // 2 - 5, cy + th // 2 - 5)]:
        pygame.draw.rect(s, LEG, (lx, ly, 5, 5))
    _rrect(s, top, (cx - tw // 2, cy - th // 2, tw, th), 4, TBL_D, 2)
    for gx in range(cx - tw // 2 + 5, cx + tw // 2 - 4, 7):   # grain
        pygame.draw.line(s, _dk(top, 12), (gx, cy - th // 2 + 4), (gx, cy + th // 2 - 4))


def draw_poseur(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    cx, cy = x + pw // 2, y + ph // 2
    pygame.draw.circle(s, OAKD2, (cx, cy), int(pw * 0.32))
    pygame.draw.circle(s, _basecol(o, OAKD), (cx, cy), int(pw * 0.28))
    pygame.draw.circle(s, BRASSD, (cx, cy), int(pw * 0.28), 2)


def draw_chair(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    cx, cy = x + pw // 2, y + ph // 2
    sw = int(pw * 0.5)
    _rrect(s, CHAIR, (cx - sw // 2, cy - sw // 2, sw, sw), 3, CHAIR_D, 1)
    pygame.draw.rect(s, CHAIR_D, (cx - sw // 2, cy - sw // 2, sw, 4))


def draw_armchair(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    aw = int(pw * 0.66)
    rx = x + (pw - aw) // 2
    _rrect(s, LEATHER, (rx, y + 6, aw, ph - 12), 6, LEATHER_D, 2)
    pygame.draw.rect(s, LEATHER_D, (rx, y + 6, 6, ph - 12), border_radius=4)        # arms
    pygame.draw.rect(s, LEATHER_D, (rx + aw - 6, y + 6, 6, ph - 12), border_radius=4)


def draw_banquette(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    col = _basecol(o, MUSTARD)
    pygame.draw.rect(s, _dk(col, 22), (x, y, pw, ph))           # back
    seat = (x + 3, y + ph // 3, pw - 6, ph - ph // 3 - 3)
    _rrect(s, col, seat, 5, _dk(col, 30), 2)
    for bx in range(x + 12, x + pw - 8, 18):                    # buttoning
        pygame.draw.circle(s, _dk(col, 30), (bx, y + ph // 3 + (ph - ph // 3) // 2), 2)


def draw_fireplace(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    sur = _basecol(o, FTEAL)
    pygame.draw.rect(s, sur, (x, y, pw, ph))
    pygame.draw.rect(s, _dk(sur, 24), (x, y, pw, ph), 2)
    _rrect(s, MIRROR, (x + 8, y + 5, pw - 16, ph // 2 - 4), 2, BRASSD, 2)   # over-mantel
    fb = (x + pw // 4, y + ph - ph // 3, pw // 2, ph // 3 - 3)
    pygame.draw.rect(s, FIREBOX, fb)
    pygame.draw.rect(s, EMBER, (fb[0] + 4, fb[1] + fb[3] - 6, fb[2] - 8, 4))


def _leaded(s, x, y, w, h, stained):
    pygame.draw.rect(s, _dk(GLASS, 30), (x, y, w, h))
    cols = max(2, w // 12)
    rows = max(2, h // 12)
    cw, ch = w // cols, h // rows
    for i in range(cols):
        for j in range(rows):
            gx, gy = x + i * cw, y + j * ch
            if stained and (i + j) % 3 == 0:
                col = STAIN[(i + j) % 3]
            else:
                col = AMBER if (i + j) % 4 == 0 else GLASS
            pygame.draw.rect(s, col, (gx + 1, gy + 1, cw - 1, ch - 1))
            pygame.draw.rect(s, LEAD, (gx, gy, cw, ch), 1)
    pygame.draw.rect(s, OAKD2, (x, y, w, h), 2)


def draw_window(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    _leaded(s, x + 2, y + 2, pw - 4, ph - 4, o.get("palette") == "stained")


def draw_column(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    cx, cy = x + pw // 2, y + ph // 2
    rad = int(pw * 0.34)
    gfxdraw.filled_circle(s, cx, cy, rad, PLASTER)
    gfxdraw.aacircle(s, cx, cy, rad, PLASTER_D)
    gfxdraw.aacircle(s, cx - 2, cy - 2, rad - 3, _lt(PLASTER, 12))


def draw_frame(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    cols = [(168, 84, 70), (96, 112, 150), (206, 186, 128), (122, 142, 112), (170, 150, 182)]
    n = max(1, pw // 26)
    for i in range(n):
        fx = x + 6 + i * (pw // n)
        _rrect(s, MOUNT, (fx, y + 8, pw // n - 8, ph - 16), 1, FRAME, 3)
        pygame.draw.rect(s, cols[i % len(cols)], (fx + 4, y + 12, pw // n - 16, ph - 24))


def draw_fallback(s, o):
    c, r, w, h = o["rect"]
    x, y, pw, ph = _px(c, r, w, h)
    base = _basecol(o, (138, 124, 106))
    sh = o.get("shape")
    if sh == "round" or sh == "planted":
        cx, cy = x + pw // 2, y + ph // 2
        gfxdraw.filled_ellipse(s, cx, cy, pw // 2 - 3, ph // 2 - 3, base)
        gfxdraw.aaellipse(s, cx, cy, pw // 2 - 3, ph // 2 - 3, _dk(base))
    else:
        _rrect(s, base, (x + 3, y + 3, pw - 6, ph - 6), 4, _dk(base), 2)


_DRAW = {
    "bar": draw_bar, "backbar": draw_gantry, "fireplace": draw_fireplace,
    "banquette": draw_banquette, "table": draw_table, "poseur": draw_poseur,
    "column": draw_column, "chair": draw_chair, "armchair": draw_armchair,
    "window": draw_window, "bay": draw_window, "frame": draw_frame,
}


def draw_overlays(s, ov, spec):
    for reg in spec.get("regions", []):
        if reg.get("overlay") != "glazed_roof":
            continue
        c, r, w, h = reg["rect"]
        x, y, pw, ph = _px(c, r, w, h)
        for yy in range(y + 10, y + ph, 22):
            pygame.draw.rect(ov, (110, 80, 50, 90), (x, yy, pw, 4))   # timber rafters
        for xx in range(x + TILE, x + pw, TILE):
            pygame.draw.rect(ov, (160, 190, 200, 40), (xx - 2, y, 4, ph))   # glass sheen


def draw_lights(s, ov, spec):
    for li in spec.get("lights", []):
        c, r = li["at"]
        cx, cy = c * TILE + TILE // 2, r * TILE + TILE // 2
        if li.get("type") == "lantern":
            pygame.draw.rect(s, OAKD2, (cx - 7, cy - 9, 14, 16), 2)
            pygame.draw.rect(s, SCONCE, (cx - 4, cy - 6, 8, 10))
        else:
            pygame.draw.line(s, BRASSD, (cx, cy - 20), (cx, cy - 8), 2)
            gfxdraw.filled_circle(s, cx, cy - 4, 6, SCONCE)
            gfxdraw.aacircle(s, cx, cy - 4, 6, BRASS)
        for rr in range(int(TILE * 0.3), 5, -9):   # subtle warm halo, must not wash out
            layer = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(layer, (255, 226, 156, 4), (cx, cy - 3), rr)
            ov.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def render(spec):
    cols, rows = S.grid_dims(spec)
    s = pygame.Surface((cols * TILE, rows * TILE))
    s.fill((18, 16, 14))
    kind = spec.get("meta", {}).get("kind", "interior")
    for reg in spec.get("regions", []):
        _floor(s, reg)
    draw_walls(s, spec, kind)
    draw_treatments(s, spec)
    draw_doors(s, spec)
    for blocking in (True, False):
        for o in spec.get("objects", []):
            if o.get("blocks", True) != blocking:
                continue
            (_DRAW.get(o.get("type")) or draw_fallback)(s, o)
    ov = pygame.Surface((cols * TILE, rows * TILE), pygame.SRCALPHA)
    draw_overlays(s, ov, spec)
    draw_lights(s, ov, spec)
    s.blit(ov, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return pygame.transform.smoothscale(s, (cols * TILE // SS, rows * TILE // SS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    args = ap.parse_args()
    pygame.init()
    spec = S.load(S.spec_path(args.slug))
    surf = render(spec)
    out = REPO_ROOT / "refs" / args.slug / "_render" / "detail.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(out))
    print("  -> %s %s" % (out.relative_to(REPO_ROOT), surf.get_size()))


if __name__ == "__main__":
    main()
