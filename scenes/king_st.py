"""Scene 2 — King Street, Hammersmith"""
import random
import pygame
from .base import Scene
from config import TILE_SIZE, SCREEN_HEIGHT

_TS = TILE_SIZE

_ROAD      = (90, 92, 95)
_ROAD_LINE = (220, 220, 215)
_CURB      = (155, 150, 142)
_PAVE      = (188, 183, 175)
_PAVE_EDGE = (172, 167, 160)
_GLASS     = (162, 182, 198)
_GLASS_HI  = (192, 208, 218)
_DOOR_WOOD = (82, 58, 38)
_RAILING   = (55, 55, 60)
_PILLAR    = (172, 165, 152)
_GATE_INT  = (25, 20, 18)
_SIDE_RD   = (100, 102, 105)

# North side — shops (col, width, wall, awning, label, style)
# Gaps at cols 10-12, 25-27, 42-44, 61-63, 78-80
_SHOPS = [
    (0,  5, (148, 145, 140), (42, 68, 135),   'POSK',                       'institutional'),
    (5,  5, (45, 45, 48),    (35, 55, 35),    'SAFFRON',                    'grocer'),
    (13, 4, (235, 230, 225), (180, 60, 65),   'ASK',                        'cafe'),
    (17, 3, (225, 222, 218), (30, 30, 32),    "LILLY'S\nNAILS",             'salon'),
    (20, 2, (180, 200, 40),  (145, 168, 30),  'THYME',                      'boutique'),
    (22, 3, (228, 225, 218), (55, 50, 45),    'MISTER CUT',                 'barber'),
    (28, 4, (232, 228, 222), (200, 30, 30),   'KFH',                        'estate'),
    (32, 4, (235, 235, 230), (180, 180, 185), 'PRIMA\nBRITANNIA',           'salon'),
    (36, 3, (80, 45, 70),    (60, 32, 52),    'SHILPA',                     'restaurant'),
    (39, 3, (195, 150, 155), (180, 140, 120), 'PATISSERIE\nSAINTE-ANNE',    'cafe'),
    (45, 4, (232, 228, 222), (70, 100, 160),  'THE ITALIAN\nBREAK',         'cafe'),
    (49, 4, (220, 215, 205), (55, 55, 58),    'BOHEMIA',                    'restaurant'),
    (53, 4, (235, 232, 228), (190, 25, 25),   'W LOCAL',                    'grocer'),
    (57, 4, (195, 125, 110), (180, 45, 35),   'SANBAO CHINESE\nKITCHEN',    'restaurant'),
    (64, 3, (220, 218, 212), (75, 78, 72),    'PORTICO',                    'estate'),
    (67, 3, (48, 42, 45),    (35, 30, 38),    'MOOBOO',                     'boutique'),
    (70, 3, (230, 228, 225), (35, 35, 38),    'CURTIS &\nPARKS',            'estate'),
    (73, 3, (225, 220, 212), (90, 40, 70),    'HORTON &\nGARTON',           'estate'),
    (76, 2, (230, 225, 218), (190, 35, 30),   'POST\nOFFICE',               'post'),
    (81, 3, (235, 235, 232), (30, 60, 120),   'DEXTERS',                    'estate'),
    (84, 3, (225, 222, 218), (0, 95, 115),    'CO-OP',                      'grocer'),
    (87, 3, (195, 180, 165), (75, 110, 105),  'CREDIT MUNCH',               'cafe'),
    (90, 3, (220, 215, 210), (68, 68, 72),    'HAIR WORKS',                 'salon'),
    (93, 2, (225, 222, 218), (40, 40, 45),    "MR ADAM'S\nBARBERS",         'barber'),
    (95, 5, (155, 75, 55),   (85, 75, 130),   'THE\nSALUTATION',            'pub'),
    # ── Extension east: #152 → #120, NORTH side only (even numbers) ──
    (100, 3, (228, 224, 218), (205, 70, 120),  'BEAUTY BY\nHONEY',           'salon'),
    (103, 2, (235, 232, 225), (210, 55, 50),   '99P STORE',                  'default'),
    (105, 3, (235, 232, 225), (40, 150, 70),   'SIMPLY FRESH',               'grocer'),
    (108, 3, (235, 235, 232), (20, 50, 120),   "DOMINO'S",                   'cafe'),
    (111, 3, (200, 178, 150), (60, 110, 70),   "PINOCCHIO'S",                'cafe'),
    (114, 3, (60, 50, 48),    (190, 85, 40),   'BRIM\nBURGERS',              'restaurant'),
    (117, 2, (58, 58, 66),    (120, 60, 150),  'MSP VAPE',                   'default'),
    (119, 2, (235, 235, 225), (35, 120, 55),   'SUBWAY',                     'cafe'),
    (121, 2, (58, 58, 66),    (215, 30, 40),   'TCG\nPOKEMON',               'boutique'),
    (123, 5, (155, 80, 60),   (75, 95, 78),    'PLOUGH &\nHARROW',           'pub_closed'),
    # ── Extension east: #118 → #2, north side, to the Wetherspoons (William Morris) ──
    (128, 3, (235, 235, 230), (20, 120, 55),   'PADDY\nPOWER',               'default'),
    (131, 3, (40, 55, 95),    (210, 170, 40),  'H&T',                        'default'),
    (134, 3, (235, 232, 225), (230, 120, 30),  'TAPI\nCARPETS',              'default'),
    (137, 3, (235, 232, 225), (40, 135, 150),  'CRISIS',                     'boutique'),
    (140, 3, (55, 48, 48),    (35, 60, 45),    'HEYTEA',                     'cafe'),
    (143, 3, (45, 38, 55),    (170, 30, 95),   'CASINO\nSLOTS',              'default'),
    (146, 3, (235, 232, 228), (110, 45, 130),  'TACO BELL',                  'cafe'),
    (149, 3, (45, 42, 45),    (200, 30, 40),   'GDK',                        'restaurant'),
    (152, 3, (225, 222, 215), (70, 105, 90),   'HOME\nSTORE',                'default'),
    (155, 3, (235, 232, 225), (210, 40, 40),   'MERKUR\nSLOTS',              'default'),
    (158, 3, (235, 228, 228), (200, 150, 160), 'SERAPHINE',                  'boutique'),
    (161, 4, (180, 185, 190), (90, 95, 100),   'LIVAT',                      'institutional'),
    (165, 3, (20, 80, 170),   (235, 200, 40),  'IKEA',                       'default'),
    (168, 3, (235, 235, 232), (210, 30, 40),   'H&M',                        'boutique'),
    (171, 3, (60, 52, 48),    (210, 95, 40),   'TORTILLA',                   'cafe'),
    (174, 6, (140, 95, 65),   (45, 65, 55),    'WETHERSPOONS',               'pub'),
]

