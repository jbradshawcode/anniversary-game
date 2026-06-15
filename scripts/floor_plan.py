"""Render a clear, labelled top-down floor plan of The William Morris (Wetherspoons).

Diagram only — drawn on the game's 20x15 tile grid so it doubles as a build spec.
Run:  SDL_VIDEODRIVER=dummy python3 scripts/floor_plan.py
Out:  wetherspoons_refs/ws_floorplan.png
"""
import pygame
import pathlib

pygame.init()
TS = 40                      # plan tile size (bigger than the game's 32 for legibility)
MX, MY = 46, 70              # left / top margin for rulers + title
COLS, ROWS = 20, 15
W = MX + COLS * TS + 20
H = MY + ROWS * TS + 220     # extra space for the legend

_BG = (244, 241, 234)
_WALL = (92, 62, 38)
_GRID = (214, 208, 196)
_INK = (35, 30, 26)
_RULER = (120, 112, 100)

# zone fills (col0, row0, col1, row1 inclusive), label, colour
_ZONES = [
    ((2, 0, 13, 2),  "BAR  —  back-bar gantry · optics · bottle fridge · cask pumps · brass rail", (150, 96, 60)),
    ((14, 0, 18, 2), "FIREPLACE\n+ over-mantel mirror", (206, 132, 70)),
    ((2, 3, 13, 5),  "HIGH TABLES & STOOLS\n(poseur tables by the bar)", (176, 200, 214)),
    ((2, 6, 9, 12),  "MAIN DINING ROOM\ndark-wood tables + bentwood chairs\n(framed prints · picture lights · bunting)", (190, 214, 184)),
    ((12, 3, 17, 12),"BACK SNUG\nbooth tables along the\nmustard banquette + round tables", (224, 210, 178)),
    ((2, 13, 5, 13), "WC / TOILETS (rear)", (208, 200, 188)),
]

# thin features needing only a legend swatch (col0,row0,col1,row1), label-key, colour
_STRIPS = [
    ((1, 3, 1, 12),  "green", (46, 96, 66)),     # green leather banquette, left wall
    ((18, 3, 18, 12),"mustard", (196, 156, 76)), # mustard/striped banquette, right wall
    ((11, 5, 11, 8), "partition", (110, 78, 48)),# glazed panelled partition (archway below row 9)
]

_LEGEND = [
    ((46, 96, 66),  "Green leather banquette (left wall)"),
    ((196, 156, 76),"Mustard / striped banquette (right wall)"),
    ((110, 78, 48), "Glazed panelled partition — archway/opening below it"),
    ((150, 96, 60), "Bar & servery"),
    ((176, 200, 214),"High poseur tables + stools"),
    ((190, 214, 184),"Main dining room (tables + chairs)"),
    ((224, 210, 178),"Back snug (booths + round tables)"),
    ((206, 132, 70),"Fireplace feature"),
]


def font(sz, bold=False):
    f = pygame.font.SysFont("helveticaneue,arial", sz, bold=bold)
    return f


def gx(c):
    return MX + c * TS


def gy(r):
    return MY + r * TS


