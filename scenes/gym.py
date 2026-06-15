"""Scene 1 — Latymer Upper School sports hall (Latymer Sports Centre, King St).

Set up for VOLLEYBALL (Londinium VC / GO Mammoth play here): two courts split by
the hall's retractable central divider CURTAIN, each with a net up. The nets and
the curtain are impassable — they block the edge between tiles (you can stand
right beside them, but not walk through), and leave gaps so you can pass around.
Blue coated sprung floor with the real multi-sport lines (orange badminton,
yellow netball), pale-timber clad walls, fold-out hoops.
"""
import pygame
from .base import Scene
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

_TS = TILE_SIZE

# ── Palette ──────────────────────────────────────────────────────────────────
_CLAD        = (202, 182, 142)
_CLAD_DK     = (184, 163, 122)
_FLOOR       = (66, 130, 180)
_FLOOR_SHEEN = (78, 143, 192)
_VB          = (248, 248, 248)
_ORANGE      = (228, 128, 52)
_YELLOW      = (232, 198, 72)
_NET_FILL    = (230, 232, 236)      # white volleyball net
_NET_MESH    = (198, 202, 208)
_NET_TAPE    = (250, 250, 250)
_POLE        = (180, 180, 190)
_ANT_R       = (212, 64, 52)
_ANT_W       = (240, 240, 240)
_CURT        = (44, 92, 172)         # central divider — blue roller curtain (per fb_06)
_CURT_DK     = (32, 68, 132)
_CURT_LT     = (78, 130, 206)
_RAIL        = (120, 124, 132)
_CURT_SH     = (40, 74, 124)         # curtain shadow on the blue floor
_CORR        = (180, 174, 164)       # lit corridor seen THROUGH the open doorway
_CORR_DK     = (66, 62, 56)          # recessed jamb / head shadow (depth)
_DOOR_PLY    = (196, 176, 136)       # flush plywood door leaf — reads as the wall
_DOOR_RV     = (150, 128, 92)        # thin reveal/frame line of a flush door
_GLASS_PN    = (58, 70, 78)          # door vision-panel glazing
_EXIT_GRN    = (46, 158, 74)         # green running-man exit sign
_EXIT_LT     = (210, 238, 215)       # exit-sign pictogram highlight
_HOOP_OR     = (230, 120, 40)
_BACKBOARD   = (240, 240, 238)
_BB_DK       = (200, 200, 198)

# ── Layout (tile-aligned so net/curtain sit on tile boundaries) ──────────────
_HALL   = pygame.Rect(24, 24, SCREEN_WIDTH - 48, SCREEN_HEIGHT - 48)
_LEFT   = pygame.Rect(2 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)   # cols 2-8, rows 3-12
_RIGHT  = pygame.Rect(11 * _TS, 3 * _TS, 7 * _TS, 10 * _TS)  # cols 11-17
_NET_Y  = 8 * _TS                                            # row 7/8 boundary (court centre)
_CURT_X = 10 * _TS                                           # col 9/10 boundary (hall centre)

_NETB = pygame.Rect(54, 86, 532, 308)                        # netball court (background)
_BAD_W, _BAD_H = 250, 142
_BADMINTON = [pygame.Rect(x, y, _BAD_W, _BAD_H)
              for y in (54, 256) for x in (44, 330)]


def _build_walls() -> frozenset:
    w = set()
    for c in list(range(2, 9)) + list(range(11, 18)):        # nets: no vertical crossing at row 7/8
        w |= {((c, 7), (c, 8)), ((c, 8), (c, 7))}
    for r in range(2, 13):                                   # curtain: no horizontal crossing col 9/10
        w |= {((9, r), (10, r)), ((10, r), (9, r))}           # (rows 1 & 13 left open to pass around)
    return frozenset(w)


# ── Walls / floor ────────────────────────────────────────────────────────────

def _draw_walls(surf):
    surf.fill(_CLAD)
    for x in range(0, SCREEN_WIDTH, 9):
        pygame.draw.line(surf, _CLAD_DK, (x, 0), (x, SCREEN_HEIGHT), 1)