# South side — buildings (col, width, wall_color, style)
_BUILDINGS = [
    (0,  10, (155, 75, 55),   'school'),
    (13, 5,  (160, 85, 60),   'terrace'),
    (18, 7,  (165, 80, 55),   'terrace'),
    (28, 7,  (165, 160, 152), 'church'),
    (35, 7,  (140, 130, 110), 'terrace'),
    (45, 5,  (160, 75, 55),   'terrace'),
    (50, 5,  (135, 115, 95),  'terrace'),
    (55, 6,  (168, 185, 202), 'modern'),
    (64, 7,  (185, 180, 172), 'modern'),
    (71, 7,  (158, 155, 150), 'town_hall'),
    (81, 9,  (170, 168, 162), 'modern'),
    (90, 10, (160, 80, 55),   'terrace'),
    (100, 8, (165, 80, 55),   'terrace'),
    (108, 7, (172, 168, 160), 'modern'),
    (115, 6, (160, 85, 60),   'terrace'),
    (121, 7, (170, 145, 110), 'modern'),
    (128, 10, (165, 80, 55),  'terrace'),
    (138, 9,  (172, 168, 160), 'modern'),
    (147, 10, (158, 155, 150), 'town_hall'),
    (157, 11, (175, 178, 182), 'modern'),
    (168, 12, (160, 82, 56),  'terrace'),
]

_SIDE_ROADS = [
    (10, 3),
    (25, 3),
    (42, 3),
    (61, 3),
    (78, 3),
]

# ── Traffic ────────────────────────────────────────────────────────────────
# The carriageway is rows 6-8; you may only step onto it on a zebra crossing,
# and only while its green man is lit. Crossings sit by the side roads and at the
# Salutation (col 97), so reaching the pub means waiting for a light to change.
_ROAD_ROWS = (6, 7, 8)
_CROSSINGS = [(10, 11), (25, 26), (42, 43), (61, 62), (78, 79),
              (96, 97), (129, 130), (157, 158)]
_WALK_TIME = 6.0          # green-man window
_WAIT_TIME = 7.0          # red-man (traffic flows)
_CROSS_OFFSET = 3.1       # stagger neighbouring lights so they don't all change at once

# Two lanes (UK: drive on the left). y = vertical centre of the lane.
_LANES = [(_ROAD_ROWS[0] * _TS + _TS - 2, -1),   # north lane -> westbound
          (_ROAD_ROWS[2] * _TS + 2, +1)]          # south lane -> eastbound
_CAR_LEN = 52
_CAR_W = 24
_CAR_COLORS = [(190, 60, 55), (70, 90, 150), (210, 200, 90), (70, 120, 90),
               (210, 215, 220), (50, 52, 58), (150, 95, 60), (120, 70, 140)]
_CAR_GLASS = (150, 175, 190)
_LIGHT_RED = (225, 60, 45)
_LIGHT_GRN = (70, 215, 95)
_LIGHT_OFF = (60, 55, 50)
_ZEBRA = (236, 236, 230)

_sign_font = None
_shop_font = None


def _font():
    global _sign_font
    if _sign_font is None:
        _sign_font = pygame.font.Font(None, 15)
    return _sign_font


def _sfont():
    global _shop_font
    if _shop_font is None:
        _shop_font = pygame.font.Font(None, 20)
    return _shop_font


_tiny_font = None


def _tfont():
    global _tiny_font
    if _tiny_font is None:
        _tiny_font = pygame.font.Font(None, 14)
    return _tiny_font


def _dk(c, n=28):
    return tuple(max(0, v - n) for v in c)


_SIGN_COLORS = {
    'SAFFRON':                (50, 185, 65),
    'THYME':                  (38, 38, 32),
    'SHILPA':                 (255, 215, 100),
    'PATISSERIE SAINTE-ANNE': (200, 165, 85),
    'SANBAO CHINESE KITCHEN': (255, 50, 40),
    'CREDIT MUNCH':           (38, 35, 30),
    'THE SALUTATION':         (255, 215, 100),
    'PRIMA BRITANNIA':        (55, 75, 135),
    "LILLY'S NAILS":          (240, 160, 60),
}




