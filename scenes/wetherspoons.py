"""Scene 10 — The William Morris (Wetherspoons): bar, high-tables, dining room + snug"""
import pygame
from .base import Scene
from config import TILE_SIZE

_TS = TILE_SIZE


def _dk(c, n=22):
    return tuple(max(0, v - n) for v in c)


# ── Palette ──────────────────────────────────────────────────────────────────
_PANEL     = (76, 51, 32)
_PANEL_DK  = (52, 34, 20)
_PANEL_LT  = (100, 70, 46)
_CARPET    = (36, 66, 62)
_CARPET_R  = (132, 58, 46)
_CARPET_GD = (158, 132, 78)
_CARPET_LF = (48, 90, 72)
_CARPET_CR = (150, 150, 128)
_SHADOW    = (28, 52, 49)
_BAR_WOOD  = (74, 36, 28)
_BAR_TOP   = (52, 26, 20)
_BAR_HI    = (110, 60, 46)
_BAR_DK    = (40, 22, 14)
_BRASS     = (206, 174, 98)
_GANTRY    = (46, 30, 18)
_GANTRY_DK = (32, 20, 12)
_OPTIC     = (190, 205, 210)
_FRIDGE    = (150, 178, 192)
_FRIDGE_FR = (90, 110, 120)
_GREEN     = (44, 82, 60)
_GREEN_DK  = (30, 60, 44)
_GREEN_HI  = (78, 120, 92)
_MUST      = (190, 150, 70)
_MUST_DK   = (150, 116, 48)
_MUST_HI   = (214, 180, 104)
_CHAIR     = (120, 80, 46)
_CHAIR_DK  = (78, 50, 28)
_SEAT      = (176, 142, 78)
_TABLE     = (92, 58, 34)
_TABLE_DK  = (60, 36, 20)
_TABLE_HI  = (120, 82, 52)
_POSEUR    = (60, 38, 24)
_STOOL     = (40, 26, 18)
_STOOL_TOP = (150, 110, 60)
_BOTTLE_G  = (44, 96, 62)
_BOTTLE_A  = (170, 116, 52)
_BOTTLE_C  = (182, 204, 214)
_BOTTLE_R  = (170, 60, 60)
_GLASS     = (156, 182, 192)
_GLASS_HI  = (198, 214, 220)
_MIRROR    = (176, 192, 200)
_FRAME     = (170, 134, 74)
_FRAME_DK  = (118, 92, 50)
_WMP_BG    = (78, 96, 78)
_WMP_FG    = (150, 120, 70)
_PUMP_CHR  = (208, 210, 212)
_PUMP_CLIP = [(180, 50, 55), (210, 178, 92), (70, 110, 150),
              (90, 60, 130), (60, 130, 90)]
_PRICE     = (24, 24, 26)
_PRICE_TX  = (235, 235, 200)
_LIGHT     = (252, 242, 208)
_GLOW      = (255, 246, 214)
_FITTING   = (54, 38, 24)
_PART_GLASS = (150, 170, 175)
_FIRE      = (235, 150, 60)
_FIRE_DK   = (180, 90, 35)
_HEARTH    = (40, 38, 40)

# ── Layout (tile positions; everything here is SOLID / non-walkable) ──────────
_GREEN_BANQ = [(1, r) for r in range(3, 13)]      # left wall
_MUST_BANQ  = [(18, r) for r in range(3, 13)]     # right wall
_PARTITION  = [(11, r) for r in range(3, 9)]      # divider (open archway rows 9-12)
_HIGH       = [(3, 4), (5, 4), (7, 4), (9, 4)]     # poseur tables by the bar
_DINING     = [(3, 7), (6, 7), (9, 7), (3, 10), (6, 10), (9, 10)]
_SNUG       = [(13, 5), (16, 5), (13, 8), (16, 8), (13, 11), (16, 11)]

_BLOCKED = _GREEN_BANQ + _MUST_BANQ + _PARTITION + _HIGH + _DINING + _SNUG