def _draw_floor(surf):
    pygame.draw.rect(surf, _FLOOR, _HALL)
    for i in range(0, _HALL.height, 14):
        if (i // 14) % 3 == 0:
            pygame.draw.rect(surf, _FLOOR_SHEEN, (_HALL.x, _HALL.y + i, _HALL.width, 5))


# ── Background multi-sport lines (thin) ──────────────────────────────────────

def _draw_badminton(surf):
    for c in _BADMINTON:
        pygame.draw.rect(surf, _ORANGE, c, 1)
        cx = c.centerx
        for sx in (cx - 26, cx + 26):
            pygame.draw.line(surf, _ORANGE, (sx, c.top), (sx, c.bottom), 1)
        pygame.draw.line(surf, _ORANGE, (c.left, c.centery), (c.right, c.centery), 1)
        for sy in (c.top + 12, c.bottom - 12):
            pygame.draw.line(surf, _ORANGE, (c.left, sy), (c.right, sy), 1)


def _draw_netball(surf):
    c = _NETB
    pygame.draw.rect(surf, _YELLOW, c, 1)
    third = c.width // 3
    for tx in (c.left + third, c.left + 2 * third):
        pygame.draw.line(surf, _YELLOW, (tx, c.top), (tx, c.bottom), 1)
    r = 84
    pygame.draw.arc(surf, _YELLOW, (c.left - r, c.centery - r, 2 * r, 2 * r), -1.4, 1.4, 1)
    pygame.draw.arc(surf, _YELLOW, (c.right - r, c.centery - r, 2 * r, 2 * r), 1.74, 4.54, 1)


# ── Volleyball courts (white, the focus) ─────────────────────────────────────

def _draw_volleyball_court(surf, court: pygame.Rect):
    pygame.draw.rect(surf, _VB, court, 3)
    for ay in (_NET_Y - 2 * _TS, _NET_Y + 2 * _TS):          # attack lines
        pygame.draw.line(surf, _VB, (court.left, ay), (court.right, ay), 2)


# ── Central divider curtain (sprite + impassable edge) ───────────────────────

def _draw_curtain(surf):
    x = _CURT_X
    y0, y1 = 2 * _TS, 13 * _TS
    pygame.draw.rect(surf, _CURT_SH, (x - 8, y0 + 2, 16, y1 - y0))   # floor shadow
    pygame.draw.rect(surf, _CURT, (x - 5, y0, 10, y1 - y0))          # fabric
    for px, col in ((x - 4, _CURT_DK), (x - 1, _CURT_LT), (x + 2, _CURT_DK)):
        pygame.draw.line(surf, col, (px, y0), (px, y1), 1)          # pleats
    pygame.draw.rect(surf, _RAIL, (x - 7, y0 - 3, 14, 4))           # ceiling track


# ── Volleyball nets (sprite + impassable edge) ───────────────────────────────

def _draw_net(surf, court: pygame.Rect):
    ny = _NET_Y
    for px in (court.left - 2, court.right + 2):                    # posts
        pygame.draw.rect(surf, _POLE, (px - 2, ny - 22, 4, 44))
    band = pygame.Rect(court.left, ny - 6, court.width, 12)
    pygame.draw.rect(surf, _NET_FILL, band)
    old = surf.get_clip()
    surf.set_clip(band)
    for x in range(court.left, court.right + 1, 6):
        pygame.draw.line(surf, _NET_MESH, (x, band.top), (x, band.bottom), 1)
    surf.set_clip(old)
    pygame.draw.line(surf, _NET_TAPE, (court.left, band.top), (court.right, band.top), 2)
    pygame.draw.line(surf, _NET_TAPE, (court.left, band.bottom), (court.right, band.bottom), 2)
    for ax in (court.left, court.right):                           # antennae
        pygame.draw.rect(surf, _ANT_W, (ax - 1, ny - 16, 3, 32))
        pygame.draw.rect(surf, _ANT_R, (ax - 1, ny - 16, 3, 8))
        pygame.draw.rect(surf, _ANT_R, (ax - 1, ny + 8, 3, 8))


# ── Basketball hoops ─────────────────────────────────────────────────────────

def _draw_hoops(surf):
    by = _HALL.centery
    bl = _HALL.x - 2
    pygame.draw.rect(surf, _BACKBOARD, (bl - 8, by - 16, 10, 32))
    pygame.draw.rect(surf, _BB_DK, (bl - 8, by - 16, 10, 32), 1)
    pygame.draw.circle(surf, _HOOP_OR, (bl + 8, by), 8, 2)
    br = _HALL.right + 2
    pygame.draw.rect(surf, _BACKBOARD, (br - 2, by - 16, 10, 32))
    pygame.draw.rect(surf, _BB_DK, (br - 2, by - 16, 10, 32), 1)
    pygame.draw.circle(surf, _HOOP_OR, (br - 8, by), 8, 2)


# ── Doors ────────────────────────────────────────────────────────────────────

def _draw_entrance(surf):
    # top-wall entrance (cols 8-11): the flush ply double doors stand OPEN, so you see
    # THROUGH to the lit corridor beyond — open leaves (each with a vision-panel slot)
    # framing a bright opening, jamb reveals for depth, a green exit sign on the lintel.
    # Ref: gym_refs/doors/hall_entrance_doors_ZOOM.jpg (open doorways, light through).
    cx = SCREEN_WIDTH // 2
    half = 2 * _TS                       # opening spans cols 8-11
    x0, x1 = cx - half, cx + half
    bot = _HALL.y + 2                    # depth of the top wall strip
    top = 7                              # tan lintel above the opening (holds the sign)
    pygame.draw.rect(surf, _CORR, (x0, top, x1 - x0, bot - top))    # lit corridor seen through
    pygame.draw.rect(surf, _CORR_DK, (x0, top, x1 - x0, 4))         # recess shadow at the head (depth)
    lw = 12
    for lx in (x0 + 2, x1 - 2 - lw):                               # the two open leaves, folded back
        pygame.draw.rect(surf, _DOOR_PLY, (lx, top, lw, bot - top))
        pygame.draw.rect(surf, _DOOR_RV, (lx, top, lw, bot - top), 1)
        pygame.draw.rect(surf, _GLASS_PN, (lx + lw // 2 - 1, top + 3, 2, bot - top - 7))  # vision panel
    for jx in (x0 - 1, x1 - 1):                                    # jamb reveals (door frame)
        pygame.draw.rect(surf, _DOOR_RV, (jx, top - 1, 2, bot - top + 1))
    sw, sh = 14, 5                                                 # green exit sign on the lintel
    sx = cx - sw // 2
    pygame.draw.rect(surf, _EXIT_GRN, (sx, 1, sw, sh))
    pygame.draw.rect(surf, _EXIT_LT, (sx + sw - 4, 2, 2, sh - 2))  # pictogram hint
    pygame.draw.rect(surf, (20, 80, 40), (sx, 1, sw, sh), 1)

    # left-wall flush ply door (matches the wall; plan confirms a door here)
    sdx, sdy, sdh = _HALL.x - 1, 10 * _TS + 2, 2 * _TS - 4
    pygame.draw.rect(surf, _DOOR_PLY, (sdx, sdy, 4, sdh))
    pygame.draw.rect(surf, _DOOR_RV, (sdx, sdy, 4, sdh), 1)


# ── Scene ────────────────────────────────────────────────────────────────────

class Gym(Scene):
    walls = _build_walls()
    # cool overhead light pools + a soft vignette for depth (see systems.lighting)
    lighting = {
        'vignette': 0.30,
        'pools': [(x, y, 90, (225, 235, 255), 0.22)
                  for y in (90, 250) for x in (160, 320, 480)],
    }

    def __init__(self):
        super().__init__('gym')

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0))
        _draw_walls(screen)
        _draw_floor(screen)
        _draw_badminton(screen)
        _draw_netball(screen)
        _draw_volleyball_court(screen, _LEFT)
        _draw_volleyball_court(screen, _RIGHT)
        _draw_hoops(screen)
        _draw_entrance(screen)
        _draw_curtain(screen)
        _draw_net(screen, _LEFT)
        _draw_net(screen, _RIGHT)
        self._draw_objects(screen)
