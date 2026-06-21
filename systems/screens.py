"""Full-screen story interludes: game over, the week-results star card, and the
post-night phone thread. Each is a tiny state object the main loop swaps in for
the overworld; they draw with the shared `menu` toolkit and step on confirm.
"""
import pygame
from typing import List
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME, UI_TITLE_FONT_NAME,
                    END_DEDICATION)
from systems import menu

_STAR_GOLD = (245, 196, 70)
_STAR_DARK = (70, 64, 92)


def draw_the_end(screen: pygame.Surface, loaded: bool = False) -> None:
    """The closing card: shown after the finale, and again when a completed save is
    loaded. CONFIRM starts a fresh playthrough."""
    menu.title_backdrop(screen)
    cx = SCREEN_WIDTH // 2
    if loaded:
        menu.text(screen, "Complete", cx, 140,
                  menu.font(UI_TITLE_FONT_NAME, 46, bold=True), menu.INK, shadow=True)
        menu.text(screen, "This save completed the game.", cx, 214,
                  menu.font(UI_FONT_NAME, 18), menu.INK)
        menu.text(screen, "Would you like to start from the beginning?", cx, 244,
                  menu.font(UI_FONT_NAME, 18), menu.INK)
        menu.text(screen, "Z — start over     X — back", cx, SCREEN_HEIGHT - 56,
                  menu.font(UI_FONT_NAME, 15), menu.MUTED)
    else:
        menu.text(screen, "The End", cx, 150,
                  menu.font(UI_TITLE_FONT_NAME, 50, bold=True), menu.INK, shadow=True)
        fnt = menu.font(UI_FONT_NAME, 18)
        for i, line in enumerate(END_DEDICATION):
            menu.text(screen, line, cx, 232 + i * 30, fnt, menu.INK)
        menu.text(screen, "Z — play again from the beginning", cx, SCREEN_HEIGHT - 56,
                  menu.font(UI_FONT_NAME, 15), menu.MUTED)


def draw_game_over(screen: pygame.Surface, lines: List[str]) -> None:
    screen.fill((10, 8, 14))
    cx = SCREEN_WIDTH // 2
    menu.text(screen, "GAME OVER", cx, 120,
              menu.font(UI_TITLE_FONT_NAME, 52, bold=True), (224, 70, 70), shadow=True)
    fnt = menu.font(UI_FONT_NAME, 18)
    for i, line in enumerate(lines):
        menu.text(screen, line, cx, 210 + i * 30, fnt, menu.INK)
    menu.text(screen, "Z to try again", cx, SCREEN_HEIGHT - 60,
              menu.font(UI_FONT_NAME, 15), menu.MUTED)


def draw_interlude_card(screen: pygame.Surface, kicker: str, name: str,
                        date: str = "") -> None:
    """A between-chapters title card, distinct from the chapter results screen."""
    menu.title_backdrop(screen)
    cx = SCREEN_WIDTH // 2
    menu.text(screen, kicker.upper(), cx, 150,
              menu.font(UI_FONT_NAME, 20), (150, 154, 162))
    menu.text(screen, name, cx, 184,
              menu.font(UI_TITLE_FONT_NAME, 46, bold=True), menu.INK, shadow=True)
    pygame.draw.rect(screen, (150, 154, 162), (cx - 40, 250, 80, 2))
    if date:
        menu.text(screen, date, cx, 268, menu.font(UI_FONT_NAME, 16), (150, 154, 162))
    menu.text(screen, "Z to read", cx, SCREEN_HEIGHT - 56,
              menu.font(UI_FONT_NAME, 15), menu.MUTED)


def draw_chapter_card(screen: pygame.Surface, completed: int, starting: int) -> None:
    """Shown between chapters: marks the one just finished and the one ahead."""
    menu.title_backdrop(screen)
    cx = SCREEN_WIDTH // 2
    menu.text(screen, "CHAPTER {0} COMPLETE".format(completed), cx, 150,
              menu.font(UI_FONT_NAME, 20), (150, 154, 162))
    menu.text(screen, "Chapter {0}".format(starting), cx, 188,
              menu.font(UI_TITLE_FONT_NAME, 46, bold=True), menu.INK, shadow=True)
    pygame.draw.rect(screen, (150, 154, 162), (cx - 40, 252, 80, 2))
    menu.text(screen, "Z to continue", cx, SCREEN_HEIGHT - 56,
              menu.font(UI_FONT_NAME, 15), menu.MUTED)


def _draw_star(screen, cx, cy, r, filled) -> None:
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pygame.draw.polygon(screen, _STAR_GOLD if filled else _STAR_DARK, pts)
    pygame.draw.polygon(screen, (255, 255, 255) if filled else (110, 104, 132),
                        pts, 2)