def _render_road(surf, ww):
    pygame.draw.rect(surf, _ROAD, (0, 6 * _TS, ww, 3 * _TS))
    pygame.draw.line(surf, _CURB, (0, 6 * _TS), (ww, 6 * _TS), 2)
    pygame.draw.line(surf, _CURB, (0, 9 * _TS - 1), (ww, 9 * _TS - 1), 2)
    cy = 7 * _TS + _TS // 2
    for x in range(0, ww, 40):
        pygame.draw.rect(surf, _ROAD_LINE, (x, cy - 1, 20, 2))


def _render_pavements(surf, ww):
    for x in range(0, ww, _TS * 2):
        pygame.draw.rect(surf, _PAVE_EDGE, (x, 4 * _TS, _TS, 2 * _TS), 1)
        pygame.draw.rect(surf, _PAVE_EDGE, (x, 9 * _TS, _TS, 2 * _TS), 1)


def _render_side_road(surf, col, w):
    x = col * _TS
    pw = w * _TS

    pygame.draw.rect(surf, _SIDE_RD, (x, 0, pw, 6 * _TS))
    pygame.draw.rect(surf, _SIDE_RD, (x, 9 * _TS, pw, 6 * _TS))

    for edge_x in (x, x + pw - 1):
        pygame.draw.line(surf, _CURB, (edge_x, 0), (edge_x, 6 * _TS), 1)
        pygame.draw.line(surf, _CURB, (edge_x, 9 * _TS), (edge_x, 15 * _TS), 1)

    cx = x + pw // 2
    for dy in range(4, 6 * _TS - 4, 12):
        pygame.draw.rect(surf, _ROAD_LINE, (cx, dy, 1, 6))
    for dy in range(9 * _TS + 4, 15 * _TS - 4, 12):
        pygame.draw.rect(surf, _ROAD_LINE, (cx, dy, 1, 6))



