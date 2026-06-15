"""scene_spec — load, validate, and derive geometry for a tile-grid scene.

A scene_spec.json is the single source of truth for a scene's geometry. From it we
derive the blocked-tile set, the walkable-tile set, and a BFS reachability check —
so layout bugs surface before any art is drawn. The same spec drives the plan
render, the in-game render, and (Stage 4) the game's SCENE_CONFIGS.

Schema (v1):
{
  "meta":   {"name", "slug", "scene_id"?, "manifest"?, "notes"?,
             "kind"?: "interior"|"exterior"|"street",   # tunes fidelity_warnings()
             "fidelity_waivers"?: [{"match": str, "why": str}]},  # explicit overrides;
                 # `match` must be a distinctive substring of EXACTLY ONE warning (>=12 chars)
                 # — a broad match becomes an active warning, it can't launder the gate
  "grid":   {"cols": 20, "rows": 15, "tile": 32},
  "regions":[{"rect": [c,r,w,h], "material": str, "label"?, "overlay"?: str}],  # floor
                 # material: wood|slate|tile|carpet|grass|concrete|cobble|asphalt|paving
                 # overlay (opt-in): "glazed_roof"
  "walls":  [[c,r,w,h], ...],                                   # blocked structure (plain)
  "treatments"?:[{"rect":[c,r,w,h], "style": str, "palette"?}], # COSMETIC wall finish,
                 # style: panel|tile|brick|facade — opt-in, never assumed
  "objects":[{"id", "type", "rect": [c,r,w,h], "blocks": bool, "label"?, "palette"?,
              "shape"?, "footprint"?, "cite"?: [str]}],  # cite = photos that place it
                 # footprint (sub-tile shape; collision still tile-based via rasteriser):
                 #   {"pos":[x,y], "size":[w,h] floats in tiles, "angle"?: deg,
                 #    "chamfer"?: {"corner": tl|tr|br|bl, "size": float}}
                 #   OR an explicit polygon: {"poly": [[x,y], ...]} for curved/faceted/L/U
                 #   shapes (e.g. a canted bar that returns to the wall at both ends)
                 #   `rect` MUST equal the footprint's integer bbox (validate() enforces it;
                 #   bounds/floor checks read `rect`, renderers + collision read the footprint).
                 #   Place it off the wall to make a free-standing feature (BFS proves the
                 #   walk-behind). Collision rasterises at ~half-tile resolution, so keep each
                 #   dimension >= ~0.5 tile and treat `angle` as coarse (thin/rotated slivers
                 #   can show in the render but vanish from collision).
                 # type drawn by render_ingame: bar|backbar|fireplace|banquette|table|
                 # poseur|column|chair|armchair|window|bay|frame
                 # shape (for non-pub types w/o bespoke art): round|tall|low|planted|box
                 #   — used when `type` has no art, so a fountain/tree/altar reads as a
                 #   silhouette not a box; unknown + no shape -> labelled box
                 # seats?: int on a table/poseur — chairs drawn around it as one setting
                 #   (the detail render); also counts toward the "tables need seats" check
                 # against?: top|bottom|left|right — table sits tight to that wall/bench and
                 #   chairs are drawn ONLY on the room side. A BANQUETTE RUN = a long
                 #   `banquette` along a wall + `table`s with against=<that wall> in front.
                 # color?: "#rrggbb" real colour read off the cited photo (detail render)
                 # palette (fill, same keys in plan + in-game):
                 #   cream|teal|mustard|tartan|green|oak|dark|brass; window/bay also take
                 #   palette "stained". Seating heuristic also counts stool/bench/settle/desk.
  "exits":  {"<side>": {"to": int, "tiles": [[c,r],...], "label"?, "derived_from"?: str,
              "style"?: str}},     # door style: timber|glazed|bifold|stained|open
  "entry":  {"<side>": [c,r]},                                  # arrival tiles
  "lights"? :[{"type", "at": [c,r]}]
}

Two gates, deliberately separate:
  validate()         — TOPOLOGY ONLY (bounds, floating objects, BFS reachability). Passing
                       means "walkable", never "accurate". This is necessary, not sufficient.
  fidelity_warnings()— FIDELITY heuristics (citations, defaulted exits, furnishing density,
                       wall treatment). Non-fatal, but an unaddressed warning means the
                       layout is probably guessed, not derived. See METHODOLOGY.md.
"""
import json
import math
import re
from collections import Counter, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from common import REPO_ROOT  # type: ignore  # noqa: E402