class Results:
    """The end-of-week star card; stars earned (1-5) from volleyball attempts."""

    def __init__(self, stars: int, attempts: int, title: str = "Week Complete") -> None:
        self.stars = max(1, min(5, stars))
        self.attempts = attempts
        self.title = title

    def draw(self, screen: pygame.Surface) -> None:
        menu.title_backdrop(screen)
        cx = SCREEN_WIDTH // 2
        menu.text(screen, self.title, cx, 70,
                  menu.font(UI_TITLE_FONT_NAME, 40, bold=True), menu.INK, shadow=True)
        gap, r = 78, 30
        x0 = cx - 2 * gap
        for i in range(5):
            _draw_star(screen, x0 + i * gap, 200, r, i < self.stars)
        tries = "1 try" if self.attempts == 1 else "{0} tries".format(self.attempts)
        menu.text(screen, "Volleyball won in {0}".format(tries), cx, 268,
                  menu.font(UI_FONT_NAME, 18), menu.INK)
        menu.text(screen, "Z to continue", cx, SCREEN_HEIGHT - 56,
                  menu.font(UI_FONT_NAME, 15), menu.MUTED)


# ── Phone / text thread ───────────────────────────────────────────────────────
# Message entries (config.PHONE_THREAD) are dicts:
#   {'who': 'James'|'Dan', 'text': str}                          plain bubble
#   {'who': ..., 'react': '👍'|...}  -> attach reaction to prior  (merged in render)
#   {'who': ..., 'shot': [(sender, line), ...], 'caption': str}  screenshot bubble
#   {'who': ..., 'notif': {'app': str, 'title': str, 'body': str}}  notification card
# A trailing 'react' key on any bubble draws a small reaction pill on it.

_PHONE_BG   = (18, 20, 28)
_BUB_ME     = (58, 122, 246)     # right-aligned (James — the "me" side)
_BUB_THEM   = (58, 60, 70)       # left-aligned (Dan)
_BUB_TEXT   = (240, 242, 248)
_SHOT_BG    = (236, 238, 242)
_SHOT_ME    = (52, 199, 89)
_SHOT_THEM  = (228, 230, 234)

# ── Emoji rendering ──────────────────────────────────────────────────────────
# This pygame/SDL build can't render colour emoji (Apple Color Emoji comes back as
# a flat silhouette), so the handful used in the phone thread are drawn as small
# vector icons. Unknown emoji are skipped; add a drawer to _EMOJI_DRAW for more.
_emoji_cache: dict = {}
_EMOJI_SKIP = frozenset([0x200D, 0xFE0F]) | frozenset(range(0x1F3FB, 0x1F400))


def _is_emoji(ch: str) -> bool:
    o = ord(ch)
    return (o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF
            or 0x2300 <= o <= 0x23FF or o in (0x200D, 0xFE0F, 0x203C, 0x2049)
            or 0x1F3FB <= o <= 0x1F3FF)


def _runs(text: str):
    """Split into (is_emoji, substring) runs so emoji draw as icons, text as text."""
    out, buf, cur = [], '', None
    for ch in text:
        e = _is_emoji(ch)
        if cur is None or e == cur:
            buf, cur = buf + ch, e
        else:
            out.append((cur, buf))
            buf, cur = ch, e
    if buf:
        out.append((cur, buf))
    return out


def _epx(fnt) -> int:
    return max(12, fnt.get_height() - 2)