# ── Floor: the famous Wetherspoons floral carpet ─────────────────────────────

def _flower(surf, cx, cy):
    for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7)):
        pygame.draw.circle(surf, _CARPET_LF, (cx + dx, cy + dy), 3)
    pygame.draw.circle(surf, _CARPET_R, (cx, cy), 4)
    pygame.draw.circle(surf, _CARPET_GD, (cx, cy), 2)


def _draw_carpet(surf):
    rect = pygame.Rect(0, 3 * _TS, 20 * _TS, 12 * _TS)
    pygame.draw.rect(surf, _CARPET, rect)
    old = surf.get_clip()
    surf.set_clip(rect)
    step = 40
    for j, gy in enumerate(range(rect.top + 8, rect.bottom, step)):
        off = step // 2 if j % 2 else 0
        for gx in range(rect.left + 8 + off, rect.right, step):
            pygame.draw.arc(surf, _CARPET_CR, (gx - 14, gy - 14, 28, 28), 0.3, 2.9, 1)
            _flower(surf, gx, gy)
    surf.set_clip(old)


# ── Walls: dark mahogany panelling, gilt prints + mirror ─────────────────────

def _panel(surf, x, y, w, h):
    pygame.draw.rect(surf, _PANEL, (x, y, w, h))
    for sx in range(x + 6, x + w - 4, 20):
        pygame.draw.rect(surf, _PANEL_DK, (sx, y + 4, 12, h - 8), 1)
        pygame.draw.line(surf, _PANEL_LT, (sx, y + 4), (sx + 12, y + 4), 1)


