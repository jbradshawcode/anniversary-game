"""Render a scene_spec to plan / blocked views.

  plan    — labelled top-down build diagram (human review)
  blocked — walkable vs blocked tiles + BFS reachability (layout debug)

The game-fidelity render (the artifact you carry into the audit) is render_ingame.py.

Run:
  SDL_VIDEODRIVER=dummy python3 $SK/render.py _synthetic --mode all
Out: refs/<slug>/_render/<mode>.png
"""
import argparse
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

import spec as S  # type: ignore  # noqa: E402

REPO_ROOT = S.REPO_ROOT

_MATERIAL = {
    "wood":     (172, 140, 92),
    "slate":    (96, 102, 108),
    "carpet":   (128, 70, 70),
    "tile":     (206, 200, 188),
    "grass":    (96, 128, 72),
    "concrete": (150, 150, 150),
    "cobble":   (120, 120, 124),
    "asphalt":  (70, 72, 76),
    "paving":   (180, 178, 170),
    "_":        (150, 150, 150),
}
# named palettes, shared with render_ingame's _OBJ_PALETTE keys so an object's `palette`
# reads the same across the plan and in-game renders (place-agnostic, not pub-wood only)
_PALETTE = {
    "cream":   (224, 216, 202),
    "teal":    (44, 74, 70),
    "mustard": (192, 152, 72),
    "tartan":  (150, 90, 84),
    "green":   (88, 110, 78),
    "oak":     (120, 84, 48),
    "dark":    (60, 44, 30),
    "brass":   (190, 160, 96),
    "_":       (110, 96, 72),
}


def _font(sz, bold=False):
    return pygame.font.SysFont("helveticaneue,arial", sz, bold=bold)


def _mat(name):
    return _MATERIAL.get(name, _MATERIAL["_"])


def _dk(c, n=28):
    return tuple(max(0, v - n) for v in c)


def _out(slug, mode):
    d = REPO_ROOT / "refs" / slug / "_render"
    d.mkdir(parents=True, exist_ok=True)
    return d / ("%s.png" % mode)


# ── plan ────────────────────────────────────────────────────────────────────

