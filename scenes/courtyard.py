"""Scene 7 — School courtyard

Long brick-paved avenue from the King Street gates to the
sports centre, flanked by Victorian school buildings (west)
and the modern wing (east).  Narrows at the gates, widens
into a piazza near the glass entrance.
"""
import pygame
from .base import Scene
from config import TILE_SIZE

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_VIC        = (155, 68, 48)
_VIC_DK     = (130, 52, 35)
_STONE      = (195, 188, 175)
_STONE_DK   = (175, 168, 155)
_MOD        = (165, 95, 58)
_MOD_DK     = (142, 78, 45)
_MOD_UPPER  = (175, 175, 178)
_MOD_UP_DK  = (155, 155, 158)
_MOD_ACCENT = (215, 195, 135)
_PATH       = (205, 178, 148)
_PATH_ALT   = (198, 170, 140)
_PATH_BRICK = (180, 120, 82)
_PATH_BR_DK = (155, 98, 65)
_GLASS      = (155, 175, 190)
_GLASS_HI   = (180, 200, 215)
_GLASS_FR   = (85, 100, 115)
_SLATE      = (85, 90, 100)
_SLATE_DK   = (72, 78, 88)
_IRON       = (42, 40, 38)
_IRON_LT    = (62, 60, 58)
_PLANT_BG   = (45, 72, 38)
_PLANT_BOX  = (55, 108, 48)
_PLANT_BX_D = (42, 85, 35)
_PLANT_COV  = (68, 95, 55)
_BENCH      = (110, 95, 72)
_BENCH_DK   = (85, 72, 52)
_BENCH_SLAT = (125, 108, 82)
_TREE_TRUNK = (95, 65, 35)
_TREE_LEAF  = (65, 135, 55)
_TREE_LF_DK = (48, 110, 42)
_TREE_LF_LT = (78, 150, 65)
_CYPRESS    = (52, 90, 52)
_CYPRESS_LT = (68, 110, 62)
_CHIMNEY    = (142, 58, 40)
_CAFE_METAL = (85, 85, 88)
_CAFE_TOP   = (195, 192, 188)
_SHADOW     = (178, 152, 122)
_WINDOW_SIL = (185, 178, 165)

# ── Blocked tiles ────────────────────────────────────────────────────────────
_BLOCKED = []
for _r in range(2, 9):
    _BLOCKED.append((3, _r))
    _BLOCKED.append((16, _r))
for _r in range(2, 5):
    _BLOCKED.append((4, _r))
    _BLOCKED.append((15, _r))
_BLOCKED.extend([
    (5, 2), (14, 4), (5, 10),
    (3, 10), (3, 11),
    (5, 6), (14, 7),
    (15, 10), (16, 10), (15, 11), (16, 11),
])

# ── Floor zones ──────────────────────────────────────────────────────────────
_FLOOR_ZONES = [
    (3, 17, 2, 13),
    (8, 12, 0, 2),
    (6, 14, 13, 15),
]


# ── Drawing ──────────────────────────────────────────────────────────────────