def wrap_blit(surf, text, cx, cy, sz=13, col=_INK, bold=False):
    f = font(sz, bold)
    lines = text.split("\n")
    th = f.get_height()
    y0 = cy - (len(lines) * th) // 2
    for i, ln in enumerate(lines):
        t = f.render(ln, True, col)
        surf.blit(t, (cx - t.get_width() // 2, y0 + i * th))


def main():
    s = pygame.Surface((W, H))
    s.fill(_BG)

    # title
    s.blit(font(22, True).render("THE WILLIAM MORRIS  (Wetherspoons) — floor plan", True, _INK), (MX, 18))
    s.blit(font(12, False).render("2-4 King Street, Hammersmith  ·  drawn on the 20x15 tile grid", True, _RULER), (MX, 46))

    plan = pygame.Rect(gx(0), gy(0), COLS * TS, ROWS * TS)

    # zone fills
    for (c0, r0, c1, r1), label, colr in _ZONES:
        rect = pygame.Rect(gx(c0), gy(r0), (c1 - c0 + 1) * TS, (r1 - r0 + 1) * TS)
        pygame.draw.rect(s, colr, rect)

    # banquette / partition strips
    for (c0, r0, c1, r1), _key, colr in _STRIPS:
        rect = pygame.Rect(gx(c0), gy(r0), (c1 - c0 + 1) * TS, (r1 - r0 + 1) * TS)
        pygame.draw.rect(s, colr, rect)

    # grid
    for c in range(COLS + 1):
        pygame.draw.line(s, _GRID, (gx(c), gy(0)), (gx(c), gy(ROWS)), 1)
    for r in range(ROWS + 1):
        pygame.draw.line(s, _GRID, (gx(0), gy(r)), (gx(COLS), gy(r)), 1)

    # rulers
    rf = font(11)
    for c in range(COLS):
        t = rf.render(str(c), True, _RULER)
        s.blit(t, (gx(c) + TS // 2 - t.get_width() // 2, gy(0) - 16))
    for r in range(ROWS):
        t = rf.render(str(r), True, _RULER)
        s.blit(t, (gx(0) - 18, gy(r) + TS // 2 - t.get_height() // 2))

    # zone labels (centred)
    for (c0, r0, c1, r1), label, colr in _ZONES:
        cx = (gx(c0) + gx(c1 + 1)) // 2
        cy = (gy(r0) + gy(r1 + 1)) // 2
        wrap_blit(s, label, cx, cy, 13, _INK, bold=True)

    # bar pump ticks (visual cue along the counter, row 2)
    for c in range(3, 13):
        pygame.draw.circle(s, (60, 40, 26), (gx(c) + TS // 2, gy(2) + TS - 8), 3)

    # partition archway opening marker (rows 9-12 of col 11 are open)
    arch = pygame.Rect(gx(11), gy(9), TS, 4 * TS)
    pygame.draw.rect(s, (120, 170, 120), arch, 2)
    s.blit(font(10, True).render("OPEN", True, (60, 110, 60)),
           (gx(11) + 4, gy(11)))

    # entrance doors + arrow
    door = pygame.Rect(gx(9), gy(14), 2 * TS, TS)
    pygame.draw.rect(s, (120, 80, 46), door)
    s.blit(font(12, True).render("ENTRANCE", True, _BG), (door.x + 8, door.y + 6))
    ax = door.centerx
    pygame.draw.line(s, (180, 40, 40), (ax, gy(15) + 34), (ax, gy(15) + 8), 4)
    pygame.draw.polygon(s, (180, 40, 40),
                        [(ax - 7, gy(15) + 12), (ax + 7, gy(15) + 12), (ax, gy(15) + 1)])
    s.blit(font(11, True).render("from King St", True, (180, 40, 40)),
           (ax + 14, gy(15) + 18))

    # outer wall
    pygame.draw.rect(s, _WALL, plan, 5)

    # legend
    ly = gy(ROWS) + 62
    s.blit(font(15, True).render("LEGEND", True, _INK), (MX, ly - 24))
    for i, (colr, txt) in enumerate(_LEGEND):
        col = i % 2
        row = i // 2
        bx = MX + col * 380
        by = ly + row * 26
        pygame.draw.rect(s, colr, (bx, by, 20, 16))
        pygame.draw.rect(s, _INK, (bx, by, 20, 16), 1)
        s.blit(font(13).render(txt, True, _INK), (bx + 28, by + 1))

    out = pathlib.Path("wetherspoons_refs") / "ws_floorplan.png"
    out.parent.mkdir(exist_ok=True)
    pygame.image.save(s, str(out))
    print("saved", out, s.get_size())


if __name__ == "__main__":
    main()
