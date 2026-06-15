"""In-game-fidelity preview render of a scene_spec (for sign-off before wiring).

Draws at the real game resolution (cols*tile x rows*tile) with per-type art, so it
looks roughly like the scene would in-game. Saved 2x for legibility.

SPEC-DRIVEN, place-agnostic:
  - floors    from region `material` (wood/slate/tile/carpet/grass/concrete/cobble/...)
  - walls     interior plaster, OR building facades when meta.kind is exterior/street;
              cosmetic `treatments` can overlay panel/tile/brick/facade
  - doors     drawn from `exits[*].tiles` on WHICHEVER edge they sit; `style` per exit
  - objects   dispatched by `type` (bespoke art); else by a generic `shape` hint
              (round/tall/low/planted); else a labelled fallback box — never dropped
  - feature colours come from each object's `palette`, not its id

Run: SDL_VIDEODRIVER=dummy python3 $SK/render_ingame.py <slug>
Out: refs/<slug>/_render/ingame.png
"""
import argparse
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

import spec as S  # type: ignore  # noqa: E402

REPO_ROOT = S.REPO_ROOT

# ── palette ──────────────────────────────────────────────────────────────────
_PLASTER, _PLASTER_DK = (214, 208, 196), (150, 144, 132)
_BARW, _BARDK, _BARTOP = (74, 50, 30), (48, 32, 18), (96, 70, 44)
_BRASS, _BRASSDK, _MIRROR = (206, 184, 122), (168, 148, 92), (184, 198, 206)
_BOTTLES = [(40, 92, 60), (162, 110, 48), (188, 202, 212), (150, 60, 60)]
_TABLE, _TABLE_DK, _CHAIR = (158, 122, 76), (132, 100, 60), (120, 90, 56)
_LEATHER, _LEATHER_DK = (150, 88, 52), (122, 68, 38)
_GLASS, _GLASS_HI, _GLASS_DK = (168, 188, 200), (200, 216, 224), (130, 150, 164)
_STAIN = [(180, 45, 55), (55, 135, 85), (65, 95, 160), (220, 195, 85)]
_MOUNT, _SCONCE, _IRON = (250, 246, 238), (250, 232, 180), (45, 45, 48)
_FALLBACK, _FALLBACK_DK = (122, 110, 96), (88, 78, 66)
_FACADE, _FACADE_DK, _FACADE_WIN = (150, 96, 72), (118, 72, 52), (208, 200, 152)

# material -> (base colour, texture style)
_MATERIAL = {
    "wood":     ((172, 140, 92), "planks"),
    "slate":    ((96, 102, 108), "courses"),
    "tile":     ((206, 200, 188), "grid"),
    "carpet":   ((128, 70, 70), "flat"),
    "grass":    ((96, 128, 72), "speckle"),
    "concrete": ((150, 150, 150), "flat"),
    "cobble":   ((120, 120, 124), "cobble"),
    "asphalt":  ((70, 72, 76), "flat"),
    "paving":   ((180, 178, 170), "grid"),
}
# named palettes for typed objects (fireplace, banquette, ...) via the spec `palette` field
_OBJ_PALETTE = {
    "cream":   ((224, 216, 202), (196, 186, 168)),
    "teal":    ((44, 74, 70), (32, 56, 52)),
    "mustard": ((192, 152, 72), (160, 122, 52)),
    "tartan":  ((150, 90, 84), (120, 64, 60)),
    "green":   ((88, 110, 78), (66, 86, 58)),
    "oak":     ((120, 84, 48), (90, 62, 34)),
    "dark":    ((60, 44, 30), (40, 30, 20)),
    "brass":   ((190, 160, 96), (150, 124, 70)),
    "_":       ((150, 134, 108), (110, 96, 72)),
}
# keys here must stay in sync with render.py's _PALETTE so an object's `palette` reads the
# same in the plan and in-game renders. ('stained' is a window/bay-only flag, not a fill.)

_FONT = None


def _font(sz=9):
    global _FONT
    if _FONT is None or _FONT[0] != sz:
        _FONT = (sz, pygame.font.SysFont("helveticaneue,arial", sz, bold=True))
    return _FONT[1]


def _dk(c, n=26):
    return tuple(max(0, v - n) for v in c)


def _pal(o):
    return _OBJ_PALETTE.get(o.get("palette", "_"), _OBJ_PALETTE["_"])