def _wm_print(surf, x, y, w, h):
    pygame.draw.rect(surf, _FRAME_DK, (x - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(surf, _FRAME, (x - 1, y - 1, w + 2, h + 2))
    pygame.draw.rect(surf, _WMP_BG, (x, y, w, h))
    for fy in range(y + 4, y + h - 2, 7):
        for fx in range(x + 4, x + w - 2, 8):
            pygame.draw.circle(surf, _WMP_FG, (fx, fy), 2)


def _draw_walls(surf):
    _panel(surf, 0, 0, _TS, 15 * _TS)
    _panel(surf, 19 * _TS, 0, _TS, 15 * _TS)
    _panel(surf, 0, 14 * _TS, 20 * _TS, _TS)
    _panel(surf, 12 * _TS, 0, 7 * _TS, 3 * _TS)        # snug back wall
    for ty in (5, 8, 11):
        _wm_print(surf, 5, ty * _TS + 5, _TS - 14, _TS - 12)
        _wm_print(surf, 19 * _TS + 7, ty * _TS + 5, _TS - 14, _TS - 12)
    # gilt mirror, left wall
    mx, my = 4, 3 * _TS + 4
    pygame.draw.rect(surf, _FRAME_DK, (mx - 1, my - 1, _TS - 6, _TS + 6))
    pygame.draw.rect(surf, _FRAME, (mx, my, _TS - 8, _TS + 4))
    pygame.draw.rect(surf, _MIRROR, (mx + 3, my + 3, _TS - 14, _TS - 2))
    pygame.draw.line(surf, _GLASS_HI, (mx + 5, my + 5), (mx + 5, my + _TS - 6), 2)
    # pump-clip bunting strung across the front room
    for i, bx in enumerate(range(_TS, 11 * _TS, 26)):
        c = _PUMP_CLIP[i % len(_PUMP_CLIP)]
        pygame.draw.polygon(surf, c, [(bx, 3 * _TS), (bx + 14, 3 * _TS), (bx + 7, 3 * _TS + 9)])


# ── Bar sprite (front room): gantry, optics, fridge, cask pumps ──────────────

def _draw_bar(surf):
    bx, bw = 2 * _TS, 11 * _TS
    pygame.draw.rect(surf, _GANTRY_DK, (bx, 0, bw, 2 * _TS))
    pygame.draw.rect(surf, _GANTRY, (bx + 3, 3, bw - 6, 2 * _TS - 8))
    # spirit optics (left third)
    for row in (10, 26):
        pygame.draw.rect(surf, _BAR_DK, (bx + 8, row + 12, bw // 3 - 8, 2))
        for ox in range(bx + 12, bx + bw // 3, 11):
            pygame.draw.rect(surf, _OPTIC, (ox, row, 5, 12))
            pygame.draw.rect(surf, _BRASS, (ox + 1, row + 12, 3, 3))
    # bottle shelves (middle)
    for row in (12, 30):
        for ox in range(bx + bw // 3 + 6, bx + 2 * bw // 3, 8):
            c = (_BOTTLE_G, _BOTTLE_A, _BOTTLE_C)[(ox) % 3]
            pygame.draw.rect(surf, c, (ox, row, 5, 11))
            pygame.draw.rect(surf, _BAR_DK, (ox, row, 5, 11), 1)
    # glass-front fridge (right third)
    fx = bx + 2 * bw // 3 + 4
    fw = bw - 2 * bw // 3 - 10
    pygame.draw.rect(surf, _FRIDGE_FR, (fx, 6, fw, 2 * _TS - 14))
    pygame.draw.rect(surf, _FRIDGE, (fx + 2, 8, fw - 4, 2 * _TS - 18))
    for gx in range(fx + 5, fx + fw - 6, 9):
        for gy in range(12, 2 * _TS - 16, 11):
            c = (_BOTTLE_R, _BOTTLE_G, _BOTTLE_C, _BOTTLE_A)[(gx + gy) % 4]
            pygame.draw.rect(surf, c, (gx, gy, 5, 8))
    pygame.draw.line(surf, _GLASS_HI, (fx + 4, 10), (fx + 4, 2 * _TS - 12), 2)
    # counter (row 2) — glossy mahogany, brass top + foot rail
    cy = 2 * _TS
    pygame.draw.rect(surf, _BAR_WOOD, (bx, cy, bw, _TS - 2))
    pygame.draw.rect(surf, _BAR_TOP, (bx, cy, bw, 6))
    pygame.draw.line(surf, _BAR_HI, (bx, cy + 7), (bx + bw, cy + 7), 1)
    pygame.draw.rect(surf, _BRASS, (bx, cy + _TS - 8, bw, 3))
    pygame.draw.rect(surf, _BAR_DK, (bx, cy, bw, _TS - 2), 1)
    # cask-ale pumps with round clips + LED price tags
    for i in range(8):
        hx = bx + 20 + i * 40
        clip = _PUMP_CLIP[i % len(_PUMP_CLIP)]
        pygame.draw.rect(surf, _PUMP_CHR, (hx, cy - 4, 5, 14))
        pygame.draw.circle(surf, clip, (hx + 2, cy - 9), 6)
        pygame.draw.circle(surf, _dk(clip), (hx + 2, cy - 9), 6, 1)
        pygame.draw.rect(surf, _PRICE, (hx - 3, cy + 9, 12, 5))
        pygame.draw.rect(surf, _PRICE_TX, (hx - 1, cy + 10, 8, 1))


# ── Glazed partition with archway ────────────────────────────────────────────

def _draw_partition(surf):
    px = 11 * _TS
    for ty in range(3, 9):
        gy = ty * _TS + 3
        pygame.draw.rect(surf, _PANEL, (px + 8, gy - 3, 16, _TS))
        pygame.draw.rect(surf, _PART_GLASS, (px + 5, gy, _TS - 10, _TS - 8))
        pygame.draw.rect(surf, _PANEL_DK, (px + 5, gy, _TS - 10, _TS - 8), 2)
        pygame.draw.line(surf, _GLASS_HI, (px + 8, gy + 3), (px + 8, gy + _TS - 11), 1)
    for py in (3 * _TS - 4, 9 * _TS - 4):                  # newel posts
        pygame.draw.rect(surf, _BAR_WOOD, (px + 10, py, 12, 8))
        pygame.draw.rect(surf, _BAR_DK, (px + 10, py, 12, 8), 1)


# ── Banquettes ───────────────────────────────────────────────────────────────

def _banquette(surf, x, y, w, h, base, dark, hi):
    pygame.draw.rect(surf, dark, (x, y, w, h))
    pygame.draw.rect(surf, base, (x + 3, y + 2, w - 6, h - 4))
    pygame.draw.rect(surf, hi, (x + 3, y + 2, w - 6, 3))
    for a in range(10, h - 6, 16):                          # buttoning
        pygame.draw.circle(surf, dark, (x + w // 2, y + a), 1)


def _draw_banquettes(surf):
    _banquette(surf, _TS, 3 * _TS, _TS, 10 * _TS, _GREEN, _GREEN_DK, _GREEN_HI)
    _banquette(surf, 18 * _TS, 3 * _TS, _TS, 10 * _TS, _MUST, _MUST_DK, _MUST_HI)


# ── Furniture sprites: poseur table, dining table, bentwood chair ────────────

def _chair(surf, cx, cy, face):
    pygame.draw.circle(surf, _SHADOW, (cx, cy + 2), 8)
    pygame.draw.circle(surf, _CHAIR_DK, (cx, cy), 8)
    pygame.draw.circle(surf, _CHAIR, (cx, cy), 7)
    pygame.draw.circle(surf, _SEAT, (cx, cy), 5)
    pygame.draw.circle(surf, _dk(_SEAT), (cx, cy), 5, 1)
    arcs = {'up': (3.6, 5.8, (cx - 9, cy - 12)), 'down': (0.5, 2.7, (cx - 9, cy - 4)),
            'left': (2.1, 4.2, (cx - 12, cy - 9)), 'right': (-1.0, 1.1, (cx - 4, cy - 9))}
    a0, a1, (ax, ay) = arcs[face]
    pygame.draw.arc(surf, _CHAIR_DK, (ax, ay, 18, 18), a0, a1, 3)


def _draw_dining(surf, positions, faces=('up', 'down', 'left', 'right')):
    off = {'up': (0, -16), 'down': (0, 16), 'left': (-16, 0), 'right': (16, 0)}
    flip = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
    for col, row in positions:
        cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
        for f in faces:
            dx, dy = off[f]
            _chair(surf, cx + dx, cy + dy, flip[f])
        pygame.draw.ellipse(surf, _SHADOW, (cx - 13, cy - 9, 26, 22))
        pygame.draw.circle(surf, _TABLE_DK, (cx, cy), 13)
        pygame.draw.circle(surf, _TABLE, (cx, cy), 12)
        pygame.draw.circle(surf, _TABLE_HI, (cx - 3, cy - 3), 8, 1)
        pygame.draw.rect(surf, (70, 70, 76), (cx - 4, cy - 4, 8, 8))   # condiment caddy
        pygame.draw.rect(surf, _BOTTLE_R, (cx - 2, cy - 3, 2, 4))


def _draw_high_tables(surf, positions):
    for col, row in positions:
        cx, cy = col * _TS + _TS // 2, row * _TS + _TS // 2
        for dx, dy in ((-14, 0), (14, 0), (0, 14)):                    # tall stools
            pygame.draw.circle(surf, _STOOL, (cx + dx, cy + dy), 6)
            pygame.draw.circle(surf, _STOOL_TOP, (cx + dx, cy + dy), 4)
        pygame.draw.circle(surf, _SHADOW, (cx, cy + 3), 11)
        pygame.draw.circle(surf, _STOOL, (cx, cy), 4)                  # pedestal
        pygame.draw.circle(surf, _POSEUR, (cx, cy), 10)                # tall round top
        pygame.draw.circle(surf, _dk(_POSEUR, 14), (cx, cy), 10, 1)
        pygame.draw.circle(surf, _BAR_HI, (cx - 3, cy - 3), 3)


# ── Fireplace, doors, lighting ───────────────────────────────────────────────

def _draw_fireplace(surf):
    fx, fy = 14 * _TS, 2 * _TS - 10
    fw, fh = 3 * _TS, _TS + 8
    pygame.draw.rect(surf, _BAR_WOOD, (fx - 4, fy - 4, fw + 8, fh + 4))
    pygame.draw.rect(surf, _BAR_DK, (fx - 4, fy - 4, fw + 8, 5))
    pygame.draw.rect(surf, _HEARTH, (fx + 6, fy + 4, fw - 12, fh - 6))
    for i in range(5):
        gx = fx + 14 + i * ((fw - 28) // 4)
        pygame.draw.polygon(surf, _FIRE_DK, [(gx, fy + fh - 4), (gx - 5, fy + 12), (gx + 5, fy + 12)])
        pygame.draw.polygon(surf, _FIRE, [(gx, fy + fh - 6), (gx - 3, fy + 16), (gx + 3, fy + 16)])
    pygame.draw.rect(surf, _FRAME, (fx + fw // 2 - 14, fy - 2, 28, 10))
    pygame.draw.rect(surf, _MIRROR, (fx + fw // 2 - 11, fy, 22, 6))


def _draw_doors(surf):
    for i, dx in enumerate((9 * _TS, 10 * _TS)):
        pygame.draw.rect(surf, _PANEL_DK, (dx, 14 * _TS, _TS, _TS))
        pygame.draw.rect(surf, _BAR_WOOD, (dx + 2, 14 * _TS + 2, _TS - 4, _TS - 4))
        pygame.draw.rect(surf, _GLASS, (dx + 6, 14 * _TS + 5, _TS - 12, _TS // 2 + 2))
        pygame.draw.line(surf, _GLASS_HI, (dx + 8, 14 * _TS + 7),
                         (dx + 8, 14 * _TS + _TS // 2 + 3), 2)
        hx = dx + (_TS - 5 if i == 0 else 3)
        pygame.draw.rect(surf, _BRASS, (hx, 14 * _TS + _TS // 2, 2, 9))


def _pendant(surf, lx, ly):
    pygame.draw.line(surf, _FITTING, (lx, ly - 22), (lx, ly - 6), 1)
    pygame.draw.circle(surf, _GLOW, (lx, ly), 8)
    pygame.draw.circle(surf, _LIGHT, (lx, ly), 5)
    pygame.draw.circle(surf, _FITTING, (lx, ly), 8, 1)


def _draw_lights(surf):
    for lx in (4 * _TS, 7 * _TS):
        _pendant(surf, lx, 5 * _TS)
        _pendant(surf, lx, 9 * _TS)
    _pendant(surf, 14 * _TS, 6 * _TS)
    _pendant(surf, 16 * _TS, 10 * _TS)
    cx, cy = 6 * _TS, 12 * _TS                              # ceiling rose
    pygame.draw.circle(surf, _PANEL_LT, (cx, cy), 14, 2)
    pygame.draw.circle(surf, _GLOW, (cx, cy), 6)
    pygame.draw.circle(surf, _LIGHT, (cx, cy), 4)


# ── Scene ────────────────────────────────────────────────────────────────────

class WilliamMorris(Scene):
    static_blocked = _BLOCKED

    def __init__(self):
        super().__init__('wetherspoons')

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_carpet(screen)
        _draw_walls(screen)
        _draw_fireplace(screen)
        _draw_bar(screen)
        _draw_partition(screen)
        _draw_banquettes(screen)
        _draw_high_tables(screen, _HIGH)
        _draw_dining(screen, _DINING)
        _draw_dining(screen, _SNUG, faces=('up', 'down', 'left'))
        _draw_doors(screen)
        _draw_lights(screen)
        self._draw_objects(screen)
