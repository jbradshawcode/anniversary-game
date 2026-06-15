"""Menus + the title-screen look. A small themed UI toolkit on top of pygame.draw.

`Menu` holds option/selection state; the module-level helpers (gradient, hero,
options, text) do the drawing so the title screen and the in-game pause/slot
menus share one visual language.
"""
import math
import pygame
from typing import Dict, List, Tuple
from config import UI_FONT_NAME, UI_TITLE_FONT_NAME

# Theme — dusk indigo→plum with a warm amber accent.
BG_TOP   = (24, 26, 51)
BG_BOT   = (46, 26, 49)
INK      = (236, 233, 244)
MUTED    = (151, 150, 172)
ACCENT   = (244, 179,  80)
SEL_TEXT = ( 30,  24,  14)
SHADOW   = (  0,   0,   0)

_fonts: Dict[Tuple[str, int, bool], pygame.font.Font] = {}
_grad: Dict[Tuple[int, int], pygame.Surface] = {}


def font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


def text(screen: pygame.Surface, s: str, cx: int, y: int, fnt: pygame.font.Font,
         color, shadow: bool = False) -> None:
    if shadow:
        sh = fnt.render(s, True, SHADOW)
        screen.blit(sh, (cx - sh.get_width() // 2 + 2, y + 2))
    surf = fnt.render(s, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, y))


def gradient(screen: pygame.Surface) -> None:
    size = screen.get_size()
    surf = _grad.get(size)
    if surf is None:
        w, h = size
        surf = pygame.Surface(size)
        for y in range(h):
            t = y / max(1, h - 1)
            surf.fill((int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
                       int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
                       int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)),
                      (0, y, w, 1))
        _grad[size] = surf
    screen.blit(surf, (0, 0))


def _ball(screen: pygame.Surface, cx: int, cy: int, r: int, alpha: int) -> None:
    """A faint volleyball watermark — circle plus three curved seams."""
    s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    c = (r + 2, r + 2)
    pygame.draw.circle(s, (255, 255, 255, alpha), c, r)
    pygame.draw.circle(s, (255, 255, 255, min(255, alpha + 40)), c, r, 2)
    seam = (255, 255, 255, min(255, alpha + 30))
    for base, bow in ((-0.48, 0.42), (0.0, -0.42), (0.48, 0.42)):
        pts = []
        for j in range(17):
            v = j / 16.0                       # 0 (top) .. 1 (bottom)
            x = base * r * 0.82 + bow * r * math.sin(math.pi * v)
            y = (v * 2 - 1) * r * 0.92
            pts.append((c[0] + int(x), c[1] + int(y)))
        pygame.draw.lines(s, seam, False, pts, 2)
    screen.blit(s, (cx - r - 2, cy - r - 2))


def title_backdrop(screen: pygame.Surface) -> None:
    gradient(screen)
    w = screen.get_width()
    _ball(screen, w - 70, 70, 96, 16)        # large faint ball, top-right
    _ball(screen, 60, screen.get_height() - 40, 60, 12)  # small one, lower-left


def hero(screen: pygame.Surface, title: str, subtitle: str = "") -> None:
    cx = screen.get_width() // 2
    text(screen, title, cx, 92, font(UI_TITLE_FONT_NAME, 50, bold=True), INK, shadow=True)
    pygame.draw.line(screen, ACCENT, (cx - 130, 162), (cx + 130, 162), 3)
    if subtitle:
        text(screen, subtitle, cx, 174, font(UI_FONT_NAME, 16), MUTED)


def options(screen: pygame.Surface, opts: List[str], index: int,
            start_y: int, gap: int = 46, size: int = 24) -> None:
    cx = screen.get_width() // 2
    fnt = font(UI_FONT_NAME, size)
    for i, opt in enumerate(opts):
        y = start_y + i * gap
        selected = i == index
        surf = fnt.render(opt, True, SEL_TEXT if selected else INK)
        if selected:
            bar = pygame.Rect(0, 0, surf.get_width() + 52, size + 18)
            bar.center = (cx, y + surf.get_height() // 2)
            pygame.draw.rect(screen, ACCENT, bar, border_radius=bar.height // 2)
        screen.blit(surf, (cx - surf.get_width() // 2, y))


class Menu:
    def __init__(self, title: str, opts: List[str], hint: str = "") -> None:
        self.title = title
        self.options = list(opts)
        self.hint = hint
        self.index = 0

    def move(self, delta: int) -> None:
        if self.options:
            self.index = (self.index + delta) % len(self.options)

    def draw(self, screen: pygame.Surface, dim: bool = False) -> None:
        if dim:
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((12, 12, 22, 165))
            screen.blit(overlay, (0, 0))
        cx = screen.get_width() // 2
        text(screen, self.title, cx, 84, font(UI_TITLE_FONT_NAME, 38, bold=True),
             INK, shadow=True)
        options(screen, self.options, self.index, 188)
        if self.hint:
            text(screen, self.hint, cx, screen.get_height() - 34,
                 font(UI_FONT_NAME, 14), MUTED)