def _render_shop(surf, col, w, wall, awning, label, style='default'):
    x = col * _TS
    pw = w * _TS
    h = 4 * _TS
    wd = _dk(wall, 32)
    ay = 2 * _TS - 10
    ay_h = 20
    sf_y = ay + ay_h + 2
    sf_h = h - sf_y - 2

    pygame.draw.rect(surf, wall, (x, 0, pw, h))

    if style == 'institutional':
        for i in range(w):
            wx = x + i * _TS + 4
            pygame.draw.rect(surf, _GLASS, (wx, 12, _TS - 8, 34))
            pygame.draw.rect(surf, wd, (wx, 12, _TS - 8, 34), 1)
    elif style in ('pub', 'pub_closed'):
        for i in range(w):
            wx = x + i * _TS + 8
            ww = _TS - 16
            pygame.draw.rect(surf, _GLASS, (wx, 8, ww, 30))
            pygame.draw.rect(surf, _GLASS_HI, (wx, 8, ww // 2, 15))
            pygame.draw.rect(surf, wd, (wx, 8, ww, 30), 1)
            pygame.draw.line(surf, wd, (wx, 23), (wx + ww - 1, 23), 1)
            pygame.draw.rect(surf, (85, 65, 45), (wx - 2, 39, ww + 4, 5))
            for fx in range(wx, wx + ww, 4):
                fc = (200, 50, 60) if fx % 8 < 4 else (255, 180, 200)
                pygame.draw.rect(surf, fc, (fx, 36, 3, 3))
    else:
        for i in range(w - 1):
            wx = x + 10 + i * (pw - 16) // max(w - 1, 1)
            pygame.draw.rect(surf, _GLASS, (wx, 10, 18, 34))
            pygame.draw.rect(surf, _GLASS_HI, (wx, 10, 9, 17))
            pygame.draw.rect(surf, wd, (wx, 10, 18, 34), 1)
            pygame.draw.line(surf, wd, (wx + 9, 10), (wx + 9, 43), 1)
            pygame.draw.line(surf, wd, (wx, 27), (wx + 17, 27), 1)

    if style in ('pub', 'pub_closed'):
        pygame.draw.rect(surf, awning, (x + 1, ay - 2, pw - 2, ay_h + 4))
        pygame.draw.rect(surf, _dk(awning, 25), (x + 1, ay + ay_h, pw - 2, 3))
        for bx in range(x + 3, x + pw - 3, 4):
            pygame.draw.rect(surf, _dk(awning, 40), (bx, ay + ay_h + 1, 2, 2))
    elif style == 'cafe':
        pygame.draw.rect(surf, awning, (x + 2, ay, pw - 4, ay_h))
        for sx in range(x + 2, x + pw - 4, 6):
            pygame.draw.circle(surf, awning, (sx + 3, ay + ay_h + 1), 3)
    else:
        pygame.draw.rect(surf, awning, (x + 2, ay, pw - 4, ay_h))
        pygame.draw.rect(surf, _dk(awning, 20), (x + 2, ay + ay_h - 2, pw - 4, 3))

    if label:
        flat = label.replace('\n', ' ')
        sign_c = _SIGN_COLORS.get(flat)
        if sign_c is None:
            avg = sum(awning) / 3
            sign_c = (252, 252, 245) if avg < 128 else (35, 32, 28)
        if '\n' in label:
            lines = label.split('\n')
            f = _tfont()
            t1 = f.render(lines[0], True, sign_c)
            t2 = f.render(lines[1], True, sign_c)
            lh = f.get_height()
            y0 = ay + (ay_h - lh * 2) // 2
            surf.blit(t1, (x + pw // 2 - t1.get_width() // 2, y0))
            surf.blit(t2, (x + pw // 2 - t2.get_width() // 2, y0 + lh))
        else:
            txt = _sfont().render(label, True, sign_c)
            if txt.get_width() > pw - 8:
                txt = _font().render(label, True, sign_c)
            surf.blit(txt, (x + pw // 2 - txt.get_width() // 2,
                             ay + (ay_h - txt.get_height()) // 2))

    if style in ('pub', 'pub_closed'):
        tc1 = (85, 75, 130)
        tc2 = (165, 155, 130)
        tc3 = (120, 45, 55)
        pygame.draw.rect(surf, tc1, (x + 2, sf_y, pw - 4, sf_h))
        for ty in range(sf_y + 2, sf_y + sf_h - 2, 8):
            for tx in range(x + 4, x + pw - 4, 8):
                c = tc2 if (tx + ty) % 16 < 8 else tc3
                pygame.draw.rect(surf, c, (tx, ty, 6, 6))
        ex = x + pw // 2 - 12
        if style == 'pub':                       # an open dark doorway — you can go in
            pygame.draw.rect(surf, _GATE_INT, (ex, sf_y + 10, 24, sf_h - 10))
            pygame.draw.ellipse(surf, _GATE_INT, (ex, sf_y + 2, 24, 18))
        else:                                    # pub_closed: a shut door — not a venue you enter
            pygame.draw.rect(surf, _DOOR_WOOD, (ex, sf_y + 8, 24, sf_h - 8))
            pygame.draw.ellipse(surf, _DOOR_WOOD, (ex, sf_y, 24, 16))
            pygame.draw.rect(surf, _dk(_DOOR_WOOD), (ex, sf_y + 8, 24, sf_h - 8), 1)
            pygame.draw.line(surf, _dk(_DOOR_WOOD), (ex + 12, sf_y + 8),
                             (ex + 12, sf_y + sf_h), 1)              # two-leaf seam
            for hx in (ex + 9, ex + 13):                            # door knobs
                pygame.draw.rect(surf, (210, 190, 130), (hx, sf_y + sf_h // 2, 2, 3))
        for lx in (x + 8, x + pw - 12):
            pygame.draw.rect(surf, (45, 42, 38), (lx, sf_y + 2, 4, 6))
            pygame.draw.rect(surf, (255, 220, 120), (lx + 1, sf_y + 3, 2, 3))

    elif style == 'estate':
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        cw, ch = 12, 9
        cols_n = max(1, (pw - 16) // (cw + 3))
        for row in range(3):
            for ci in range(cols_n):
                cx = x + 6 + ci * (cw + 3)
                cy = sf_y + 3 + row * (ch + 2)
                if cx + cw < x + pw - 6 and cy + ch < sf_y + sf_h - 3:
                    pygame.draw.rect(surf, (248, 248, 242), (cx, cy, cw, ch))
                    pygame.draw.rect(surf, (200, 198, 192), (cx, cy, cw, ch), 1)
                    pygame.draw.rect(surf, (180, 175, 168), (cx + 1, cy + 1, cw - 2, 4))

    elif style == 'grocer':
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        dx = x + pw // 2 - 8
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 16, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 16, sf_h - 8), 1)

    elif style == 'barber':
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 14, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 14, sf_h), 1)
        dx = x + pw // 2 - 12
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 18, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 18, sf_h - 8), 1)
        pole_x = x + pw - 10
        pole_top = sf_y + 2
        pole_h = sf_h - 4
        pygame.draw.rect(surf, (220, 220, 218), (pole_x, pole_top, 6, pole_h))
        for sy in range(pole_top, pole_top + pole_h, 6):
            pygame.draw.rect(surf, (200, 30, 30), (pole_x, sy, 6, 2))
            pygame.draw.rect(surf, (30, 30, 200), (pole_x, sy + 3, 6, 2))
        pygame.draw.rect(surf, (160, 155, 148), (pole_x - 1, pole_top - 2, 8, 3))
        pygame.draw.rect(surf, (160, 155, 148), (pole_x - 1, pole_top + pole_h, 8, 3))

    elif style == 'cafe':
        pygame.draw.rect(surf, (172, 182, 175), (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        dx = x + pw - 22
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 18, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 18, sf_h - 8), 1)

    elif style == 'restaurant':
        pygame.draw.rect(surf, (170, 178, 165), (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        dx = x + 6
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 10, 16, sf_h - 10))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 10, 16, sf_h - 10), 1)
        mx = x + pw - 14
        pygame.draw.rect(surf, (38, 35, 32), (mx, sf_y + sf_h - 18, 10, 16))
        pygame.draw.rect(surf, (55, 52, 48), (mx, sf_y + sf_h - 18, 10, 16), 1)

    elif style == 'salon':
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        pygame.draw.line(surf, (200, 180, 255),
                         (x + 5, sf_y + 1), (x + pw - 5, sf_y + 1), 2)
        dx = x + pw // 2 - 10
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 20, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 20, sf_h - 8), 1)
        pygame.draw.rect(surf, (178, 172, 158), (dx + 14, sf_y + 24, 3, 3))

    elif style == 'post':
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        dx = x + pw // 2 - 10
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 20, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 20, sf_h - 8), 1)
        pygame.draw.rect(surf, (200, 30, 25), (x + 2, sf_y - 2, pw - 4, 3))

    elif style == 'boutique':
        pygame.draw.rect(surf, wall, (x, sf_y, pw, sf_h))
        ww = pw - 20
        pygame.draw.rect(surf, _GLASS, (x + 10, sf_y + 4, ww, sf_h - 14))
        pygame.draw.rect(surf, wd, (x + 10, sf_y + 4, ww, sf_h - 14), 1)
        dx = x + pw - 18
        pygame.draw.rect(surf, _dk(wall, 15), (dx, sf_y + sf_h - 24, 14, 24))
        pygame.draw.rect(surf, wd, (dx, sf_y + sf_h - 24, 14, 24), 1)
        for hx in (x + 8, x + pw - 12):
            pygame.draw.circle(surf, (90, 160, 70), (hx, sf_y - 4), 5)
            pygame.draw.circle(surf, (60, 120, 45), (hx, sf_y - 4), 5, 1)

    elif style == 'institutional':
        for i in range(w):
            gx = x + i * _TS + 2
            gw = _TS - 4
            pygame.draw.rect(surf, _GLASS, (gx, sf_y, gw, sf_h))
            pygame.draw.rect(surf, wd, (gx, sf_y, gw, sf_h), 1)
            pygame.draw.line(surf, wd,
                             (gx + gw // 2, sf_y), (gx + gw // 2, sf_y + sf_h), 1)

    else:
        pygame.draw.rect(surf, _GLASS, (x + 4, sf_y, pw - 8, sf_h))
        pygame.draw.rect(surf, wd, (x + 4, sf_y, pw - 8, sf_h), 1)
        dx = x + pw // 2 - 10
        pygame.draw.rect(surf, _DOOR_WOOD, (dx, sf_y + 8, 20, sf_h - 8))
        pygame.draw.rect(surf, _dk(_DOOR_WOOD), (dx, sf_y + 8, 20, sf_h - 8), 1)
        pygame.draw.rect(surf, (178, 172, 158), (dx + 14, sf_y + 24, 3, 3))

    pygame.draw.rect(surf, _dk(wall, 18), (x, 0, pw, h), 1)

    if style == 'grocer':
        crate_colors = [(45, 140, 50), (200, 60, 40), (220, 180, 40), (180, 100, 40)]
        n = min(len(crate_colors), (pw - 8) // 14)
        for ci in range(n):
            cx = x + 4 + ci * ((pw - 8) // max(n, 1))
            pygame.draw.rect(surf, (120, 95, 55), (cx, h, 12, 8))
            pygame.draw.rect(surf, crate_colors[ci], (cx + 1, h + 1, 10, 5))
    elif style == 'cafe':
        for ti in range(min(w - 1, 3)):
            tx = x + 6 + ti * 20
            pygame.draw.circle(surf, (160, 155, 148), (tx + 6, h + 8), 5, 1)
            pygame.draw.rect(surf, (140, 135, 128), (tx + 1, h + 5, 3, 5))
            pygame.draw.rect(surf, (140, 135, 128), (tx + 9, h + 5, 3, 5))
    elif style == 'post':
        pb_x = x + pw - 12
        pygame.draw.rect(surf, (200, 30, 25), (pb_x, h, 8, 14))
        pygame.draw.rect(surf, (160, 22, 18), (pb_x, h, 8, 14), 1)
        pygame.draw.rect(surf, (160, 22, 18), (pb_x + 1, h + 4, 6, 2))


def _render_building(surf, col, w, wall, style):
    x = col * _TS
    pw = w * _TS
    y = 11 * _TS
    h = 4 * _TS
    wd = _dk(wall, 32)

    pygame.draw.rect(surf, wall, (x, y, pw, h))

    if style == 'school':
        gc = 3
        gw_t = 2
        gx1 = x + gc * _TS
        gx2 = gx1 + gw_t * _TS

        for i in range(w):
            if gc <= i < gc + gw_t:
                continue
            wx = x + i * _TS + 6
            ww = _TS - 12
            pygame.draw.rect(surf, wd, (wx, y + 4, ww, 28))
            pygame.draw.ellipse(surf, wd, (wx, y, ww, 12))
            pygame.draw.rect(surf, _GLASS, (wx + 2, y + 8, ww - 4, 20))
            pygame.draw.rect(surf, _GLASS_HI, (wx + 2, y + 8, (ww - 4) // 2, 10))

        gw = gw_t * _TS
        pygame.draw.rect(surf, _GATE_INT, (gx1 + 8, y + 2, gw - 16, h - 2))
        pygame.draw.ellipse(surf, wall, (gx1 + 4, y - 12, gw - 8, 26))
        pygame.draw.ellipse(surf, _GATE_INT, (gx1 + 8, y - 9, gw - 16, 20))
        pygame.draw.rect(surf, _PILLAR, (gx1, y - 2, 8, h + 2))
        pygame.draw.rect(surf, _PILLAR, (gx2 - 8, y - 2, 8, h + 2))
        pygame.draw.rect(surf, _dk(_PILLAR, 15), (gx1 - 1, y - 6, 10, 5))
        pygame.draw.rect(surf, _dk(_PILLAR, 15), (gx2 - 9, y - 6, 10, 5))
        for bx in range(gx1 + 12, gx2 - 10, 5):
            pygame.draw.line(surf, _RAILING, (bx, y + 8), (bx, y + h - 2), 1)
        pygame.draw.line(surf, _RAILING,
                         (gx1 + 10, y + h // 2), (gx2 - 10, y + h // 2), 1)

        for rx in range(x, gx1, 5):
            pygame.draw.line(surf, _RAILING, (rx, y - 5), (rx, y), 1)
        for rx in range(gx2, x + pw, 5):
            pygame.draw.line(surf, _RAILING, (rx, y - 5), (rx, y), 1)
        pygame.draw.line(surf, _RAILING, (x, y - 3), (gx1, y - 3), 1)
        pygame.draw.line(surf, _RAILING, (gx2, y - 3), (x + pw, y - 3), 1)

    elif style == 'church':
        for i in range(0, w, 2):
            wx = x + i * _TS + _TS // 2 - 4
            pygame.draw.rect(surf, _GLASS, (wx, y + 10, 12, 32))
            pygame.draw.polygon(surf, _GLASS, [
                (wx, y + 10), (wx + 12, y + 10), (wx + 6, y + 3)])
            pygame.draw.rect(surf, wd, (wx, y + 10, 12, 32), 1)
        sx = x + pw // 2
        pygame.draw.polygon(surf, _dk(wall, 8), [
            (sx - 8, y), (sx + 8, y), (sx, y - 22)])
        pygame.draw.rect(surf, (68, 62, 58), (sx - 1, y - 28, 2, 8))

    elif style == 'town_hall':
        concrete = (148, 145, 140)
        pygame.draw.rect(surf, concrete, (x + 1, y + 1, pw - 2, h - 2))
        for band_y in range(y + _TS, y + h, _TS):
            pygame.draw.line(surf, _dk(concrete, 8),
                             (x + 2, band_y), (x + pw - 2, band_y), 1)
        for i in range(w):
            wx = x + i * _TS + 5
            ww = _TS - 10
            pygame.draw.rect(surf, (110, 125, 145), (wx, y + 6, ww, 26))
            pygame.draw.rect(surf, _dk(concrete, 12), (wx, y + 6, ww, 26), 1)
            pygame.draw.rect(surf, (110, 125, 145), (wx, y + 38, ww, 26))
            pygame.draw.rect(surf, _dk(concrete, 12), (wx, y + 38, ww, 26), 1)
        ew = _TS * 3
        ex = x + pw // 2 - ew // 2
        pygame.draw.rect(surf, (72, 75, 78), (ex, y + 72, ew, h - 72))
        pygame.draw.rect(surf, _GLASS, (ex + 4, y + 76, ew // 2 - 6, h - 80))
        pygame.draw.rect(surf, _GLASS,
                         (ex + ew // 2 + 2, y + 76, ew // 2 - 6, h - 80))

    elif style == 'modern':
        pygame.draw.rect(surf, (138, 158, 178), (x + 2, y + 2, pw - 4, h - 4))
        for gx in range(x + _TS, x + pw, _TS):
            pygame.draw.line(surf, (118, 138, 158), (gx, y + 2), (gx, y + h - 2), 1)
        for gy in range(y + _TS, y + h, _TS):
            pygame.draw.line(surf, (118, 138, 158), (x + 2, gy), (x + pw - 2, gy), 1)

    else:
        for i in range(0, w, 2):
            wx = x + i * _TS + 4
            ww = _TS * 2 - 8
            pygame.draw.rect(surf, _GLASS, (wx + 4, y + 6, ww - 8, 22))
            pygame.draw.rect(surf, _GLASS_HI, (wx + 4, y + 6, (ww - 8) // 2, 11))
            pygame.draw.rect(surf, wd, (wx + 4, y + 6, ww - 8, 22), 1)
            pygame.draw.rect(surf, _DOOR_WOOD, (wx + 8, y + 36, ww - 16, 24))
            pygame.draw.rect(surf, _dk(_DOOR_WOOD), (wx + 8, y + 36, ww - 16, 24), 1)

    pygame.draw.rect(surf, _dk(wall, 18), (x, y, pw, h), 1)


# Streetlamps — irregular spacing along both pavements (per the Street View refs:
# tall single-lantern columns, varied gaps, interspersed with the street trees).
_LAMPS = ([(c, 188) for c in (4, 19, 35, 53, 71, 90, 106, 123, 142, 161, 176)]
          + [(c, 350) for c in (11, 27, 46, 64, 83, 100, 119, 135, 153, 171)])

_glow = None


def _glow_surf():
    global _glow
    if _glow is None:
        R = 66
        _glow = pygame.Surface((2 * R, 2 * R))
        for r in range(R, 0, -1):
            f = (1 - r / R) ** 2.2 * 0.7
            pygame.draw.circle(_glow, (int(255 * f), int(204 * f), int(120 * f)),
                               (R, R), r)
    return _glow


def _render_lamp(surf, col, base_y, h=42):
    x = col * _TS + _TS // 2
    body, hi = (48, 50, 58), (74, 78, 88)
    pygame.draw.rect(surf, (34, 36, 42), (x - 3, base_y - 2, 6, 3))      # base
    pygame.draw.rect(surf, body, (x - 2, base_y - h, 4, h))             # column
    pygame.draw.rect(surf, hi, (x - 2, base_y - h, 1, h))
    pygame.draw.rect(surf, body, (x - 6, base_y - h - 4, 12, 5))        # lantern housing
    pygame.draw.rect(surf, (255, 238, 182), (x - 4, base_y - h - 3, 8, 4))  # lit lens
    return (x, base_y - h - 1)


def _apply_evening(surf, lamp_pts):
    # golden-hour warm grade over the whole street, then additive lamp glow
    try:
        import numpy as np
    except ImportError:
        np = None
    if np is not None:
        arr = pygame.surfarray.array3d(surf).astype('float32')
        arr[..., 0] *= 0.97
        arr[..., 1] *= 0.86
        arr[..., 2] *= 0.69
        np.clip(arr, 0, 255, out=arr)
        pygame.surfarray.blit_array(surf, arr.astype('uint8'))
    g = _glow_surf()
    R = g.get_width() // 2
    for x, y in lamp_pts:
        surf.blit(g, (x - R, y - R + 20), special_flags=pygame.BLEND_RGB_ADD)  # cast down


def _render_furniture(surf, ww):
    """Static street furniture baked into the background: bollards lining both kerbs
    (with gaps at the crossings), a couple of bins and a red post box."""
    cols = ww // _TS
    near_cross = set()
    for c0, c1 in _CROSSINGS:
        near_cross.update(range(c0 - 1, c1 + 2))
    for c in range(0, cols, 2):
        if c in near_cross:
            continue
        for base_y in (6 * _TS - 1, 9 * _TS + 7):          # just inside each kerb
            x = c * _TS + _TS // 2
            pygame.draw.rect(surf, (58, 60, 66), (x - 1, base_y - 7, 3, 8))
            pygame.draw.rect(surf, (190, 180, 70), (x - 1, base_y - 7, 3, 2))   # reflective band
    for c in (14, 47, 88, 134):                            # litter bins on the north pavement
        x = c * _TS + _TS // 2
        pygame.draw.rect(surf, (52, 58, 60), (x - 5, 5 * _TS - 6, 10, 14))
        pygame.draw.rect(surf, (38, 44, 46), (x - 5, 5 * _TS - 6, 10, 3))
    px = 76 * _TS + _TS // 2                               # post box by the Post Office (col 76)
    pygame.draw.rect(surf, (160, 30, 28), (px - 5, 5 * _TS - 12, 11, 20))
    pygame.draw.rect(surf, (120, 20, 20), (px - 5, 5 * _TS - 12, 11, 4))
    pygame.draw.rect(surf, (30, 20, 20), (px - 3, 5 * _TS - 4, 7, 2))


def _render_car(surf, car):
    cx, cy = int(car['x']), car['y']
    col = car['color']
    horiz = pygame.Rect(cx - _CAR_LEN // 2, cy - _CAR_W // 2, _CAR_LEN, _CAR_W)
    pygame.draw.rect(surf, _dk(col, 30), horiz)                       # shadow base
    body = horiz.inflate(-2, -4)
    pygame.draw.rect(surf, col, body)
    pygame.draw.rect(surf, _dk(col, 18), body, 1)
    cabin = pygame.Rect(cx - _CAR_LEN // 6, cy - _CAR_W // 2 + 4, _CAR_LEN // 3, _CAR_W - 8)
    pygame.draw.rect(surf, _CAR_GLASS, cabin)                          # windscreen band
    fx = cx + car['dir'] * (_CAR_LEN // 2 - 3)                         # headlights lead the way
    pygame.draw.rect(surf, (255, 240, 190), (fx - 1, cy - _CAR_W // 2 + 2, 2, 3))
    pygame.draw.rect(surf, (255, 240, 190), (fx - 1, cy + _CAR_W // 2 - 5, 2, 3))


def _render_crossing(surf, c0, c1, walk):
    x0, x1 = c0 * _TS, (c1 + 1) * _TS
    for bx in range(x0 + 3, x1 - 3, 10):                              # zebra stripes across the road
        pygame.draw.rect(surf, _ZEBRA, (bx, _ROAD_ROWS[0] * _TS + 2, 6, 3 * _TS - 4))
    # belisha/pedestrian signal heads on each kerb, red man / green man
    for ky in (_ROAD_ROWS[0] * _TS - 6, (_ROAD_ROWS[2] + 1) * _TS + 6):
        head = pygame.Rect(x0 - 9, ky - 7, 7, 14)
        pygame.draw.rect(surf, (30, 30, 34), head)
        pygame.draw.circle(surf, _LIGHT_RED if not walk else _LIGHT_OFF, (head.centerx, head.y + 4), 2)
        pygame.draw.circle(surf, _LIGHT_GRN if walk else _LIGHT_OFF, (head.centerx, head.y + 10), 2)


class KingSt(Scene):
    lighting = {'vignette': 0.26}     # screen-space vignette over the scrolling view

    def __init__(self):
        super().__init__('king_st')
        self._bg = None
        self._t = 0.0
        self._cars = []
        self._spawn = [1.0, 2.4]          # per-lane spawn countdown
        self._player = None
        self._party = None

    def enter(self, player) -> None:
        self._player = player             # is_walkable lets you finish a crossing once on the road
        self._prime_traffic()             # arrive to a street already in flow, not an empty road

    def set_party(self, party) -> None:
        self._party = party               # so the lights hold green while the crew are crossing

    # ── crossings / traffic lights ──────────────────────────────────────────
    def _crossing_index(self, tx: int):
        for i, (c0, c1) in enumerate(_CROSSINGS):
            if c0 <= tx <= c1:
                return i
        return None

    def _ped_on_crossing(self, i: int) -> bool:
        """Is anyone (player or a follower) still standing on this crossing's road?"""
        c0, c1 = _CROSSINGS[i]
        peds = []
        if self._player is not None:
            peds.append((self._player.tile_x, self._player.tile_y))
        if self._party is not None:
            peds += [(int(f.x // _TS), int(f.y // _TS)) for f in self._party.followers]
        return any(c0 <= x <= c1 and y in _ROAD_ROWS for x, y in peds)

    def _walk_now(self, i: int) -> bool:
        period = _WALK_TIME + _WAIT_TIME
        green = (self._t + i * _CROSS_OFFSET) % period < _WALK_TIME
        return green or self._ped_on_crossing(i)   # never go red while someone's still on it

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        if tile_y in _ROAD_ROWS:                          # the carriageway
            ci = self._crossing_index(tile_x)
            if ci is None:
                return False                              # no jaywalking
            if self._walk_now(ci):
                return True
            # red man: only let a pedestrian already on the road finish crossing off it
            return self._player is not None and self._player.tile_y in _ROAD_ROWS
        return super().is_walkable(tile_x, tile_y)

    # ── cars ────────────────────────────────────────────────────────────────
    def _new_car(self, lane: int, x: float) -> dict:
        y, d = _LANES[lane]
        return {'x': float(x), 'y': y, 'dir': d, 'lane': lane,
                'speed': random.uniform(110, 170), 'color': random.choice(_CAR_COLORS)}

    def _spawn_car(self, lane: int) -> None:
        d = _LANES[lane][1]
        x = -_CAR_LEN if d > 0 else self.world_width + _CAR_LEN
        self._cars.append(self._new_car(lane, x))

    def _prime_traffic(self) -> None:
        """Populate the whole carriageway with spaced, already-moving cars so the
        street reads as live the instant you arrive — then the spawn loop tops it up.
        Cars are kept off any crossing pedestrians currently have the green on."""
        self._cars = []
        self._spawn = [random.uniform(1.8, 4.2), random.uniform(1.8, 4.2)]
        for lane in range(len(_LANES)):
            x = random.uniform(0, 200)            # per-lane phase so the two lanes differ
            while x < self.world_width:
                if self._x_off_crossing(x):
                    self._cars.append(self._new_car(lane, x))
                x += random.uniform(150, 280)     # spacing between cars in the lane

    @staticmethod
    def _x_off_crossing_spans():
        return [(c0 * _TS - _CAR_LEN, (c1 + 1) * _TS + _CAR_LEN) for c0, c1 in _CROSSINGS]

    def _x_off_crossing(self, x: float) -> bool:
        """True if x isn't sitting on a crossing that's currently green for pedestrians
        (so we never prime a car parked in an active zebra)."""
        for i, (lo, hi) in enumerate(self._x_off_crossing_spans()):
            if self._walk_now(i) and lo <= x <= hi:
                return False
        return True

    def _car_stop_x(self, car) -> float:
        """Furthest this car may advance: the stop line of the next green crossing, or
        the back of the car ahead in its lane (whichever it reaches first)."""
        d, x = car['dir'], car['x']
        limit = car['dir'] * 1e9
        for i, (c0, c1) in enumerate(_CROSSINGS):
            if not self._walk_now(i):
                continue
            line = (c0 * _TS - _CAR_LEN / 2 - 2) if d > 0 else ((c1 + 1) * _TS + _CAR_LEN / 2 + 2)
            if (line - x) * d >= 0:                       # at or approaching the stop line -> hold
                limit = min(limit, line) if d > 0 else max(limit, line)
        for o in self._cars:                              # don't rear-end the car ahead
            if o is car or o['lane'] != car['lane']:
                continue
            if (o['x'] - x) * d > 0:
                gap = o['x'] - d * (_CAR_LEN + 6)
                limit = min(limit, gap) if d > 0 else max(limit, gap)
        return limit

    def update(self, dt: float) -> None:
        super().update(dt)
        self._t += dt
        for lane in (0, 1):
            self._spawn[lane] -= dt
            if self._spawn[lane] <= 0:
                self._spawn_car(lane)
                self._spawn[lane] = random.uniform(1.8, 4.2)
        for car in self._cars:
            nx = car['x'] + car['dir'] * car['speed'] * dt
            stop = self._car_stop_x(car)
            car['x'] = min(nx, stop) if car['dir'] > 0 else max(nx, stop)
        self._cars = [c for c in self._cars
                      if -_CAR_LEN * 2 <= c['x'] <= self.world_width + _CAR_LEN * 2]

    def _draw_traffic(self, screen: pygame.Surface) -> None:
        for i, (c0, c1) in enumerate(_CROSSINGS):
            _render_crossing(screen, c0, c1, self._walk_now(i))
        for car in self._cars:
            _render_car(screen, car)

    def _ensure_bg(self):
        if self._bg is not None:
            return
        ww = self.world_width
        self._bg = pygame.Surface((ww, SCREEN_HEIGHT))
        self._bg.fill(_PAVE)

        _render_road(self._bg, ww)
        _render_pavements(self._bg, ww)

        for sr in _SIDE_ROADS:
            _render_side_road(self._bg, *sr)
        for shop in _SHOPS:
            _render_shop(self._bg, *shop)
        for bldg in _BUILDINGS:
            _render_building(self._bg, *bldg)
        _render_furniture(self._bg, ww)
        lamp_pts = [_render_lamp(self._bg, c, by) for c, by in _LAMPS]
        _apply_evening(self._bg, lamp_pts)

    def draw_structures(self, screen: pygame.Surface):
        self._ensure_bg()
        screen.blit(self._bg, (0, 0))
        self._draw_traffic(screen)