# ── floors ───────────────────────────────────────────────────────────────────

def draw_floor(s, spec, TS):
    for reg in spec.get("regions", []):
        c, r, w, h = reg["rect"]
        x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
        base, style = _MATERIAL.get(reg.get("material", "wood"), _MATERIAL["wood"])
        pygame.draw.rect(s, base, (x, y, pw, ph))
        if style == "planks":
            for i, xx in enumerate(range(x, x + pw, 11)):
                if i % 2:
                    pygame.draw.rect(s, _dk(base, 10), (xx, y, 11, ph))
                pygame.draw.line(s, _dk(base, 26), (xx, y), (xx, y + ph))
        elif style in ("courses", "cobble"):
            step = 16 if style == "courses" else 14
            for ci, yy in enumerate(range(y, y + ph, step)):
                pygame.draw.line(s, _dk(base, 22), (x, yy), (x + pw, yy))
                off = (ci * 13) % 30
                for xx in range(x - off, x + pw, 30):
                    pygame.draw.line(s, _dk(base, 22), (max(x, xx), yy),
                                     (max(x, xx), min(y + ph, yy + step)))
        elif style == "grid":
            for yy in range(y, y + ph, 16):
                pygame.draw.line(s, _dk(base, 16), (x, yy), (x + pw, yy))
            for xx in range(x, x + pw, 16):
                pygame.draw.line(s, _dk(base, 16), (xx, y), (xx, y + ph))
        elif style == "speckle":
            for i in range(x, x + pw, 7):
                for j in range(y, y + ph, 7):
                    if (i + j) // 7 % 3 == 0:
                        pygame.draw.rect(s, _dk(base, 18), (i, j, 3, 3))


# ── walls + cosmetic treatments ──────────────────────────────────────────────