def _draw_vic_building(surf):
    x, w = 0, 3 * _TS
    h = 15 * _TS
    pygame.draw.rect(surf, _VIC, (x, 0, w, h))
    offset = 0
    for gy in range(0, h, 4):
        for gx in range(x + offset, x + w, 8):
            pygame.draw.line(surf, _VIC_DK, (gx, gy), (gx, gy + 4), 1)
        offset = 4 - offset
        pygame.draw.line(surf, _VIC_DK, (x, gy), (x + w, gy), 1)

    gable_h = 2 * _TS
    for i in range(6):
        gy = 2 * _TS + i * gable_h
        peak_y = gy + gable_h // 2
        pygame.draw.polygon(surf, _SLATE, [
            (w - 2, gy + 2), (w + 6, peak_y), (w - 2, gy + gable_h - 2)])
        pygame.draw.polygon(surf, _SLATE_DK, [
            (w - 2, gy + 2), (w + 6, peak_y), (w - 2, gy + gable_h - 2)], 1)
        pygame.draw.rect(surf, _STONE, (w + 3, peak_y - 3, 5, 6))

    for i in range(6):
        wy = 2 * _TS + i * gable_h + (gable_h - 20) // 2
        wx = w - 16
        pygame.draw.rect(surf, _STONE, (wx - 2, wy - 2, 16, 22))
        pygame.draw.polygon(surf, _STONE, [
            (wx, wy), (wx + 6, wy - 5), (wx + 12, wy)])
        pygame.draw.polygon(surf, _GLASS, [
            (wx + 2, wy), (wx + 6, wy - 3), (wx + 10, wy)])
        pygame.draw.rect(surf, _GLASS, (wx, wy, 12, 18))
        pygame.draw.rect(surf, _GLASS_HI, (wx, wy, 6, 9))
        pygame.draw.line(surf, _STONE_DK, (wx + 6, wy - 3), (wx + 6, wy + 18), 1)
        pygame.draw.rect(surf, _STONE_DK, (wx, wy, 12, 18), 1)
        pygame.draw.rect(surf, _WINDOW_SIL, (wx - 2, wy + 18, 16, 2))

    for cx in (_TS - 4, 2 * _TS - 6):
        pygame.draw.rect(surf, _CHIMNEY, (cx, 0, 8, 6))
        pygame.draw.rect(surf, _VIC_DK, (cx, 0, 8, 6), 1)
        pygame.draw.rect(surf, _STONE, (cx - 1, 0, 10, 2))


