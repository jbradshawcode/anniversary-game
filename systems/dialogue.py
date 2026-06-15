"""Dialogue box — Undertale-style text overlay at the bottom of the screen"""
import pygame
from typing import Callable, List, Optional
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, UI_FONT_NAME,
                    DIALOGUE_CPS, DIALOGUE_FAST)
from systems import portraits

_BG     = (  0,   0,   0)
_BORDER = (255, 255, 255)
_TEXT   = (255, 255, 255)
_SEL    = (255,  50,  50)
_NAME   = (255, 210,  80)

_BORDER_W = 3
_PAD_X    = 24
_PAD_Y    = 18
_LINE_H   = 28
_MARGIN   = 16
_PB       = 92          # portrait box size (when the speaker has a bust)
_BOX_H    = 112
_BOX      = pygame.Rect(_MARGIN, SCREEN_HEIGHT - _BOX_H - _MARGIN,
                         SCREEN_WIDTH - _MARGIN * 2, _BOX_H)

_font = None


def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.SysFont(UI_FONT_NAME, 22)
    return _font


class DialogueBox:
    def __init__(self, sfx=None):
        self._sfx = sfx               # SoundBank for the typewriter blip (optional)
        self.active = False
        self._pages: list = []
        self._index = 0
        self._choosing = False
        self._choice_keys: List[str] = []
        self._choice_branches: dict = {}
        self._choice_index = 0
        self._on_done: Optional[Callable[[], None]] = None
        self._on_choice: Optional[Callable[[str], None]] = None
        self._speaker: Optional[str] = None
        self._full = ""              # current page text, fully
        self._shown = 0.0            # characters revealed so far (typewriter)
        self._typing = False

    @property
    def choosing(self) -> bool:
        return self._choosing

    def start(self, pages: list, on_done: Optional[Callable[[], None]] = None,
              speaker: Optional[str] = None,
              on_choice: Optional[Callable[[str], None]] = None):
        self.active = True
        self._pages = list(pages)
        self._index = 0
        self._on_done = on_done
        self._on_choice = on_choice
        self._speaker = speaker
        self._begin_page()

    def _finish(self):
        self.active = False
        cb = self._on_done
        self._on_done = None
        if cb:
            cb()

    def _begin_page(self):
        if self._index >= len(self._pages):
            self._finish()
            return
        page = self._pages[self._index]
        self._full = page['text'] if isinstance(page, dict) else page
        self._shown = 0.0
        self._typing = len(self._full) > 0
        if isinstance(page, dict):
            self._choosing = True
            self._choice_keys = list(page['choices'].keys())
            self._choice_branches = page['choices']
            self._choice_index = 0
        else:
            self._choosing = False

    def update(self, dt: float):
        if not self.active or not self._typing:
            return
        fast = pygame.key.get_pressed()[pygame.K_x]
        cps = DIALOGUE_CPS * (DIALOGUE_FAST if fast else 1.0)
        prev = int(self._shown)
        self._shown += cps * dt
        if self._shown >= len(self._full):
            self._shown = float(len(self._full))
            self._typing = False
        now = int(self._shown)
        # blip on each fresh (every other, non-space) glyph — but not while fast-forwarding
        if self._sfx is not None and not fast and now > prev and now % 2 == 0:
            if not self._full[now - 1].isspace():
                self._sfx.play('blip')

    def skip(self):
        """Reveal the rest of the current line instantly (X / cancel)."""
        if self._typing:
            self._shown = float(len(self._full))
            self._typing = False

    def advance(self):
        if self._typing:                 # first press finishes the line, doesn't skip it
            self.skip()
            return
        if self._choosing:
            selected = self._choice_keys[self._choice_index]
            follow_up = self._choice_branches[selected]
            self._choosing = False
            if self._on_choice is not None:
                self._on_choice(selected)
            if not follow_up:
                self._finish()
            else:
                self._pages = follow_up
                self._index = 0
                self._begin_page()
        else:
            self._index += 1
            self._begin_page()

    def move_choice(self, delta: int):
        if not self._choosing or self._typing or delta == 0:
            return
        self._choice_index = (self._choice_index + delta) % len(self._choice_keys)

    @staticmethod
    def _wrap_text(font, text: str, max_w: int) -> List[str]:
        lines, cur = [], ""
        for word in text.split(' '):
            trial = word if not cur else cur + ' ' + word
            if font.size(trial)[0] <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return

        pygame.draw.rect(screen, _BG, _BOX)
        pygame.draw.rect(screen, _BORDER, _BOX, _BORDER_W)

        font = _get_font()

        # portrait bust on the left (when the speaker has one); text indents past it
        portrait = portraits.bust(self._speaker) if self._speaker else None
        text_x = _BOX.x + _PAD_X
        if portrait is not None:
            pb = pygame.Rect(_BOX.x + 12, _BOX.y + 10, _PB, _PB)
            pygame.draw.rect(screen, (28, 30, 40), pb)
            screen.blit(portrait, (pb.centerx - portrait.get_width() // 2,
                                   pb.bottom - portrait.get_height()))
            pygame.draw.rect(screen, _BORDER, pb, 2)
            text_x = pb.right + 16

        if self._speaker:
            ns = font.render(self._speaker, True, _NAME)
            tag_x = _BOX.x + (12 if portrait is not None else 18)
            tag = pygame.Rect(tag_x, _BOX.y - 24, ns.get_width() + 24, 26)
            pygame.draw.rect(screen, _BG, tag)
            pygame.draw.rect(screen, _BORDER, tag, _BORDER_W)
            screen.blit(ns, (tag.x + 12, tag.y + 2))
        # wrap to the available width (narrower when a portrait is shown), then run
        # the typewriter over the wrapped lines so long lines can't overflow the box
        max_w = max(60, _BOX.right - 14 - text_x)
        display = []                       # (is_paragraph_start, text)
        for para in self._full.split('\n'):
            wl = self._wrap_text(font, para, max_w) or ['']
            display.extend((j == 0, sub) for j, sub in enumerate(wl))
        revealed, count = int(self._shown), 0
        for i, (start, sub) in enumerate(display):
            if count >= revealed:
                break
            prefix = "* " if start else "   "
            screen.blit(font.render(prefix + sub[:revealed - count], True, _TEXT),
                        (text_x, _BOX.y + _PAD_Y + i * _LINE_H))
            count += len(sub) + 1

        if self._choosing and not self._typing:
            choice_y = _BOX.y + _PAD_Y + len(display) * _LINE_H
            cx = text_x + 16
            for i, key in enumerate(self._choice_keys):
                if i == self._choice_index:
                    screen.blit(font.render(">", True, _SEL), (cx, choice_y))
                surf = font.render(key, True, _TEXT)
                screen.blit(surf, (cx + 16, choice_y))
                cx += 16 + surf.get_width() + 40   # advance past this label (no overlap)