# Each drawer fills an SxS SRCALPHA surface with one emoji icon.
def _e_joy(s, S):
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, (255, 206, 64), (cx, cy), r)
    pygame.draw.circle(s, (230, 170, 40), (cx, cy), r, max(1, S // 18))
    dk, ey = (70, 50, 25), cy - S // 9
    for ex in (cx - S // 5, cx + S // 5):                  # closed laughing eyes (^)
        pygame.draw.lines(s, dk, False,
                          [(ex - S // 9, ey), (ex, ey - S // 11), (ex + S // 9, ey)],
                          max(2, S // 16))
    mouth = pygame.Rect(cx - S // 4, cy + S // 12, S // 2, S // 3)
    pygame.draw.ellipse(s, (110, 45, 35), mouth)           # open smile
    pygame.draw.rect(s, (252, 252, 250), (mouth.x + 2, mouth.y, mouth.w - 4, max(2, S // 12)))
    for tx in (cx - r + S // 10, cx + r - S // 10):        # tears of joy
        pygame.draw.ellipse(s, (120, 200, 240), (tx - S // 14, cy - S // 14, S // 7, S // 4))


def _e_thumb(s, S):
    tan, dk = (244, 198, 150), (200, 155, 110)
    fist = pygame.Rect(S // 4, S // 2 - S // 16, S // 2, S // 2 - S // 12)
    pygame.draw.rect(s, tan, fist, border_radius=max(2, S // 8))
    pygame.draw.rect(s, dk, fist, 1, border_radius=max(2, S // 8))
    thumb = pygame.Rect(S // 4, S // 6, S // 4, S // 2)
    pygame.draw.rect(s, tan, thumb, border_radius=max(2, S // 9))
    pygame.draw.rect(s, dk, thumb, 1, border_radius=max(2, S // 9))


def _e_glove(s, S):
    red, dk = (220, 55, 50), (170, 35, 32)
    body = pygame.Rect(S // 5, S // 6, S * 3 // 5, S * 3 // 5)
    pygame.draw.rect(s, red, body, border_radius=S // 3)             # glove body
    pygame.draw.circle(s, red, (S // 5 + S // 10, S // 2), S // 6)   # thumb bump
    pygame.draw.line(s, dk, (S // 2, S // 5), (S // 2, S // 2), max(1, S // 22))  # knuckle crease
    pygame.draw.rect(s, (236, 230, 224),                            # wrist cuff
                     pygame.Rect(S // 4, S * 5 // 7, S // 2, S // 5), border_radius=S // 12)
    pygame.draw.rect(s, dk, body, 1, border_radius=S // 3)


def _e_no(s, S):
    red = (228, 52, 52)
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, red, (cx, cy), r, max(2, S // 7))
    a = int((r - S // 8) * 0.7)
    pygame.draw.line(s, red, (cx - a, cy - a), (cx + a, cy + a), max(2, S // 7))


def _e_heart(s, S):
    red, dk = (228, 52, 64), (180, 32, 44)
    r = S // 4
    pygame.draw.circle(s, red, (S // 2 - r + 1, S // 2 - r + 2), r)
    pygame.draw.circle(s, red, (S // 2 + r - 1, S // 2 - r + 2), r)
    pygame.draw.polygon(s, red, [(S // 2 - 2 * r + 1, S // 2 - r + 2),
                                 (S // 2 + 2 * r - 1, S // 2 - r + 2),
                                 (S // 2, S - S // 8)])
    pygame.draw.circle(s, dk, (S // 2 - r + 1, S // 2 - r + 2), r, 1)


def _e_cry(s, S):                                          # loud crying (two streams)
    r = S // 2 - 1
    cx = cy = S // 2
    pygame.draw.circle(s, (255, 206, 64), (cx, cy), r)
    pygame.draw.circle(s, (230, 170, 40), (cx, cy), r, max(1, S // 18))
    dk = (70, 50, 25)
    for ex in (cx - S // 5, cx + S // 5):                  # scrunched eyes (^)
        pygame.draw.lines(s, dk, False,
                          [(ex - S // 9, cy - S // 14), (ex, cy - S // 7),
                           (ex + S // 9, cy - S // 14)], max(2, S // 16))
    pygame.draw.ellipse(s, (110, 45, 35),
                        pygame.Rect(cx - S // 6, cy + S // 8, S // 3, S // 5))
    for ex in (cx - S // 4, cx + S // 4):                  # tear streams
        pygame.draw.rect(s, (120, 200, 240),
                         pygame.Rect(ex - S // 16, cy - S // 16, S // 8, S // 2),
                         border_radius=S // 12)


def _e_tear(s, S):                                         # single sad tear
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, (255, 206, 64), (cx, cy), r)
    pygame.draw.circle(s, (230, 170, 40), (cx, cy), r, max(1, S // 20))
    dk = (70, 50, 25)
    for ex in (cx - S // 5, cx + S // 5):                  # eyes
        pygame.draw.circle(s, dk, (ex, cy - S // 12), max(2, S // 12))
    pygame.draw.arc(s, dk, pygame.Rect(cx - S // 5, cy + S // 8, 2 * (S // 5), S // 4),
                    0.4, 2.74, max(2, S // 14))            # frown (top arc)
    blue, bd = (120, 200, 240), (70, 150, 210)            # big teardrop on the cheek
    tx, ty = cx - S // 4, cy + S // 10
    pygame.draw.polygon(s, blue, [(tx, cy - S // 8), (tx - S // 9, ty), (tx + S // 9, ty)])
    pygame.draw.circle(s, blue, (tx, ty), max(2, S // 9))
    pygame.draw.circle(s, bd, (tx, ty), max(2, S // 9), 1)


def _e_pray(s, S):                                         # folded hands (peak shape)
    tan, dk = (244, 198, 150), (200, 155, 110)
    pygame.draw.polygon(s, tan, [(S // 2, S // 6), (S // 2 - S // 4, S * 5 // 6),
                                 (S // 2, S * 3 // 4)])
    pygame.draw.polygon(s, tan, [(S // 2, S // 6), (S // 2 + S // 4, S * 5 // 6),
                                 (S // 2, S * 3 // 4)])
    pygame.draw.line(s, dk, (S // 2, S // 6), (S // 2, S * 3 // 4), max(1, S // 20))


def _e_wave(s, S):                                          # waving hand
    tan, dk = (244, 198, 150), (200, 155, 110)
    palm = pygame.Rect(S // 4, S // 3, S // 2, S // 2)
    pygame.draw.rect(s, tan, palm, border_radius=max(2, S // 8))
    pygame.draw.rect(s, dk, palm, 1, border_radius=max(2, S // 8))
    for i in range(4):                                      # four fingers
        fx = S // 4 + 2 + i * (S // 8)
        pygame.draw.rect(s, tan, (fx, S // 5, max(2, S // 12), S // 4), border_radius=2)
    pygame.draw.rect(s, tan, (S // 6, S * 2 // 5, S // 6, S // 4), border_radius=2)  # thumb


def _e_eyes(s, S):                                          # looking eyes
    for ex in (S // 2 - S // 5, S // 2 + S // 5):
        pygame.draw.ellipse(s, (250, 250, 252), (ex - S // 6, S // 3, S // 3, S // 3))
        pygame.draw.circle(s, (40, 42, 50), (ex, S // 2), max(2, S // 9))


def _e_clock(s, S):                                         # clock face
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, (236, 238, 242), (cx, cy), r)
    pygame.draw.circle(s, (120, 124, 132), (cx, cy), r, max(1, S // 14))
    pygame.draw.line(s, (40, 42, 50), (cx, cy), (cx, cy - r + S // 5), max(2, S // 14))
    pygame.draw.line(s, (40, 42, 50), (cx, cy), (cx + r - S // 4, cy), max(2, S // 16))


def _e_party(s, S):                                         # party popper
    pygame.draw.polygon(s, (240, 180, 60),
                        [(S // 5, S * 4 // 5), (S * 2 // 5, S * 2 // 5), (S * 4 // 5, S * 4 // 5)])
    for cxp, cyp, col in [(S * 3 // 5, S // 4, (228, 52, 64)), (S * 4 // 5, S * 2 // 5, (58, 160, 220)),
                          (S // 2, S // 6, (90, 200, 120)), (S * 7 // 10, S // 2, (245, 196, 70))]:
        pygame.draw.circle(s, col, (cxp, cyp), max(1, S // 12))


def _e_pin(s, S):                                           # round pushpin
    cx = S // 2
    r = S // 4
    pygame.draw.polygon(s, (228, 52, 52),
                        [(cx - r // 2, S // 3 + r // 2), (cx + r // 2, S // 3 + r // 2), (cx, S * 5 // 6)])
    pygame.draw.circle(s, (228, 52, 52), (cx, S // 3), r)
    pygame.draw.circle(s, (255, 150, 150), (cx - r // 3, S // 3 - r // 3), max(1, r // 3))


def _e_money(s, S):                                         # money with wings
    note = pygame.Rect(S // 4, S // 3, S // 2, S // 3)
    pygame.draw.polygon(s, (236, 238, 242), [(S // 4, S * 2 // 5), (S // 12, S // 4), (S // 4, S // 2)])  # wing
    pygame.draw.rect(s, (90, 180, 110), note, border_radius=2)
    pygame.draw.rect(s, (40, 120, 70), note, 1, border_radius=2)
    pygame.draw.circle(s, (40, 120, 70), (S // 2, S // 2), max(2, S // 10), 1)


def _e_zip(s, S):                                           # zipper-mouth face
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, (255, 206, 64), (cx, cy), r)
    pygame.draw.circle(s, (230, 170, 40), (cx, cy), r, max(1, S // 18))
    dk = (70, 50, 25)
    for ex in (cx - S // 5, cx + S // 5):
        pygame.draw.circle(s, dk, (ex, cy - S // 9), max(1, S // 14))
    y = cy + S // 6
    pygame.draw.line(s, (120, 120, 130), (cx - S // 4, y), (cx + S // 4, y), max(2, S // 14))
    for i in range(-2, 3):                                  # zip teeth
        pygame.draw.line(s, (160, 160, 170), (cx + i * S // 12, y - S // 16),
                         (cx + i * S // 12, y + S // 16), 1)


def _e_salute(s, S):                                        # saluting face
    cx = cy = S // 2
    r = S // 2 - 1
    pygame.draw.circle(s, (255, 206, 64), (cx, cy), r)
    pygame.draw.circle(s, (230, 170, 40), (cx, cy), r, max(1, S // 20))
    dk = (70, 50, 25)
    for ex in (cx - S // 6, cx + S // 7):                  # eyes
        pygame.draw.circle(s, dk, (ex, cy + S // 12), max(2, S // 13))
    pygame.draw.arc(s, dk, pygame.Rect(cx - S // 6, cy + S // 5, 2 * (S // 6), S // 6),
                    3.7, 5.7, max(2, S // 18))             # slight smile
    # flat saluting hand: fingertips at the forehead, angled down to the wrist on the right
    tan, td = (245, 206, 160), (200, 160, 115)
    ft = (cx - S // 16, cy - S // 4)         # fingertips at the forehead
    hl = (S - 1, cy + S // 5)                # wrist, lower-right off the face
    dx, dy = hl[0] - ft[0], hl[1] - ft[1]
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    th = S // 5
    nx, ny = -dy / L * th / 2.0, dx / L * th / 2.0
    poly = [(int(ft[0] + nx), int(ft[1] + ny)), (int(hl[0] + nx), int(hl[1] + ny)),
            (int(hl[0] - nx), int(hl[1] - ny)), (int(ft[0] - nx), int(ft[1] - ny))]
    pygame.draw.polygon(s, tan, poly)
    pygame.draw.circle(s, tan, (int(ft[0]), int(ft[1])), int(th / 2))   # rounded fingertips
    pygame.draw.polygon(s, td, poly, 1)


def _e_raise(s, S):                                         # raising hands
    tan = (244, 198, 150)
    for hx in (S // 4, S * 3 // 4):
        palm = pygame.Rect(hx - S // 10, S * 2 // 5, S // 5, S // 3)
        pygame.draw.rect(s, tan, palm, border_radius=2)
        for i in range(3):
            pygame.draw.rect(s, tan, (hx - S // 10 + i * (S // 14), S // 5, max(1, S // 16), S // 4),
                             border_radius=1)


def _e_alarm(s, S):                                         # alarm clock
    cx = cy = S // 2
    r = S // 2 - 4
    dk = (70, 72, 80)
    pygame.draw.circle(s, dk, (cx - r, cy - r + 2), max(2, S // 8))   # bells
    pygame.draw.circle(s, dk, (cx + r, cy - r + 2), max(2, S // 8))
    pygame.draw.line(s, dk, (cx - r // 2, cy + r - 2), (cx - r, cy + r + S // 8), 2)  # legs
    pygame.draw.line(s, dk, (cx + r // 2, cy + r - 2), (cx + r, cy + r + S // 8), 2)
    pygame.draw.circle(s, (228, 70, 60), (cx, cy), r)
    pygame.draw.circle(s, (245, 245, 245), (cx, cy), r - 3)
    pygame.draw.line(s, (40, 42, 50), (cx, cy), (cx, cy - r + S // 5), max(2, S // 16))
    pygame.draw.line(s, (40, 42, 50), (cx, cy), (cx + r - S // 5, cy), max(1, S // 20))


def _e_bangbang(s, S):                                      # double exclamation
    red = (228, 52, 52)
    for ex in (S // 2 - S // 6, S // 2 + S // 6):
        pygame.draw.rect(s, red, (ex - max(1, S // 22), S // 5, max(2, S // 11), S * 2 // 5))
        pygame.draw.circle(s, red, (ex, S * 7 // 10), max(2, S // 12))


def _e_siren(s, S):                                         # rotating red light
    pygame.draw.line(s, (255, 220, 130), (S // 2 - S // 4, S // 5), (S // 2 - S // 3, S // 8), 2)
    pygame.draw.line(s, (255, 220, 130), (S // 2 + S // 4, S // 5), (S // 2 + S // 3, S // 8), 2)
    pygame.draw.rect(s, (80, 82, 90), (S // 4, S * 3 // 5, S // 2, S // 5), border_radius=2)
    pygame.draw.ellipse(s, (228, 52, 52), (S // 3, S // 4, S // 3, S * 2 // 5))
    pygame.draw.ellipse(s, (255, 170, 170), (S // 3 + 2, S // 4 + 2, S // 6, S // 6))


def _e_microbe(s, S):                                       # microbe
    g, gd = (120, 200, 90), (80, 150, 60)
    pygame.draw.circle(s, g, (S // 2, S // 2), S // 2 - 4)
    pygame.draw.circle(s, gd, (S // 2, S // 2), S // 2 - 4, 2)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]:
        pygame.draw.circle(s, gd, (S // 2 + dx * S // 6, S // 2 + dy * S // 6), max(1, S // 11))


def _e_sponge(s, S):                                        # sponge
    r = pygame.Rect(S // 5, S // 4, S * 3 // 5, S // 2)
    pygame.draw.rect(s, (240, 210, 90), r, border_radius=2)
    pygame.draw.rect(s, (200, 170, 60), r, 1, border_radius=2)
    for dx, dy in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]:
        pygame.draw.circle(s, (200, 170, 60),
                           (S // 5 + S // 8 + dx * S // 7, S // 4 + S // 6 + dy * S // 6), max(1, S // 16))


def _e_melt(s, S):                                          # melting face
    y, dk = (255, 206, 64), (70, 50, 25)
    pygame.draw.circle(s, y, (S // 2, S // 2 - S // 12), S // 2 - 4)
    pygame.draw.ellipse(s, y, (S // 6, S // 2, S * 2 // 3, S // 3))    # drip downward
    pygame.draw.ellipse(s, y, (S // 3, S * 5 // 8, S // 4, S // 4))
    for ex in (S // 2 - S // 5, S // 2 + S // 5):
        pygame.draw.circle(s, dk, (ex, S // 2 - S // 10), max(1, S // 14))
    pygame.draw.arc(s, dk, pygame.Rect(S // 2 - S // 5, S // 2 - S // 12, 2 * (S // 5), S // 4),
                    3.6, 5.8, max(1, S // 18))


def _e_skull(s, S):                                         # skull
    w, dk = (238, 238, 235), (40, 42, 48)
    pygame.draw.circle(s, w, (S // 2, S // 2 - S // 12), S // 2 - 4)
    pygame.draw.rect(s, w, (S // 2 - S // 5, S // 2, 2 * (S // 5), S // 4), border_radius=2)
    for ex in (S // 2 - S // 5, S // 2 + S // 5):
        pygame.draw.circle(s, dk, (ex, S // 2 - S // 10), max(2, S // 9))
    pygame.draw.circle(s, dk, (S // 2, S // 2), max(1, S // 16))
    for i in range(-2, 3):
        pygame.draw.line(s, dk, (S // 2 + i * S // 12, S // 2 + S // 8),
                         (S // 2 + i * S // 12, S // 2 + S // 4), 1)


def _e_boom(s, S):                                          # collision / boom
    cx = cy = S // 2
    spikes = [(0, -1, 1.0), (0.35, -0.35, 0.45), (1, 0, 1.0), (0.35, 0.35, 0.45),
              (0, 1, 1.0), (-0.35, 0.35, 0.45), (-1, 0, 1.0), (-0.35, -0.35, 0.45)]
    out = [(cx + int(dx * (S // 2 - 1) * m), cy + int(dy * (S // 2 - 1) * m)) for dx, dy, m in spikes]
    pygame.draw.polygon(s, (245, 150, 40), out)
    inn = [(cx + int(dx * (S // 4) * m), cy + int(dy * (S // 4) * m)) for dx, dy, m in spikes]
    pygame.draw.polygon(s, (250, 220, 90), inn)


def _e_speaker(s, S):                                       # speaker / loud
    dk = (60, 62, 70)
    pygame.draw.rect(s, dk, (S // 5, S * 2 // 5, S // 6, S // 5))
    pygame.draw.polygon(s, dk, [(S // 5 + S // 6, S * 2 // 5), (S * 2 // 5, S // 4),
                                (S * 2 // 5, S * 3 // 4), (S // 5 + S // 6, S * 3 // 5)])
    for r in (S // 6, S // 4):
        pygame.draw.arc(s, (80, 160, 230), pygame.Rect(S // 2 - r // 2, S // 2 - r, r, 2 * r),
                        -1.0, 1.0, 2)


def _e_seenoevil(s, S):                                     # see-no-evil monkey
    br, tan = (150, 100, 60), (212, 172, 124)
    for ex in (S // 4, S * 3 // 4):
        pygame.draw.circle(s, br, (ex, S // 2 - S // 8), max(2, S // 6))   # ears
    pygame.draw.circle(s, br, (S // 2, S // 2), S // 2 - 4)                 # face
    pygame.draw.ellipse(s, tan, (S // 3, S // 2, S // 3, S // 3))          # muzzle
    pygame.draw.rect(s, tan, (S // 5, S // 3, S * 3 // 5, S // 5), border_radius=3)  # hands over eyes


def _e_flag_lb(s, S):                                       # Lebanese flag
    fr = pygame.Rect(S // 6, S // 4, S * 2 // 3, S // 2)
    band = fr.h // 3
    pygame.draw.rect(s, (220, 60, 60), (fr.x, fr.y, fr.w, band))
    pygame.draw.rect(s, (245, 245, 245), (fr.x, fr.y + band, fr.w, band))
    pygame.draw.rect(s, (220, 60, 60), (fr.x, fr.y + 2 * band, fr.w, fr.h - 2 * band))
    cxp, cym = fr.centerx, fr.centery
    pygame.draw.polygon(s, (40, 130, 60), [(cxp, cym - band // 2),
                                           (cxp - fr.w // 8, cym + band // 2),
                                           (cxp + fr.w // 8, cym + band // 2)])
    pygame.draw.rect(s, (40, 130, 60), (cxp - 1, cym + band // 2 - 1, 2, 3))
    pygame.draw.rect(s, (170, 170, 170), fr, 1)


_EMOJI_DRAW = {
    '\U0001F602': _e_joy,    # face with tears of joy
    '\U0001F44D': _e_thumb,  # thumbs up
    '\U0001F94A': _e_glove,  # boxing glove
    '\U0001F6AB': _e_no,     # prohibited / no entry
    '❤': _e_heart,      # red heart
    '\U0001F62D': _e_cry,    # loudly crying face
    '\U0001F622': _e_tear,   # crying face
    '\U0001F64F': _e_pray,   # folded hands
    '\U0001F44B': _e_wave,   # waving hand
    '\U0001F440': _e_eyes,   # eyes
    '\U0001F550': _e_clock,  # clock
    '\U0001F389': _e_party,  # party popper
    '\U0001F4CD': _e_pin,    # round pushpin
    '\U0001F4B8': _e_money,  # money with wings
    '\U0001F910': _e_zip,    # zipper-mouth face
    '\U0001FAE1': _e_salute, # saluting face
    '\U0001F64C': _e_raise,  # raising hands
    '⏰': _e_alarm,      # alarm clock
    '‼': _e_bangbang,   # double exclamation
    '\U0001F6A8': _e_siren,  # police-car light / siren
    '\U0001F9A0': _e_microbe,# microbe
    '\U0001F9FD': _e_sponge, # sponge
    '\U0001FAE0': _e_melt,   # melting face
    '\U0001F480': _e_skull,  # skull
    '\U0001F4A5': _e_boom,   # collision / boom
    '\U0001F50A': _e_speaker,# speaker high volume
    '\U0001F648': _e_seenoevil,  # see-no-evil monkey
    '\U0001F1F1\U0001F1E7': _e_flag_lb,  # Lebanese flag (regional indicators L + B)
}


def _emoji_glyph(ch: str, px: int):
    if ch not in _EMOJI_DRAW:
        return None
    key = (ch, px)
    if key not in _emoji_cache:
        S = 40
        base = pygame.Surface((S, S), pygame.SRCALPHA)
        _EMOJI_DRAW[ch](base, S)
        _emoji_cache[key] = pygame.transform.smoothscale(base, (px, px))
    return _emoji_cache[key]


def _emoji_bases(seg: str):
    chars = [ch for ch in seg if ord(ch) not in _EMOJI_SKIP]
    out, i = [], 0
    while i < len(chars):                         # pair regional indicators into a flag glyph
        if (0x1F1E6 <= ord(chars[i]) <= 0x1F1FF and i + 1 < len(chars)
                and 0x1F1E6 <= ord(chars[i + 1]) <= 0x1F1FF):
            out.append(chars[i] + chars[i + 1])
            i += 2
        else:
            out.append(chars[i])
            i += 1
    return out


def _rich_w(fnt, text: str, epx: int) -> int:
    w = 0
    for e, seg in _runs(text):
        if not e:
            w += fnt.size(seg)[0]
            continue
        for ch in _emoji_bases(seg):
            g = _emoji_glyph(ch, epx)
            w += (g.get_width() + 1) if g is not None else epx
    return w


def _rich_blit(screen, fnt, text: str, x: int, y: int, color, epx: int) -> int:
    cx, lh = x, fnt.get_height()
    for e, seg in _runs(text):
        if not e:
            t = fnt.render(seg, True, color)
            screen.blit(t, (cx, y))
            cx += t.get_width()
            continue
        for ch in _emoji_bases(seg):
            g = _emoji_glyph(ch, epx)
            if g is not None:
                screen.blit(g, (cx, y + (lh - epx) // 2))
                cx += g.get_width() + 1
            else:
                cx += epx
    return cx - x


class Phone:
    """A scrolling iMessage-style thread, revealed one bubble per confirm."""

    def __init__(self, thread: List[dict], me: str = 'James',
                 other: str = None) -> None:
        self._thread = thread
        self._me = me
        self._other = other or ('Dan' if me == 'James' else 'James')
        self.shown = 1
        self._fnt = None
        self._small = None
        self._title = None

    @property
    def done(self) -> bool:
        return self.shown >= len(self._thread)

    def advance(self) -> bool:
        """Reveal the next message; return True if any remained to reveal."""
        if self.shown < len(self._thread):
            self.shown += 1
            return True
        return False

    def _fonts(self):
        if self._fnt is None:
            self._fnt = menu.font(UI_FONT_NAME, 15)
            self._small = menu.font(UI_FONT_NAME, 12)
            self._title = menu.font(UI_FONT_NAME, 16, bold=True)
        return self._fnt, self._small, self._title

    @staticmethod
    def _wrap(fnt, text: str, max_w: int) -> List[str]:
        epx, out, line = _epx(fnt), [], ""
        for word in text.split(' '):
            trial = word if not line else line + ' ' + word
            if _rich_w(fnt, trial, epx) <= max_w or not line:
                line = trial
            else:
                out.append(line)
                line = word
        if line:
            out.append(line)
        return out

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((6, 7, 10))
        fnt, small, title = self._fonts()
        # phone shell
        pw, ph = 360, SCREEN_HEIGHT - 24
        px = (SCREEN_WIDTH - pw) // 2
        py = 12
        shell = pygame.Rect(px, py, pw, ph)
        pygame.draw.rect(screen, _PHONE_BG, shell, border_radius=26)
        pygame.draw.rect(screen, (60, 64, 78), shell, 2, border_radius=26)
        header = pygame.Rect(px, py, pw, 46)
        pygame.draw.rect(screen, (30, 32, 42), header, border_radius=26)
        ts = title.render(self._other, True, _BUB_TEXT)
        screen.blit(ts, (px + pw // 2 - ts.get_width() // 2, py + 14))

        inner_w = pw - 28
        # lay messages bottom-up so the latest sits near the bottom
        msgs = self._thread[:self.shown]
        blocks = [self._measure(m, fnt, small, inner_w) for m in msgs]
        total_h = sum(h for _, h in blocks) + 12 * len(blocks)
        y = py + ph - 20 - total_h           # bottom-anchored: newest stays in view,
                                             # older messages scroll up under the header
        old = screen.get_clip()
        screen.set_clip(pygame.Rect(px, py + 48, pw, ph - 48))
        for m, (render, h) in zip(msgs, blocks):
            render(screen, px + 14, y, inner_w)
            y += h + 12
        screen.set_clip(old)

        menu.text(screen, "Z to continue", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 6,
                  small, menu.MUTED)

    # Each _measure returns (render_fn(screen, x, y, w), height).
    def _measure(self, m: dict, fnt, small, w):
        if 'sep' in m:                       # a centered date pill
            return self._measure_sep(m, small, w)
        mine = m['who'] == self._me
        if 'shot' in m:
            return self._measure_shot(m, fnt, small, w, mine)
        if 'notif' in m:
            return self._measure_notif(m, small, w, mine)
        return self._measure_text(m, fnt, small, w, mine)

    def _measure_sep(self, m, small, w):
        label = m['sep']
        ts = small.render(label, True, (150, 154, 162))
        bw = ts.get_width() + 18

        def render(screen, x, y, ww):
            bx = x + (ww - bw) // 2
            pygame.draw.rect(screen, (40, 42, 52), (bx, y, bw, 20), border_radius=10)
            screen.blit(ts, (bx + 9, y + 4))
        return render, 20

    def _measure_text(self, m, fnt, small, w, mine):
        epx = _epx(fnt)
        # pre-formatted messages (with their own line breaks, e.g. the emoji meme)
        # get the full bubble width so each crafted line stays on one line, and are
        # centred within the bubble (matching how they were composed)
        preformatted = '\n' in m['text']
        cap = w - 24 if preformatted else int(w * 0.66)
        lines = []                               # honour explicit \n (paragraph breaks)
        for seg in m['text'].split('\n'):
            lines.extend(self._wrap(fnt, seg, cap) if seg else [''])
        bw = max(_rich_w(fnt, ln, epx) for ln in lines) + 22
        bh = len(lines) * 20 + 14
        react = m.get('react')

        def render(screen, x, y, ww):
            bx = x + ww - bw if mine else x
            rect = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, _BUB_ME if mine else _BUB_THEM, rect,
                             border_radius=14)
            for i, ln in enumerate(lines):
                lx = bx + (bw - _rich_w(fnt, ln, epx)) // 2 if preformatted else bx + 11
                _rich_blit(screen, fnt, ln, lx, y + 7 + i * 20, _BUB_TEXT, epx)
            if react:
                self._reaction(screen, rect, react, mine, small)
        return render, bh + (10 if react else 0)

    def _measure_notif(self, m, small, w, mine):
        n = m['notif']
        body_lines = self._wrap(small, n['body'], int(w * 0.74))
        bw = int(w * 0.82)
        bh = 30 + len(body_lines) * 16 + 12

        def render(screen, x, y, ww):
            bx = x + (ww - bw) // 2
            rect = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, (244, 246, 250), rect, border_radius=14)
            pygame.draw.rect(screen, (210, 214, 222), rect, 1, border_radius=14)
            screen.blit(small.render(n['app'], True, (120, 124, 132)), (bx + 12, y + 7))
            screen.blit(menu.font(UI_FONT_NAME, 13, bold=True).render(
                n['title'], True, (20, 22, 28)), (bx + 12, y + 22))
            for i, ln in enumerate(body_lines):
                screen.blit(small.render(ln, True, (60, 64, 72)),
                            (bx + 12, y + 40 + i * 16))
        return render, bh

    def _measure_shot(self, m, fnt, small, w, mine):
        shot = m['shot']
        caption = m.get('caption')
        me_side = m.get('shot_me', 'James')
        epx = _epx(small)
        bw = int(w * 0.8)
        inner = bw - 20
        name_h = small.get_height() - 1
        rows, prev = [], None
        for sender, line in shot:
            wl = self._wrap(small, line, int(inner * 0.7))
            named = sender != me_side and sender != prev   # label each 'them' group
            rows.append((sender, wl, named))
            prev = sender
        rh = sum(len(wl) * 15 + 12 + (name_h if nm else 0) for _, wl, nm in rows) + 16
        cap_h = 18 if caption else 0
        bh = rh + cap_h

        def render(screen, x, y, ww):
            bx = x + ww - bw if mine else x
            outer = pygame.Rect(bx, y, bw, bh)
            pygame.draw.rect(screen, _SHOT_BG, outer, border_radius=12)
            pygame.draw.rect(screen, (200, 204, 210), outer, 1, border_radius=12)
            cy = y + 8
            for sender, wl, named in rows:
                smine = sender == me_side
                if named:                                  # sender name above the bubble
                    screen.blit(small.render(sender, True, (120, 124, 132)),
                                (bx + 12, cy))
                    cy += name_h
                tw = max(_rich_w(small, ln, epx) for ln in wl) + 14
                th = len(wl) * 15 + 8
                sx = bx + bw - 10 - tw if smine else bx + 10
                pygame.draw.rect(screen, _SHOT_ME if smine else _SHOT_THEM,
                                 pygame.Rect(sx, cy, tw, th), border_radius=9)
                tc = (255, 255, 255) if smine else (28, 30, 36)
                for i, ln in enumerate(wl):
                    _rich_blit(screen, small, ln, sx + 7, cy + 4 + i * 15, tc, epx)
                cy += th + 12
            if caption:
                screen.blit(small.render(caption, True, (120, 124, 132)),
                            (bx + 8, y + bh - 16))
        return render, bh

    @staticmethod
    def _reaction(screen, rect, react, mine, small):
        # WhatsApp puts the reaction badge at the bubble's bottom-right corner — always,
        # whoever sent the message (mine is kept for signature compatibility, unused).
        epx = _epx(small)
        pw2 = _rich_w(small, react, epx) + 12
        bx = rect.right - pw2 + 8
        pr = pygame.Rect(bx, rect.bottom - 9, pw2, 18)
        pygame.draw.rect(screen, (40, 42, 52), pr, border_radius=9)
        _rich_blit(screen, small, react, bx + 6, rect.bottom - 7, (250, 250, 250), epx)