def _facade(s, x, y, w, h):
    """A building frontage (for exterior/street scenes): brick + a band of lit windows."""
    pygame.draw.rect(s, _FACADE, (x, y, w, h))
    for ci, yy in enumerate(range(y, y + h, 6)):
        pygame.draw.line(s, _FACADE_DK, (x, yy), (x + w, yy))
        off = (ci % 2) * 5
        for xx in range(x - off, x + w, 10):
            pygame.draw.line(s, _FACADE_DK, (max(x, xx), yy), (max(x, xx), min(y + h, yy + 6)))
    if w >= h:  # horizontal frontage -> windows along a mid band
        wy, wh = y + max(2, h // 3), min(10, max(4, h // 2))
        for wx in range(x + 6, x + w - 8, 22):
            pygame.draw.rect(s, _FACADE_DK, (wx - 1, wy - 1, 12, wh + 2))
            pygame.draw.rect(s, _FACADE_WIN, (wx, wy, 10, wh))
    else:       # vertical frontage -> windows stacked
        wx, ww2 = x + max(2, w // 3), min(10, max(4, w // 2))
        for wy in range(y + 6, y + h - 8, 22):
            pygame.draw.rect(s, _FACADE_DK, (wx - 1, wy - 1, ww2 + 2, 12))
            pygame.draw.rect(s, _FACADE_WIN, (wx, wy, ww2, 10))
    pygame.draw.rect(s, _FACADE_DK, (x, y, w, h), 2)


def draw_walls(s, spec, TS, kind="interior"):
    exterior = kind in ("exterior", "street")
    for w in spec.get("walls", []):
        c, r, ww, hh = w
        x, y, pw, ph = c * TS, r * TS, ww * TS, hh * TS
        if exterior:
            _facade(s, x, y, pw, ph)
        else:
            pygame.draw.rect(s, _PLASTER, (x, y, pw, ph))
            pygame.draw.rect(s, _PLASTER_DK, (x, y, pw, ph), 2)


def _treat_panel(s, x, y, w, h, vertical, pal):
    upper, lower = _PLASTER, pal[0]
    if vertical:
        split = w * 2 // 5
        pygame.draw.rect(s, upper, (x, y, split, h))
        pygame.draw.rect(s, lower, (x + split, y, w - split, h))
        pygame.draw.line(s, pal[1], (x + split, y), (x + split, y + h), 2)
    else:
        split = h * 2 // 5
        pygame.draw.rect(s, upper, (x, y, w, split))
        pygame.draw.rect(s, lower, (x, y + split, w, h - split))
        pygame.draw.line(s, pal[1], (x, y + split), (x + w, y + split), 2)
        for px in range(x + 5, x + w - 8, 26):
            pygame.draw.rect(s, pal[1], (px, y + split + 5, 20, h - split - 10), 1)


def draw_treatments(s, spec, TS):
    """Optional cosmetic wall finishes — opt-in, never assumed."""
    for t in spec.get("treatments", []):
        c, r, w, h = t["rect"]
        x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
        style = t.get("style", "panel")
        pal = _OBJ_PALETTE.get(t.get("palette", "oak"), _OBJ_PALETTE["oak"])
        if style == "panel":
            _treat_panel(s, x, y, pw, ph, w < h, pal)
        elif style in ("tile", "brick"):
            pygame.draw.rect(s, pal[0], (x, y, pw, ph))
            step = 12 if style == "tile" else 10
            for ci, yy in enumerate(range(y, y + ph, step)):
                pygame.draw.line(s, pal[1], (x, yy), (x + pw, yy))
                off = (ci % 2) * (step // 2) if style == "brick" else 0
                for xx in range(x - off, x + pw, step + 6):
                    pygame.draw.line(s, pal[1], (max(x, xx), yy),
                                     (max(x, xx), min(y + ph, yy + step)))
        elif style == "facade":
            pygame.draw.rect(s, pal[0], (x, y, pw, ph))
            pygame.draw.rect(s, pal[1], (x, y, pw, ph), 2)


# ── doors (from exits, on any edge) ──────────────────────────────────────────

def _edge_runs(spec):
    """Group each exit's tiles by which border edge they touch -> drawable door runs."""
    cols, rows = S.grid_dims(spec)
    runs = []
    for ex in spec.get("exits", {}).values():
        for edge in ("west", "east", "north", "south"):
            sel = []
            for (c, r) in ex.get("tiles", []):
                if (edge == "west" and c == 0) or (edge == "east" and c == cols - 1) \
                        or (edge == "north" and r == 0) or (edge == "south" and r == rows - 1):
                    sel.append((c, r))
            if sel:
                runs.append((edge, sel, ex.get("style", "timber")))
    return runs


def _door(s, rect, style, vertical):
    x, y, w, h = rect
    if style == "open":
        pygame.draw.rect(s, _dk(_BARDK, 10), (x, y, w, h))
        return
    pygame.draw.rect(s, _BARDK, (x, y, w, h))
    if style in ("glazed", "bifold", "stained"):
        cols_n = max(2, (w // 10) if not vertical else 1)
        rows_n = max(2, (h // 10) if vertical else 1)
        gw, gh = max(2, w // cols_n), max(2, h // rows_n)
        for i in range(cols_n):
            for j in range(rows_n):
                gx, gy = x + 2 + i * gw, y + 2 + j * gh
                if style == "stained":
                    pygame.draw.rect(s, _STAIN[(i + j) % 4], (gx, gy, gw - 3, gh - 3))
                else:
                    pygame.draw.rect(s, _GLASS, (gx, gy, gw - 3, gh - 3))
                    pygame.draw.rect(s, _GLASS_HI, (gx, gy, (gw - 3) // 2, (gh - 3) // 2))
    else:  # timber
        pygame.draw.rect(s, _BARW, (x + 2, y + 2, w - 4, h - 4))
        pygame.draw.rect(s, _BRASS, (x + w - 5 if vertical else x + w // 2,
                                     y + h // 2, 3, 3))


def draw_doors(s, spec, TS):
    cols, rows = S.grid_dims(spec)
    for edge, sel, style in _edge_runs(spec):
        if edge in ("west", "east"):
            rs = sorted(r for _, r in sel)
            y0, h = rs[0] * TS, (rs[-1] - rs[0] + 1) * TS
            x0 = 0 if edge == "west" else (cols - 1) * TS + 4
            _door(s, (x0, y0, TS - 4, h), style, vertical=True)
        else:
            cs = sorted(c for c, _ in sel)
            x0, w = cs[0] * TS, (cs[-1] - cs[0] + 1) * TS
            y0 = 0 if edge == "north" else (rows - 1) * TS + 4
            _door(s, (x0, y0, w, TS - 4), style, vertical=False)


# ── typed object art ─────────────────────────────────────────────────────────

def _fp_px(o, TS):
    fp = o.get("footprint")
    return [(px * TS, py * TS) for px, py in S._footprint_polygon(fp)] if fp else None


def draw_bar(s, o, TS):
    poly = _fp_px(o, TS)
    if poly:   # true chamfered/free-standing shape (matches collision + detail render)
        pygame.draw.polygon(s, _BARW, poly)
        pygame.draw.polygon(s, _BARDK, poly, 2)
        return
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    pygame.draw.rect(s, _BARW, (x, y, pw, ph))
    pygame.draw.rect(s, _BARDK, (x, y, pw, ph), 2)
    pygame.draw.rect(s, _BARTOP, (x, y, pw, 5))
    pygame.draw.line(s, _BRASS, (x + 2, y + ph - 3), (x + pw - 2, y + ph - 3), 2)
    for px in range(x + 8, x + pw - 6, 12):
        pygame.draw.rect(s, _BRASSDK, (px, y + ph - 9, 4, 8))
        pygame.draw.circle(s, _BRASS, (px + 2, y + ph - 10), 3)


def draw_gantry(s, o, TS):
    poly = _fp_px(o, TS)
    if poly:
        pygame.draw.polygon(s, _BARDK, poly)
        pygame.draw.polygon(s, _BRASSDK, poly, 2)
        return
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    pygame.draw.rect(s, _BARDK, (x, y, pw, ph))
    pygame.draw.rect(s, _BARW, (x + 2, y + 2, pw - 4, ph - 4))
    for sy in range(y + 6, y + ph - 4, 9):
        pygame.draw.line(s, _BRASSDK, (x + 3, sy), (x + pw - 3, sy))
        for i, bx in enumerate(range(x + 4, x + pw - 4, 5)):
            pygame.draw.rect(s, _BOTTLES[i % 4], (bx, sy - 5, 3, 5))
    pygame.draw.rect(s, _MIRROR, (x + 5, y + ph // 2 - 3, pw - 10, 6))


def draw_fireplace(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    body, body_dk = _pal(o)
    pygame.draw.rect(s, body_dk, (x, y, pw, ph))
    pygame.draw.rect(s, body, (x + 2, y + 2, pw - 4, ph - 4))
    pygame.draw.rect(s, _BRASSDK, (x + 5, y + 4, pw - 10, ph // 2), 2)
    pygame.draw.rect(s, _MIRROR, (x + 6, y + 5, pw - 12, ph // 2 - 2))
    pygame.draw.rect(s, _BARDK, (x + 5, y + ph - 10, pw - 10, 8))
    pygame.draw.rect(s, (150, 70, 40), (x + 8, y + ph - 8, pw - 16, 5))


def draw_banquette(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    col, col_dk = _pal(o)
    pygame.draw.rect(s, col_dk, (x, y, pw, ph))
    pygame.draw.rect(s, col, (x + 2, y + 2, pw - 4, ph - 5))
    step = TS if w >= h else TS
    for cx in range(x + step, x + pw, step):
        pygame.draw.line(s, col_dk, (cx, y + 2), (cx, y + ph - 3))


def draw_table(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 3, r * TS + 3, w * TS - 6, h * TS - 6
    pygame.draw.rect(s, _TABLE, (x, y, pw, ph))
    pygame.draw.rect(s, _TABLE_DK, (x, y, pw, ph), 1)


def draw_poseur(s, o, TS):
    c, r, w, h = o["rect"]
    cx, cy = c * TS + TS // 2, r * TS + TS // 2
    pygame.draw.rect(s, _BARDK, (cx - 9, cy - 9, 18, 18))
    pygame.draw.rect(s, _BARW, (cx - 7, cy - 7, 14, 14))
    pygame.draw.rect(s, _BARTOP, (cx - 7, cy - 7, 14, 3))


def draw_column(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    base, base_dk = _pal(o) if o.get("palette") else (_PLASTER, _PLASTER_DK)
    pygame.draw.rect(s, base, (x + 6, y + 2, pw - 12, ph - 4))
    pygame.draw.rect(s, base_dk, (x + 6, y + 2, pw - 12, ph - 4), 2)


def draw_chair(s, o, TS):
    c, r, w, h = o["rect"]
    cx, cy = c * TS + TS // 2, r * TS + TS // 2
    pygame.draw.rect(s, _CHAIR, (cx - 5, cy - 5, 10, 10))
    pygame.draw.rect(s, _dk(_CHAIR), (cx - 5, cy - 5, 10, 10), 1)


def draw_armchair(s, o, TS):
    c, r, w, h = o["rect"]
    x, y = c * TS + 4, r * TS + 5
    pygame.draw.rect(s, _LEATHER, (x, y, TS - 8, TS - 10))
    pygame.draw.rect(s, _LEATHER_DK, (x, y, TS - 8, TS - 10), 2)


def draw_window(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 2, r * TS + 2, w * TS - 4, h * TS - 4
    stained = o.get("palette") == "stained"
    pygame.draw.rect(s, _GLASS_DK, (x, y, pw, ph))
    cells = 3
    cw = max(2, (pw - 4) // cells)
    for i in range(cells):
        col = _STAIN[i % 4] if stained else (_GLASS if i % 2 else _GLASS_HI)
        pygame.draw.rect(s, col, (x + 2 + i * cw, y + 2, cw - 1, ph - 4))
    pygame.draw.rect(s, _dk(_GLASS_DK, 40), (x, y, pw, ph), 1)


def draw_frame(s, o, TS):
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 4, r * TS + 4, w * TS - 8, h * TS - 8
    pygame.draw.rect(s, _MOUNT, (x - 1, y - 1, pw + 2, ph + 2))
    body = _pal(o)[0]
    pygame.draw.rect(s, body, (x, y, pw, ph))
    pygame.draw.rect(s, _dk(body, 30), (x, y, pw, max(2, ph // 3)))


def _label(s, x, y, o):
    lab = o.get("label") or o.get("type") or "?"
    s.blit(_font(9).render(lab[:14], True, _MOUNT), (x + 2, y + 2))


def _shape_cols(o, default=None):
    return _pal(o) if o.get("palette") else (default or (_FALLBACK, _FALLBACK_DK))


def draw_fallback(s, o, TS):
    """A type with neither bespoke art nor a `shape`: a labelled box, never silently dropped."""
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 2, r * TS + 2, w * TS - 4, h * TS - 4
    base, base_dk = _shape_cols(o)
    pygame.draw.rect(s, base, (x, y, pw, ph))
    pygame.draw.rect(s, base_dk, (x, y, pw, ph), 2)
    _label(s, x, y, o)


def draw_shape_round(s, o, TS):     # fountain, roundabout, planter, drum
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 2, r * TS + 2, w * TS - 4, h * TS - 4
    base, base_dk = _shape_cols(o)
    pygame.draw.ellipse(s, base, (x, y, pw, ph))
    pygame.draw.ellipse(s, base_dk, (x, y, pw, ph), 2)
    _label(s, x, y, o)


def draw_shape_tall(s, o, TS):      # column, lamppost, bollard, post, tree trunk
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    base, base_dk = _shape_cols(o)
    bw = max(6, pw // 3)
    pygame.draw.rect(s, base, (x + (pw - bw) // 2, y + 2, bw, ph - 4))
    pygame.draw.rect(s, base_dk, (x + (pw - bw) // 2, y + 2, bw, ph - 4), 2)
    _label(s, x, y, o)


def draw_shape_low(s, o, TS):       # bench, kerb, low wall, counter, pew
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS, r * TS, w * TS, h * TS
    base, base_dk = _shape_cols(o)
    bh = max(6, ph // 3)
    pygame.draw.rect(s, base, (x + 2, y + (ph - bh) // 2, pw - 4, bh))
    pygame.draw.rect(s, base_dk, (x + 2, y + (ph - bh) // 2, pw - 4, bh), 2)
    _label(s, x, y, o)


def draw_shape_planted(s, o, TS):   # tree, shrub, planter bed (green by default)
    c, r, w, h = o["rect"]
    x, y, pw, ph = c * TS + 1, r * TS + 1, w * TS - 2, h * TS - 2
    base, base_dk = _shape_cols(o, default=_OBJ_PALETTE["green"])
    pygame.draw.ellipse(s, base, (x, y, pw, ph))
    pygame.draw.ellipse(s, base_dk, (x, y, pw, ph), 2)
    _label(s, x, y, o)


# generic shape primitives for non-pub objects, chosen via the spec's `shape` hint, so a
# fountain/tree/altar/counter reads as a distinct silhouette rather than an identical box
_SHAPE = {"round": draw_shape_round, "tall": draw_shape_tall, "low": draw_shape_low,
          "planted": draw_shape_planted, "box": draw_fallback}


_DRAW = {
    "bar": draw_bar, "backbar": draw_gantry, "fireplace": draw_fireplace,
    "banquette": draw_banquette, "table": draw_table, "poseur": draw_poseur,
    "column": draw_column, "chair": draw_chair, "armchair": draw_armchair,
    "window": draw_window, "bay": draw_window, "frame": draw_frame,
}


def draw_lights(s, ov, spec, TS):
    for li in spec.get("lights", []):
        c, r = li["at"]
        cx, cy = c * TS + TS // 2, r * TS + TS // 2
        if li.get("type") == "lantern":
            pygame.draw.rect(s, _IRON, (cx - 4, cy - 6, 8, 10), 1)
            pygame.draw.rect(s, _SCONCE, (cx - 2, cy - 4, 4, 6))
        else:
            pygame.draw.line(s, _BRASSDK, (cx, cy - 13), (cx, cy - 6))
            pygame.draw.circle(s, _SCONCE, (cx, cy - 4), 4)
            pygame.draw.circle(s, _BRASS, (cx, cy - 4), 4, 1)
        for rr in range(13, 3, -4):
            layer = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(layer, (255, 224, 150, 4), (cx, cy - 3), rr)
            ov.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_overlays(s, ov, spec, TS):
    """Region-level opt-in overlays, e.g. a glazed pitched roof. Never inferred."""
    for reg in spec.get("regions", []):
        if reg.get("overlay") != "glazed_roof":
            continue
        c, r, w, h = reg["rect"]
        x0, x1, y0, y1 = c * TS, (c + w) * TS, r * TS, (r + h) * TS
        beam = (92, 64, 38, 110)
        for yy in range(y0 + 8, y1, 16):
            pygame.draw.rect(ov, beam, (x0, yy, x1 - x0, 3))
        for xx in range(x0 + TS, x1, TS):
            pygame.draw.rect(ov, beam, (xx - 1, y0, 3, y1 - y0))


def render(spec):
    cols, rows = S.grid_dims(spec)
    TS = spec["grid"].get("tile", 32)
    s = pygame.Surface((cols * TS, rows * TS))
    s.fill((0, 0, 0))
    kind = spec.get("meta", {}).get("kind", "interior")
    draw_floor(s, spec, TS)
    draw_walls(s, spec, TS, kind)
    draw_treatments(s, spec, TS)
    draw_doors(s, spec, TS)
    for blocking in (True, False):  # solid features first, loose items on top
        for o in spec.get("objects", []):
            if o.get("blocks", True) != blocking:
                continue
            # bespoke type art > generic `shape` primitive > labelled box (never dropped)
            fn = _DRAW.get(o.get("type")) or _SHAPE.get(o.get("shape")) or draw_fallback
            fn(s, o, TS)
    ov = pygame.Surface((cols * TS, rows * TS), pygame.SRCALPHA)
    draw_overlays(s, ov, spec, TS)
    draw_lights(s, ov, spec, TS)
    s.blit(ov, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return pygame.transform.scale2x(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    args = ap.parse_args()
    pygame.init()
    spec = S.load(S.spec_path(args.slug))
    problems = S.validate(spec)
    fidelity = S.fidelity_warnings(spec)
    surf = render(spec)
    out = REPO_ROOT / "refs" / args.slug / "_render" / "ingame.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(out))
    print("  -> %s %s" % (out.relative_to(REPO_ROOT), surf.get_size()))
    # Two gates, never conflated. "reachable" is NOT "looks right" — that's the audit + human.
    print("TOPOLOGY: %s (NOT a fidelity check)"
          % ("reachable" if not problems else "%d issue(s)" % len(problems)))
    active, waived = S.partition_waivers(spec, fidelity)
    print("FIDELITY: %s" % ("no active warnings" if not active
                            else "%d active warning(s) — likely guessed, not derived" % len(active)))
    for w in active:
        print("  • " + w)
    for w, why in waived:
        print("  ~ waived: %s  [why: %s]" % (w, why))
    if any(ex.get("derived_from") for ex in spec.get("exits", {}).values()):
        print("NOTE: a `derived_from` names the evidence file, it does NOT prove the door's "
              "tile — door positions are confirmed only by the Phase-3.5 audit, not this gate.")


if __name__ == "__main__":
    main()