SPECS_DIR = REPO_ROOT / "specs"

Tile = Tuple[int, int]


def load(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())


def spec_path(slug: str) -> Path:
    return SPECS_DIR / ("%s.scene.json" % slug)


def _rect_tiles(rect: List[int]) -> Set[Tile]:
    c, r, w, h = rect
    return {(c + dc, r + dr) for dc in range(w) for dr in range(h)}


# ── sub-tile footprints ─────────────────────────────────────────────────────────
# A `footprint` lets an object have a float position/size, a rotation and a chamfered
# corner (e.g. an angled free-standing bar), while collision stays strictly tile-based:
# the polygon is rasterised to the integer tiles it covers ≥ _COVER. Movement, BFS, and the
# Phase-4 compile all consume that tile set — one deterministic rasteriser, every gate.
_COVER = 0.5          # a tile is blocked iff the footprint covers >= this fraction of it
_SAMPLES = 4          # NxN fixed sample grid per tile (deterministic; offset off edges)


def _footprint_polygon(fp: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Footprint -> polygon in tile units. Either an explicit `poly` (a vertex list, for
    curved/faceted/L/U shapes — e.g. a canted bar that returns to the wall), or a base rect
    with an optional chamfered corner + rotation."""
    if "poly" in fp:
        return [(float(px), float(py)) for px, py in fp["poly"]]
    x, y = fp["pos"]
    w, h = fp["size"]
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]   # tl, tr, br, bl
    ch = fp.get("chamfer")
    if ch:
        s = float(ch.get("size", 1.0))
        i = {"tl": 0, "tr": 1, "br": 2, "bl": 3}.get(ch.get("corner", "br"), 2)

        def _toward(a, b):
            ax, ay = a
            bx, by = b
            d = math.hypot(bx - ax, by - ay) or 1.0
            return (ax + (bx - ax) / d * s, ay + (by - ay) / d * s)

        poly = []
        for j, p in enumerate(pts):
            if j == i:
                poly.append(_toward(p, pts[(j - 1) % 4]))
                poly.append(_toward(p, pts[(j + 1) % 4]))
            else:
                poly.append(p)
        pts = poly
    ang = float(fp.get("angle", 0))
    if ang:
        cx, cy, a = x + w / 2, y + h / 2, math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        pts = [((px - cx) * ca - (py - cy) * sa + cx,
                (px - cx) * sa + (py - cy) * ca + cy) for px, py in pts]
    return pts


def _in_poly(px: float, py: float, poly: List[Tuple[float, float]]) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[i - 1]
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1):
            inside = not inside
    return inside


def footprint_tiles(fp: Dict[str, Any], cols: int, rows: int) -> Set[Tile]:
    """Deterministic raster of a footprint to the tiles it covers >= _COVER."""
    poly = _footprint_polygon(fp)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    out: Set[Tile] = set()
    need = _COVER * _SAMPLES * _SAMPLES
    for r in range(max(0, int(math.floor(min(ys)))), min(rows, int(math.ceil(max(ys))))):
        for c in range(max(0, int(math.floor(min(xs)))), min(cols, int(math.ceil(max(xs))))):
            hits = sum(_in_poly(c + (i + 0.5) / _SAMPLES, r + (j + 0.5) / _SAMPLES, poly)
                       for i in range(_SAMPLES) for j in range(_SAMPLES))
            if hits >= need:
                out.add((c, r))
    return out


def footprint_bbox(fp: Dict[str, Any]) -> List[int]:
    """Integer tile bounding box of a footprint polygon — must equal the object's `rect`."""
    poly = _footprint_polygon(fp)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    c, r = int(math.floor(min(xs))), int(math.floor(min(ys)))
    return [c, r, int(math.ceil(max(xs))) - c, int(math.ceil(max(ys))) - r]


def grid_dims(spec: Dict[str, Any]) -> Tuple[int, int]:
    g = spec["grid"]
    return g["cols"], g["rows"]


def obj_tiles(o: Dict[str, Any], cols: int, rows: int) -> Set[Tile]:
    """Tiles an object occupies — rasterised footprint if present, else its integer rect."""
    fp = o.get("footprint")
    return footprint_tiles(fp, cols, rows) if fp else _rect_tiles(o["rect"])


def region_tiles(spec: Dict[str, Any]) -> Set[Tile]:
    out: Set[Tile] = set()
    for reg in spec.get("regions", []):
        out |= _rect_tiles(reg["rect"])
    return out


def blocked_tiles(spec: Dict[str, Any]) -> Set[Tile]:
    cols, rows = grid_dims(spec)
    out: Set[Tile] = set()
    for w in spec.get("walls", []):
        out |= _rect_tiles(w)
    for o in spec.get("objects", []):
        if o.get("blocks", True):
            out |= obj_tiles(o, cols, rows)
    return out


def walkable_tiles(spec: Dict[str, Any]) -> Set[Tile]:
    return region_tiles(spec) - blocked_tiles(spec)


def exit_tiles(spec: Dict[str, Any]) -> Set[Tile]:
    out: Set[Tile] = set()
    for ex in spec.get("exits", {}).values():
        out |= {tuple(t) for t in ex.get("tiles", [])}
    return out


def entry_tiles(spec: Dict[str, Any]) -> List[Tile]:
    return [tuple(t) for t in spec.get("entry", {}).values()]


def reachable_from(start: Tile, walk: Set[Tile]) -> Set[Tile]:
    seen: Set[Tile] = set()
    if start not in walk:
        return seen
    q = deque([start])
    seen.add(start)
    while q:
        c, r = q.popleft()
        for nc, nr in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
            if (nc, nr) in walk and (nc, nr) not in seen:
                seen.add((nc, nr))
                q.append((nc, nr))
    return seen


def validate(spec: Dict[str, Any]) -> List[str]:
    """Return a list of problems; empty list means the spec is sound."""
    problems: List[str] = []
    cols, rows = grid_dims(spec)

    def in_bounds(rect: List[int]) -> bool:
        c, r, w, h = rect
        return 0 <= c and 0 <= r and c + w <= cols and r + h <= rows and w > 0 and h > 0

    for reg in spec.get("regions", []):
        if not in_bounds(reg["rect"]):
            problems.append("region out of bounds: %s" % reg)
    for w in spec.get("walls", []):
        if not in_bounds(w):
            problems.append("wall out of bounds: %s" % w)
    for o in spec.get("objects", []):
        if not in_bounds(o["rect"]):
            problems.append("object out of bounds: %s (%s)" % (o.get("id"), o["rect"]))
        fp = o.get("footprint")
        if fp and footprint_bbox(fp) != list(o["rect"]):
            problems.append("object %s: rect %s != footprint bbox %s — they must match, or "
                            "renders/collision disagree" % (o.get("id"), o["rect"], footprint_bbox(fp)))

    walk = walkable_tiles(spec)
    if not walk:
        problems.append("no walkable tiles")
        return problems

    # every blocking object should sit on/against floor, not float in the void
    floor = region_tiles(spec)
    blocked = blocked_tiles(spec)
    for o in spec.get("objects", []):
        if o.get("blocks", True) and not (obj_tiles(o, cols, rows) & (floor | blocked)):
            problems.append("object %s is outside any floor region" % o.get("id"))

    # reachability from the first entry point (or any walkable tile)
    starts = [t for t in entry_tiles(spec) if t in walk]
    if entry_tiles(spec) and not starts:
        problems.append("entry point(s) not on a walkable tile: %s" % entry_tiles(spec))
    start = starts[0] if starts else next(iter(walk))
    reached = reachable_from(start, walk)
    stranded = walk - reached
    if stranded:
        problems.append("%d walkable tiles unreachable from %s, e.g. %s"
                        % (len(stranded), start, sorted(stranded)[:6]))
    for et in exit_tiles(spec):
        if et not in reached:
            problems.append("exit tile %s not reachable from entry %s" % (et, start))
        c, r = et
        if not (c == 0 or c == cols - 1 or r == 0 or r == rows - 1):
            problems.append("exit tile %s is not on the map border — it draws no door and "
                            "dodges the centre check; put internal thresholds in as "
                            "walls/regions, keep exits on the edge" % (et,))
    return problems


# object types that the renderer actually draws AS wall treatment (so the "flat" check
# can't be cleared by a `panelling` object that renders as a fallback box — finishes go in
# `treatments[]`, which does render)
_RENDERED_TREATMENT = {"window", "bay"}
# semantic furniture categories for the "tables need seats" heuristic — synonyms are
# allowed; ones without bespoke art (stool/bench/settle/desk) should carry a `shape` so
# they render as more than a box
_SEAT = {"chair", "armchair", "stool", "bench", "banquette", "settle"}
_TABLE = {"table", "poseur", "desk"}
_KINDS = ("interior", "exterior", "street")


# Only real INPUT evidence counts as a citeable source. Excludes the pipeline's own
# outputs (_render, _archive), the authoring rationale (reconstruction.md), and metadata
# (manifest.json) — citing those would be circular or would leak the audit-forbidden recon.
_EVIDENCE_DIRS = {"gallery", "_resolve", "floorplan", "interior360", "exterior", "interior"}
_EVIDENCE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"}


def evidence_files(slug: str) -> Set[str]:
    """Relative paths of real photo/plan INPUTS under refs/<slug>/ (for cite verification)."""
    base = REPO_ROOT / "refs" / slug
    if not slug or not base.exists():
        return set()
    out: Set[str] = set()
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in _EVIDENCE_EXT:
            continue
        rel = p.relative_to(base)
        if rel.parts and rel.parts[0] in _EVIDENCE_DIRS:
            out.add(str(rel))
    return out


def _cite_resolves(cite: str, files: Set[str]) -> bool:
    """A cite resolves if it exactly matches, or prefixes, a real file (e.g. 'gallery/01'
    matches 'gallery/01_long_name.jpg'). It must *look* like a path or filename — contain a
    '/' or '.' — so a bare directory word ('gallery', 'g') that prefixes everything is
    rejected; a cite has to name a specific image, not a folder."""
    c = cite.strip()
    if not c or ("/" not in c and "." not in c):
        return False
    for f in files:
        if f == c:
            return True
        # prefix only counts at a name boundary, so 'gallery/02' matches
        # 'gallery/02_foo.jpg' but 'gallery/0' does NOT match 'gallery/01_foo.jpg'
        if f.startswith(c) and not f[len(c):len(c) + 1].isalnum():
            return True
    return False


def _df_resolves(df: str, files: Set[str]) -> bool:
    """A `derived_from` resolves only if it names a real evidence file: a full basename
    ('facade.jpg'), a relative path, or a cite-style prefix ('gallery/02'). A bare word that
    merely happens to be a filename *stem* ('facade', 'aerial') does NOT count — that let
    free prose ('I looked at the facade') pass."""
    if isinstance(df, (list, tuple)):
        df = " ".join(str(x) for x in df)
    names = set(files) | {f.split("/")[-1] for f in files}
    for tok in re.findall(r"[\w./-]+", str(df)):
        tok = tok.strip(".,;:")
        if tok in names or _cite_resolves(tok, files):
            return True
    return False


_WAIVER_MIN = 12  # a `match` shorter than this is too broad to be a real, specific waiver
# Warnings prefixed with this are NON-WAIVABLE: they mean the scene is ungrounded or cites
# fabricated evidence — the exact "false success" the gate exists to stop. No `why` clears them.
_HARD = "[non-waivable] "


def partition_waivers(spec: Dict[str, Any], warns: List[str]):
    """Split fidelity warnings into (active, waived) using meta.fidelity_waivers.

    A waiver is {"match": "<distinctive substring of ONE warning>", "why": "<justification>"}.
    To stop a waiver laundering the whole gate (e.g. match=" " matches every warning), a
    waiver only waives if it has a `why`, its `match` is >= _WAIVER_MIN chars, AND it matches
    **exactly one** warning. A waiver that is too short, matches nothing (stale), or matches
    several (over-broad) does NOT waive — it is itself surfaced as an *active* warning.
    Returns (active: List[str], waived: List[Tuple[warn, why]]).
    """
    waivers = spec.get("meta", {}).get("fidelity_waivers", [])
    waived_idx: Dict[int, str] = {}
    waiver_problems: List[str] = []
    for wv in waivers:
        m, why = wv.get("match", ""), wv.get("why", "")
        if not why or len(m) < _WAIVER_MIN:
            waiver_problems.append("invalid waiver %r — needs a `why` and a `match` of "
                                   ">= %d chars" % (m, _WAIVER_MIN))
            continue
        hits = [i for i, w in enumerate(warns) if m in w]
        if len(hits) == 0:
            waiver_problems.append("stale waiver matches no current warning: %r" % m)
        elif len(hits) > 1:
            waiver_problems.append("over-broad waiver matches %d warnings: %r — make it "
                                   "specific to one" % (len(hits), m))
        elif warns[hits[0]].startswith(_HARD):
            waiver_problems.append("cannot waive a non-waivable warning (ungrounded / "
                                   "fabricated-cite): %r — fix the evidence, don't waive" % m)
        else:
            waived_idx[hits[0]] = why
    active = [w for i, w in enumerate(warns) if i not in waived_idx] + waiver_problems
    waived = [(warns[i], why) for i, why in waived_idx.items()]
    return active, waived


def fidelity_warnings(spec: Dict[str, Any]) -> List[str]:
    """Heuristic 'is this derived or guessed?' checks. Non-fatal; see module docstring.

    These catch the failure modes validate() can't: defaulted door positions, an
    under-furnished room, no wall treatment, and objects placed without a photo cite.

    Furnishing/wall checks apply only to enclosed interiors — an open street or plaza is
    legitimately sparse and wall-less, so firing them there would just train the operator
    to ignore the gate. Set `meta.kind` to interior|exterior|street to tune it.
    """
    warns: List[str] = []
    cols, rows = grid_dims(spec)
    objs = spec.get("objects", [])
    kind = spec.get("meta", {}).get("kind", "interior")
    if kind not in _KINDS:
        warns.append("meta.kind %r unknown — use one of %s (assuming interior)"
                     % (kind, "/".join(_KINDS)))
        kind = "interior"

    # evidence files for this place; if none gathered yet, cite-paths can't be verified
    files = evidence_files(spec.get("meta", {}).get("slug", ""))

    # If anything CLAIMS evidence (cite / derived_from) but no files exist on disk, the
    # verification below would skip silently — exactly the "false success" hole. Flag it
    # loudly: no-evidence is a result, not a free pass. (Un-gathered fixtures like
    # _synthetic carry no cites, so they stay quiet about THIS non-waivable warning —
    # they still raise the ordinary uncited/sparse/etc. warnings.)
    claims_evidence = any(o.get("cite") for o in objs) or any(
        ex.get("derived_from") for ex in spec.get("exits", {}).values())
    if claims_evidence and not files:
        warns.append(_HARD + "objects/exits cite evidence but no files exist under "
                     "refs/<slug>/ — citations are UNVERIFIABLE; gather evidence first")

    # apply to every kind: evidence citations must exist + non-defaulted, evidenced doors
    uncited = [o.get("id", "?") for o in objs if not o.get("cite")]
    if uncited:
        warns.append("%d object(s) have no `cite` (photo that places them): %s"
                     % (len(uncited), ", ".join(uncited[:8])))
    if files:
        badcite = [o.get("id", "?") for o in objs if o.get("cite")
                   and not all(_cite_resolves(c, files) for c in o["cite"])]
        if badcite:
            warns.append(_HARD + "%d object(s) `cite` a file not in refs/<slug>/: %s — "
                         "citations must name real evidence" % (len(badcite), ", ".join(badcite[:8])))

    for side, ex in spec.get("exits", {}).items():
        tiles = ex.get("tiles", [])
        if not tiles:
            continue
        df = ex.get("derived_from")
        if df and files and not _df_resolves(df, files):
            warns.append("exit '%s' `derived_from` names no real evidence file — "
                         "an unverifiable string can't justify a door position" % side)
        # The centre check runs EVEN with a derived_from: a citation names a photo, it does
        # NOT prove the door sits on this tile (only the audit can). A centred door stays
        # suspect either way.
        if side in ("west", "east"):
            span, wall_len = [r for _, r in tiles], rows
        else:
            span, wall_len = [c for c, _ in tiles], cols
        mid = (min(span) + max(span)) / 2
        # tolerance scales with wall length (central ~20% reads as "defaulted") so the check
        # is uniform across a tiny room and a long scrolling wall; intentionally conservative
        # — a genuinely-central real door is cleared with a justified waiver.
        tol = max(1.0, (wall_len - 1) * 0.1)
        if abs(mid - (wall_len - 1) / 2) <= tol:
            tail = ("despite a `derived_from` (a citation doesn't prove the tile)"
                    if df else "with no `derived_from`")
            warns.append("exit '%s' sits at the wall's centre %s — verify the real door "
                         "position on facade/aerial or waive with justification" % (side, tail))

    if kind == "interior":
        walk = len(walkable_tiles(spec)) or 1
        per100 = len(objs) / (walk / 100.0)
        if per100 < 6:
            warns.append("sparse: %.1f objects/100 floor tiles (interiors read empty "
                         "below ~6)" % per100)

        # a table can carry its own chairs via `seats: N` (drawn as a setting), or be paired
        # with standalone seat objects — count both
        seats = (sum(1 for o in objs if o.get("type") in _SEAT)
                 + sum(o.get("seats", 0) for o in objs if o.get("type") in _TABLE))
        tables = sum(1 for o in objs if o.get("type") in _TABLE)
        if tables and seats < tables:
            warns.append("%d table(s) but only %d seat(s) — tables without chairs read as "
                         "boxes" % (tables, seats))

        materials = {reg.get("material") for reg in spec.get("regions", [])}
        has_treatment = (bool(spec.get("treatments"))
                         or any(o.get("type") in _RENDERED_TREATMENT for o in objs))
        if len(materials) <= 2 and not has_treatment:
            warns.append("flat: one/two floor materials and no wall treatment (panelling, "
                         "windows, fireplaces) — won't read as the real interior")

        # micro-composition: real rooms mix furniture; a uniform comb of identical tables
        # is the "eyeballed, un-measured detail" smell. Vary type/seats/shape (dining vs
        # poseur vs bistro) per the measured fixtures pass (reconstruction §4b).
        tbls = [o for o in objs if o.get("type") in _TABLE]
        if len(tbls) >= 5:
            sigs = Counter((o.get("type"), o.get("seats", 0), tuple(o["rect"][2:]),
                            o.get("shape"), o.get("palette")) for o in tbls)
            if sigs.most_common(1)[0][1] >= 0.8 * len(tbls):
                warns.append("%d tables are near-identical (type/size/seats/shape) — real "
                             "rooms mix dining/poseur/bistro and spacing; vary them or it "
                             "reads as a uniform comb" % len(tbls))

        # a wall bench is seating FOR tables — a long banquette with nothing fronting it is
        # an arrangement that was placed as a loose block, not a run.
        table_tiles = set()
        for o in tbls:
            table_tiles |= _rect_tiles(o["rect"])
        for o in objs:
            if o.get("type") != "banquette":
                continue
            c, r, w, h = o["rect"]
            if max(w, h) < 3:
                continue
            if w >= h:
                front = ({(cc, r - 1) for cc in range(c, c + w)}
                         | {(cc, r + h) for cc in range(c, c + w)})
            else:
                front = ({(c - 1, rr) for rr in range(r, r + h)}
                         | {(c + w, rr) for rr in range(r, r + h)})
            if not (front & table_tiles):
                warns.append("banquette run '%s' has no fronting tables — a wall bench "
                             "seats tables; place tables against it" % o.get("id", "?"))
    elif not objs:
        warns.append("%s scene has no objects — exteriors still need facades / street "
                     "furniture / features to be recognisable" % kind)
    return warns