def _draw_mod_building(surf):
    x = 17 * _TS
    w = 3 * _TS
    h = 15 * _TS
    pygame.draw.rect(surf, _MOD, (x, 0, w, h))
    offset = 0
    for gy in range(0, h, 4):
        for gx in range(x + offset, x + w, 8):
            pygame.draw.line(surf, _MOD_DK, (gx, gy), (gx, gy + 4), 1)
        offset = 4 - offset
        pygame.draw.line(surf, _MOD_DK, (x, gy), (x + w, gy), 1)

    for r in range(0, 15, 3):
        uy = r * _TS
        pygame.draw.rect(surf, _MOD_UPPER, (x + 2, uy, w - 4, _TS))
        pygame.draw.rect(surf, _GLASS, (x + 4, uy + 4, w - 8, _TS - 8))
        pygame.draw.rect(surf, _GLASS_HI,
                         (x + 4, uy + 4, (w - 8) // 2, (_TS - 8) // 2))
        pygame.draw.rect(surf, _MOD_UP_DK, (x + 4, uy + 4, w - 8, _TS - 8), 1)

    pygame.draw.rect(surf, _MOD_ACCENT, (x, 0, 3, h))


def _draw_gate_walls(surf):
    zones = [
        (3, 8, 0, 2),
        (12, 17, 0, 2),
    ]
    for c0, c1, r0, r1 in zones:
        x, y = c0 * _TS, r0 * _TS
        w, h = (c1 - c0) * _TS, (r1 - r0) * _TS
        pygame.draw.rect(surf, _VIC, (x, y, w, h))
        offset = 0
        for gy in range(y, y + h, 4):
            for gx in range(x + offset, x + w, 8):
                pygame.draw.line(surf, _VIC_DK, (gx, gy), (gx, gy + 4), 1)
            offset = 4 - offset
            pygame.draw.line(surf, _VIC_DK, (x, gy), (x + w, gy), 1)

    for section_x, section_w in [(3 * _TS, 5 * _TS), (12 * _TS, 5 * _TS)]:
        arch_w = 32
        num = section_w // arch_w
        for i in range(num):
            ax = section_x + i * arch_w + 4
            ay = 6
            aw = arch_w - 8
            ah = 2 * _TS - 10
            pygame.draw.rect(surf, _STONE, (ax - 1, ay - 1, aw + 2, ah + 2))
            pygame.draw.polygon(surf, _STONE, [
                (ax, ay), (ax + aw // 2, ay - 6), (ax + aw, ay)])
            pygame.draw.rect(surf, _IRON, (ax + 1, ay + 1, aw - 2, ah - 2))
            pygame.draw.polygon(surf, _IRON, [
                (ax + 1, ay + 1), (ax + aw // 2, ay - 4), (ax + aw - 1, ay + 1)])
            for rx in range(ax + 4, ax + aw - 2, 4):
                pygame.draw.line(surf, _IRON_LT, (rx, ay), (rx, ay + ah), 1)
            pygame.draw.line(surf, _IRON_LT,
                             (ax + 1, ay + ah // 2), (ax + aw - 1, ay + ah // 2), 1)


def _draw_gateposts(surf):
    for px in (8 * _TS - 10, 12 * _TS):
        pygame.draw.rect(surf, _VIC, (px, 0, 10, 2 * _TS))
        offset = 0
        for gy in range(0, 2 * _TS, 4):
            pygame.draw.line(surf, _VIC_DK, (px, gy), (px + 10, gy), 1)
            for gx in range(px + offset, px + 10, 8):
                pygame.draw.line(surf, _VIC_DK, (gx, gy), (gx, gy + 4), 1)
            offset = 4 - offset
        pygame.draw.rect(surf, _STONE, (px - 2, 0, 14, 4))
        pygame.draw.rect(surf, _STONE_DK, (px - 2, 0, 14, 4), 1)
        pygame.draw.rect(surf, _STONE, (px + 1, _TS + 2, 8, 10))
        pygame.draw.rect(surf, _STONE_DK, (px + 1, _TS + 2, 8, 10), 1)
        pygame.draw.polygon(surf, _STONE, [
            (px, 6), (px + 5, 0), (px + 10, 6)])
        pygame.draw.polygon(surf, _STONE_DK, [
            (px, 6), (px + 5, 0), (px + 10, 6)], 1)


def _draw_south_walls(surf):
    for c0, c1 in [(3, 6), (14, 17)]:
        x, y = c0 * _TS, 13 * _TS
        w, h = (c1 - c0) * _TS, 2 * _TS
        pygame.draw.rect(surf, _VIC, (x, y, w, h))
        offset = 0
        for gy in range(y, y + h, 4):
            for gx in range(x + offset, x + w, 8):
                pygame.draw.line(surf, _VIC_DK, (gx, gy), (gx, gy + 4), 1)
            offset = 4 - offset
            pygame.draw.line(surf, _VIC_DK, (x, gy), (x + w, gy), 1)


def _draw_glass_entrance(surf):
    gx = 6 * _TS
    gy = 13 * _TS
    gw = 8 * _TS
    gh = 2 * _TS
    pygame.draw.rect(surf, _VIC, (gx - 6, gy - 2, 10, gh + 4))
    pygame.draw.rect(surf, _VIC, (gx + gw - 4, gy - 2, 10, gh + 4))
    pygame.draw.rect(surf, _VIC_DK, (gx - 6, gy - 2, 10, gh + 4), 1)
    pygame.draw.rect(surf, _VIC_DK, (gx + gw - 4, gy - 2, 10, gh + 4), 1)

    pygame.draw.rect(surf, _GLASS_FR, (gx, gy - 2, gw, gh + 4))
    pane_w = gw // 8
    for i in range(8):
        px = gx + i * pane_w + 1
        pw = pane_w - 2
        pygame.draw.rect(surf, _GLASS, (px, gy, pw, gh - 2))
        pygame.draw.rect(surf, _GLASS_HI, (px, gy, pw // 2, gh // 3))
        pygame.draw.rect(surf, _GLASS_FR, (px, gy, pw, gh - 2), 1)
    pygame.draw.line(surf, _GLASS_FR,
                     (gx + gw // 2, gy), (gx + gw // 2, gy + gh - 2), 2)
    pygame.draw.line(surf, _GLASS_FR,
                     (gx, gy + gh // 2), (gx + gw, gy + gh // 2), 1)


def _draw_floor(surf):
    old_clip = surf.get_clip()
    for c0, c1, r0, r1 in _FLOOR_ZONES:
        fx, fy = c0 * _TS, r0 * _TS
        fw, fh = (c1 - c0) * _TS, (r1 - r0) * _TS
        pygame.draw.rect(surf, _PATH, (fx, fy, fw, fh))
        surf.set_clip(pygame.Rect(fx, fy, fw, fh))
        for py in range(fy, fy + fh, _TS):
            for px in range(fx, fx + fw, _TS):
                if ((px - fx) // _TS + (py - fy) // _TS) % 3 == 0:
                    pygame.draw.rect(surf, _PATH_ALT, (px, py, _TS, _TS))
        surf.set_clip(old_clip)

    strip_x = 10 * _TS - 8
    strip_w = 16
    for c0, c1, r0, r1 in _FLOOR_ZONES:
        fy = r0 * _TS
        fh = (r1 - r0) * _TS
        surf.set_clip(pygame.Rect(c0 * _TS, fy, (c1 - c0) * _TS, fh))
        pygame.draw.rect(surf, _PATH_BRICK, (strip_x, fy, strip_w, fh))
        bw, bh = 8, 4
        for row in range(fh // bh + 1):
            off = (bw // 2) if row % 2 else 0
            for col in range(-1, strip_w // bw + 2):
                bx = strip_x + col * bw + off
                by = fy + row * bh
                pygame.draw.rect(surf, _PATH_BR_DK, (bx, by, bw, bh), 1)
        surf.set_clip(old_clip)


def _draw_planted_borders(surf):
    for r in range(2, 9):
        bx, by = 3 * _TS, r * _TS
        pygame.draw.rect(surf, _PLANT_BG, (bx, by, _TS, _TS))
        pygame.draw.rect(surf, _PLANT_COV, (bx + 2, by + 2, _TS - 4, _TS - 4))
        cx, cy = bx + _TS // 2, by + _TS // 2
        pygame.draw.circle(surf, _PLANT_BX_D, (cx, cy), 8)
        pygame.draw.circle(surf, _PLANT_BOX, (cx - 1, cy - 1), 7)

    for r in range(2, 5):
        bx, by = 4 * _TS, r * _TS
        pygame.draw.rect(surf, _PLANT_BG, (bx, by, _TS, _TS))
        pygame.draw.rect(surf, _PLANT_COV, (bx + 4, by + 4, _TS - 8, _TS - 8))
        for sx in range(bx + 8, bx + _TS - 4, 12):
            pygame.draw.circle(surf, _PLANT_BOX, (sx, by + _TS // 2), 5)
            pygame.draw.circle(surf, _PLANT_BX_D, (sx, by + _TS // 2), 5, 1)

    for r in range(2, 9):
        bx, by = 16 * _TS, r * _TS
        pygame.draw.rect(surf, _PLANT_BG, (bx, by, _TS, _TS))
        pygame.draw.rect(surf, _PLANT_COV, (bx + 2, by + 2, _TS - 4, _TS - 4))
        cx, cy = bx + _TS // 2, by + _TS // 2
        pygame.draw.circle(surf, _PLANT_BX_D, (cx, cy), 8)
        pygame.draw.circle(surf, _PLANT_BOX, (cx - 1, cy - 1), 7)

    for r in range(2, 5):
        bx, by = 15 * _TS, r * _TS
        pygame.draw.rect(surf, _PLANT_BG, (bx, by, _TS, _TS))
        pygame.draw.rect(surf, _PLANT_COV, (bx + 4, by + 4, _TS - 8, _TS - 8))
        for sx in range(bx + 8, bx + _TS - 4, 12):
            pygame.draw.circle(surf, _PLANT_BOX, (sx, by + _TS // 2), 5)
            pygame.draw.circle(surf, _PLANT_BX_D, (sx, by + _TS // 2), 5, 1)


def _draw_tree(surf, col: int, row: int):
    cx = col * _TS + _TS // 2
    cy = row * _TS + _TS // 2
    pygame.draw.ellipse(surf, _SHADOW, (cx - 14, cy - 4, 28, 14))
    pygame.draw.rect(surf, _TREE_TRUNK, (cx - 3, cy - 4, 6, 10))
    pygame.draw.circle(surf, _TREE_LF_DK, (cx, cy - 4), 13)
    pygame.draw.circle(surf, _TREE_LEAF, (cx - 2, cy - 6), 11)
    pygame.draw.circle(surf, _TREE_LF_LT, (cx - 4, cy - 8), 6)


def _draw_cypress(surf, col: int, row: int):
    cx = col * _TS + _TS // 2
    cy = row * _TS + _TS // 2
    pygame.draw.ellipse(surf, _SHADOW, (cx - 5, cy + 4, 10, 6))
    pygame.draw.rect(surf, _TREE_TRUNK, (cx - 1, cy + 2, 3, 6))
    pygame.draw.ellipse(surf, _CYPRESS, (cx - 5, cy - 14, 10, 26))
    pygame.draw.ellipse(surf, _CYPRESS_LT, (cx - 3, cy - 12, 6, 20))


def _draw_bench(surf, col: int, row: int, facing: str):
    x, y = col * _TS, row * _TS
    if facing in ('east', 'west'):
        pygame.draw.rect(surf, _BENCH, (x + 8, y + 2, 16, 28))
        for sy in range(y + 3, y + 29, 4):
            pygame.draw.rect(surf, _BENCH_SLAT, (x + 9, sy, 14, 3))
        for ly in (y + 4, y + 22):
            pygame.draw.rect(surf, _BENCH_DK, (x + 7, ly, 2, 6))
            pygame.draw.rect(surf, _BENCH_DK, (x + 23, ly, 2, 6))
        back_x = x + 5 if facing == 'east' else x + 24
        pygame.draw.rect(surf, _BENCH_DK, (back_x, y + 2, 3, 28))
    else:
        pygame.draw.rect(surf, _BENCH, (x + 2, y + 8, 28, 16))
        for sx in range(x + 3, x + 29, 4):
            pygame.draw.rect(surf, _BENCH_SLAT, (sx, y + 9, 3, 14))
        for lx in (x + 4, x + 22):
            pygame.draw.rect(surf, _BENCH_DK, (lx, y + 7, 6, 2))
            pygame.draw.rect(surf, _BENCH_DK, (lx, y + 23, 6, 2))
        back_y = y + 6 if facing == 'south' else y + 24
        pygame.draw.rect(surf, _BENCH_DK, (x + 2, back_y, 28, 3))


def _draw_cafe_tables(surf):
    for tr in (10, 11):
        for tc in (15, 16):
            tx = tc * _TS
            ty = tr * _TS
            cx, cy = tx + _TS // 2, ty + _TS // 2
            pygame.draw.rect(surf, _CAFE_TOP, (cx - 6, cy - 6, 12, 12))
            pygame.draw.rect(surf, _CAFE_METAL, (cx - 6, cy - 6, 12, 12), 1)
            for dx, dy in [(-9, 0), (9, 0), (0, -9), (0, 9)]:
                sx, sy = cx + dx, cy + dy
                if (tx + 2 < sx < tx + _TS - 2 and
                        ty + 2 < sy < ty + _TS - 2):
                    pygame.draw.rect(surf, _CAFE_METAL,
                                     (sx - 3, sy - 3, 6, 6))


# ── Scene ────────────────────────────────────────────────────────────────────

class Courtyard(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('courtyard')

    def draw_structures(self, screen: pygame.Surface):
        _draw_vic_building(screen)
        _draw_mod_building(screen)
        _draw_gate_walls(screen)
        _draw_south_walls(screen)
        _draw_floor(screen)
        _draw_planted_borders(screen)
        _draw_gateposts(screen)
        _draw_glass_entrance(screen)

        _draw_tree(screen, 5, 2)
        _draw_tree(screen, 14, 4)
        _draw_tree(screen, 5, 10)

        _draw_cypress(screen, 3, 10)
        _draw_cypress(screen, 3, 11)

        _draw_bench(screen, 5, 6, 'east')
        _draw_bench(screen, 14, 7, 'west')

        _draw_cafe_tables(screen)