def render_plan(spec, problems, fidelity=()):
    cols, rows = S.grid_dims(spec)
    TS, MX, MY = 40, 48, 76
    W = MX + cols * TS + 20
    H = MY + rows * TS + 120
    s = pygame.Surface((W, H))
    s.fill((244, 241, 234))

    def gx(c):
        return MX + c * TS

    def gy(r):
        return MY + r * TS

    s.blit(_font(20, True).render(spec["meta"]["name"] + " — floor plan", True, (35, 30, 26)), (MX, 16))
    note = spec["meta"].get("notes", "drawn on the %dx%d tile grid" % (cols, rows))
    s.blit(_font(12).render(note, True, (120, 112, 100)), (MX, 44))

    for reg in spec.get("regions", []):
        c, r, w, h = reg["rect"]
        pygame.draw.rect(s, _mat(reg.get("material", "_")), (gx(c), gy(r), w * TS, h * TS))
    for c in range(cols + 1):
        pygame.draw.line(s, (214, 208, 196), (gx(c), gy(0)), (gx(c), gy(rows)))
    for r in range(rows + 1):
        pygame.draw.line(s, (214, 208, 196), (gx(0), gy(r)), (gx(cols), gy(r)))
    rf = _font(11)
    for c in range(cols):
        t = rf.render(str(c), True, (120, 112, 100))
        s.blit(t, (gx(c) + TS // 2 - t.get_width() // 2, gy(0) - 15))
    for r in range(rows):
        t = rf.render(str(r), True, (120, 112, 100))
        s.blit(t, (gx(0) - 17, gy(r) + TS // 2 - t.get_height() // 2))

    for w in spec.get("walls", []):
        c, r, ww, hh = w
        pygame.draw.rect(s, (92, 62, 38), (gx(c), gy(r), ww * TS, hh * TS))
    for o in spec.get("objects", []):
        c, r, ww, hh = o["rect"]
        col = _PALETTE.get(o.get("palette", "_"), _PALETTE["_"]) if o.get("blocks", True) else (200, 190, 170)
        if o.get("footprint"):   # draw the real (rasterised) footprint, not the bbox
            for (tc, tr) in S.obj_tiles(o, cols, rows):
                pygame.draw.rect(s, col, (gx(tc) + 1, gy(tr) + 1, TS - 2, TS - 2))
        else:
            rect = (gx(c) + 2, gy(r) + 2, ww * TS - 4, hh * TS - 4)
            pygame.draw.rect(s, col, rect)
            pygame.draw.rect(s, _dk(col), rect, 1 if o.get("blocks", True) else 2)
        lab = o.get("label", o.get("type", ""))
        if lab:
            t = _font(10, True).render(lab, True, (245, 245, 240))
            s.blit(t, (gx(c) + 4, gy(r) + 4))

    for side, ex in spec.get("exits", {}).items():
        for (c, r) in ex.get("tiles", []):
            pygame.draw.rect(s, (60, 120, 200), (gx(c) + 6, gy(r) + 6, TS - 12, TS - 12))
        if ex.get("tiles"):
            c, r = ex["tiles"][0]
            t = _font(9, True).render("%s->%s" % (side, ex.get("to", "?")), True, (40, 60, 110))
            s.blit(t, (gx(c), gy(r) - 1))

    pygame.draw.rect(s, (92, 62, 38), (gx(0), gy(0), cols * TS, rows * TS), 4)

    by = gy(rows) + 20
    if problems:
        s.blit(_font(14, True).render("TOPOLOGY: %d issue(s)" % len(problems), True, (170, 40, 40)), (MX, by))
        for i, p in enumerate(problems[:4]):
            s.blit(_font(11).render("• " + p[:110], True, (150, 40, 40)), (MX, by + 20 + i * 16))
    else:
        s.blit(_font(14, True).render("TOPOLOGY: reachable (NOT a fidelity check)", True, (40, 130, 60)), (MX, by))
    by += 22 + (16 * min(len(problems), 4) if problems else 0)
    if fidelity:
        s.blit(_font(14, True).render("FIDELITY: %d warning(s)" % len(fidelity), True, (180, 120, 30)), (MX, by))
        for i, w in enumerate(fidelity[:4]):
            s.blit(_font(11).render("• " + w[:110], True, (160, 110, 30)), (MX, by + 20 + i * 16))
    return s


# ── blocked ─────────────────────────────────────────────────────────────────

def render_blocked(spec):
    cols, rows = S.grid_dims(spec)
    TS, MX, MY = 36, 30, 50
    s = pygame.Surface((MX + cols * TS + 16, MY + rows * TS + 16))
    s.fill((28, 28, 32))
    walk = S.walkable_tiles(spec)
    blocked = S.blocked_tiles(spec)
    entries = [t for t in S.entry_tiles(spec) if t in walk]
    reached = S.reachable_from(entries[0], walk) if entries else set()
    exits = S.exit_tiles(spec)
    s.blit(_font(15, True).render("blocked / reachability — " + spec["meta"]["name"], True, (235, 235, 235)), (MX, 16))
    for r in range(rows):
        for c in range(cols):
            x, y = MX + c * TS, MY + r * TS
            if (c, r) in blocked:
                col = (150, 56, 56)
            elif (c, r) in walk and reached and (c, r) not in reached:
                col = (190, 70, 190)            # stranded walkable
            elif (c, r) in walk:
                col = (70, 130, 80)
            else:
                col = (44, 44, 50)              # void
            pygame.draw.rect(s, col, (x + 1, y + 1, TS - 2, TS - 2))
            if (c, r) in exits:
                pygame.draw.rect(s, (70, 140, 220), (x + 1, y + 1, TS - 2, TS - 2), 3)
            if (c, r) in entries:
                pygame.draw.rect(s, (235, 210, 90), (x + 1, y + 1, TS - 2, TS - 2), 3)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--mode", default="all", choices=["plan", "blocked", "all"])
    args = ap.parse_args()

    pygame.init()
    spec = S.load(S.spec_path(args.slug))
    problems = S.validate(spec)
    active, waived = S.partition_waivers(spec, S.fidelity_warnings(spec))
    modes = ["plan", "blocked"] if args.mode == "all" else [args.mode]
    for m in modes:
        surf = render_plan(spec, problems, active) if m == "plan" else render_blocked(spec)
        out = _out(args.slug, m)
        pygame.image.save(surf, str(out))
        print("  -> %s %s" % (out.relative_to(REPO_ROOT), surf.get_size()))
    if problems:
        print("TOPOLOGY: %d issue(s):" % len(problems))
        for p in problems:
            print("  • " + p)
    else:
        print("TOPOLOGY: reachable (necessary, NOT sufficient — fidelity is separate)")
    if active:
        print("FIDELITY: %d active warning(s) — likely guessed, not derived:" % len(active))
        for w in active:
            print("  • " + w)
    else:
        print("FIDELITY: no active warnings")
    for w, why in waived:
        print("  ~ waived: %s  [why: %s]" % (w, why))


if __name__ == "__main__":
    main()
